from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import ActivityLog, Client, DONE, DRAFT, OPEN, Task, User
from ..services.approvals import queue_action
from ..services.priority import refresh_priorities
from ..utils import log_activity, today_sg

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@bp.route("/")
@login_required
def list_tasks():
    q = Task.query
    if s := request.args.get("q", "").strip():
        q = q.filter(Task.title.ilike(f"%{s}%"))
    if st := request.args.get("status"):
        q = q.filter(Task.status == st)
    if cid := request.args.get("client", type=int):
        q = q.filter(Task.client_id == cid)
    refresh_priorities(today_sg())
    return render_template("tasks/list.html", tasks=q.order_by(Task.priority_score.desc()).all(),
                           clients=Client.query.order_by(Client.name).all(), args=request.args)


@bp.route("/<int:task_id>")
@login_required
def detail(task_id):
    task = db.get_or_404(Task, task_id)
    logs = ActivityLog.query.filter_by(entity_type="task", entity_id=task.id).order_by(ActivityLog.id.desc()).all()
    return render_template("tasks/detail.html", task=task, logs=logs,
                           clients=Client.query.order_by(Client.name).all(),
                           users=User.query.order_by(User.name).all())


@bp.post("/<int:task_id>/confirm")
@login_required
def confirm(task_id):
    task = db.get_or_404(Task, task_id)
    f = request.form
    title = f.get("title", "").strip()
    if not title:
        flash("A task needs a title.", "danger")
        return redirect(request.referrer or url_for("tasks.detail", task_id=task.id))
    due_raw = f.get("due_date", "").strip()
    if not due_raw and not f.get("no_due_date"):
        flash("Pick a due date, or tick 'No due date'. The AI never guesses one for you.", "warning")
        return redirect(request.referrer or url_for("tasks.detail", task_id=task.id))
    try:
        due = datetime.strptime(due_raw, "%Y-%m-%d").date() if due_raw else None
    except ValueError:
        flash("That due date isn't valid.", "danger")
        return redirect(request.referrer or url_for("tasks.detail", task_id=task.id))

    owner_id = f.get("owner_id", type=int)
    owner = db.session.get(User, owner_id) if owner_id else None
    new_client = f.get("client_id", type=int) or None
    changes = []  # corrections feed 'learns from corrections' + the Reports correction rate
    for field, old, new in (("title", task.title, title), ("due_date", task.due_date, due),
                            ("owner", task.owner_name, owner.name if owner else task.owner_name),
                            ("client", task.client_id, new_client)):
        if old != new:
            changes.append(f"{field}: {old!r} -> {new!r}")
    task.title, task.due_date = title, due
    task.owner_id, task.owner_name = (owner.id, owner.name) if owner else (None, task.owner_name)
    task.client_id = new_client
    task.needs_confirmation, task.status = False, OPEN
    if changes:
        log_activity("task.corrected", "task", task.id, "; ".join(changes))
    log_activity("task.confirmed", "task", task.id)
    db.session.commit()

    if task.due_date:
        queue_action(task, "calendar", {
            "summary": f"[FollowUp] {task.title}", "date": task.due_date.isoformat(),
            "description": task.source_quote or ""}, current_user.id)
    refresh_priorities(today_sg())
    flash("Task confirmed. A calendar reminder is waiting in the Approval Queue." if task.due_date
          else "Task confirmed.", "success")
    return redirect(url_for("tasks.detail", task_id=task.id))


@bp.post("/<int:task_id>/reply")
@login_required
def log_reply(task_id):
    """Reply-aware reminders: once a reply or completion is recorded, chasing stops."""
    task = db.get_or_404(Task, task_id)
    kind = request.form.get("kind", "reply")
    task.reply_received = True
    if kind == "done":
        task.status = DONE
    elif task.status != DRAFT:
        task.status = OPEN
    log_activity("task.reply_logged" if kind == "reply" else "task.completed", "task", task.id, commit=True)
    flash("Recorded. Reminders for this task have stopped.", "success")
    return redirect(url_for("tasks.detail", task_id=task.id))
