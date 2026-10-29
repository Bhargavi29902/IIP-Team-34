"""Approval Queue logic. AI proposes, a human decides, every step leaves evidence."""
import hashlib
import json

from ..extensions import db
from ..models import EXECUTED, FAILED, OPEN, PENDING, REJECTED, WAITING, Approval, Task, utcnow
from ..utils import log_activity
from .integrations import run_action


def make_key(kind: str, task_id: int, payload: dict) -> str:
    raw = f"{kind}:{task_id}:{json.dumps(payload, sort_keys=True)}"
    return hashlib.sha256(raw.encode()).hexdigest()


def queue_action(task: Task, kind: str, payload: dict, user_id: int | None,
                 ai_generated: bool = False) -> tuple[Approval, bool]:
    """Create a pending approval. The idempotency key means the same action is never queued twice."""
    key = make_key(kind, task.id, payload)
    existing = Approval.query.filter_by(idempotency_key=key).first()
    if existing:
        return existing, False
    a = Approval(task_id=task.id, kind=kind, idempotency_key=key, requested_by=user_id,
                 ai_generated=ai_generated)
    a.set_data(payload)
    db.session.add(a)
    db.session.flush()
    log_activity("approval.queued", "approval", a.id, f"{kind} for task {task.id}", user_id=user_id)
    db.session.commit()
    return a, True


def approve(approval: Approval, user_id: int, edits: dict | None = None) -> Approval:
    if approval.status == EXECUTED:  # a retry/double click must never act twice
        return approval
    if approval.status not in (PENDING, FAILED):
        raise ValueError(f"Approval is {approval.status} and cannot be approved.")
    if edits:
        approval.set_data({**approval.data, **edits})
    approval.decided_by, approval.decided_at = user_id, utcnow()
    try:
        result = run_action(approval.kind, approval.data)
    except Exception as exc:
        approval.status = FAILED
        approval.result_message = f"Failed: {exc}. Draft kept; you can retry."
        log_activity("approval.failed", "approval", approval.id, str(exc), user_id=user_id)
        db.session.commit()
        return approval

    approval.status, approval.external_id = EXECUTED, result["id"]
    approval.simulated = bool(result.get("simulated"))
    verb = "Calendar event created" if approval.kind == "calendar" else "Email sent"
    approval.result_message = verb + (" (SIMULATED - nothing left this app)" if approval.simulated else "")
    task = approval.task
    if approval.kind == "calendar":
        task.calendar_event_id = approval.external_id
    elif task.status == OPEN:
        task.status = WAITING
    log_activity("approval.executed", "approval", approval.id, approval.result_message, user_id=user_id)
    db.session.commit()
    return approval


def reject(approval: Approval, user_id: int) -> Approval:
    if approval.status in (EXECUTED, REJECTED):
        return approval
    approval.status, approval.decided_by, approval.decided_at = REJECTED, user_id, utcnow()
    log_activity("approval.rejected", "approval", approval.id, user_id=user_id)
    db.session.commit()
    return approval
