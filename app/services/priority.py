"""Rule-based priority with a plain-English reason."""
from datetime import date

from ..extensions import db
from ..models import DONE, BLOCKED, WAITING, Task


def score_task(task: Task, today: date) -> tuple[int, str]:
    reasons: list[str] = []
    if task.due_date is None:
        score, reasons = 20, ["No confirmed due date"]
    else:
        days = (task.due_date - today).days
        if days < 0:
            score, reasons = 100, [f"Overdue by {-days} day(s)"]
        elif days <= 2:
            score, reasons = 80, [f"Due in {days} day(s)"]
        elif days <= 7:
            score, reasons = 60, [f"Due in {days} days"]
        else:
            score, reasons = 30, [f"Due in {days} days"]
    if task.status == BLOCKED:
        score += 10
        reasons.append("blocked")
    if task.status == WAITING and not task.reply_received:
        score -= 10
        reasons.append("waiting on a reply")
    if task.needs_confirmation:
        reasons.append("details need confirmation")
    return max(score, 0), "; ".join(reasons)


def refresh_priorities(today: date) -> None:
    for t in Task.query.filter(Task.status != DONE).all():
        t.priority_score, t.priority_reason = score_task(t, today)
    db.session.commit()
