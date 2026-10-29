"""Capture -> mask -> extract -> validate -> flag -> save as DRAFT tasks for a human to confirm."""
from ..extensions import db
from ..models import DRAFT, Client, Holiday, SourceMessage, Task, User
from ..utils import log_activity, today_sg
from .dates import date_warnings
from .duplicates import find_duplicates
from .extraction import extract_tasks
from .priority import refresh_priorities


def _match_client(name: str | None) -> Client | None:
    if not name:
        return None
    for c in Client.query.all():
        if name.lower() in c.name.lower() or c.name.split()[0].lower() in name.lower():
            return c
    return None


def process_message(message: SourceMessage, user_id: int | None = None) -> list[Task]:
    clients = [c.name for c in Client.query.all()]
    sent_on = (message.sent_at.date() if message.sent_at else today_sg())
    result = extract_tasks(message.body, sent_on, clients)  # may raise ExtractionError
    holidays = {h.date: h.name for h in Holiday.query.all()}
    users = User.query.all()

    created = []
    for et in result.tasks:
        client = _match_client(et.client)
        flags = list(et.flags) + date_warnings(et.due_date, holidays)
        dups = find_duplicates(et.title, client.id if client else None)
        if dups:
            flags.append(f"Possible duplicate of task #{dups[0].id}")
        owner = next((u for u in users if et.owner and u.name.lower().startswith(et.owner.lower())), None)
        task = Task(message_id=message.id, client_id=client.id if client else None,
                    owner_id=owner.id if owner else None, owner_name=et.owner,
                    title=et.title, due_date=et.due_date, due_date_text=et.due_date_text,
                    due_reason=et.due_reason, source_quote=et.source_quote,
                    confidence=et.confidence, needs_confirmation=et.needs_confirmation,
                    status=DRAFT)
        task.set_flags(flags)
        db.session.add(task)
        created.append(task)
    message.processed = True
    db.session.flush()
    log_activity("message.extracted", "message", message.id, f"{len(created)} draft task(s)", user_id=user_id)
    db.session.commit()
    refresh_priorities(today_sg())
    return created
