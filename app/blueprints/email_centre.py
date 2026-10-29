from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import DONE, DRAFT, Approval, Task
from ..services.approvals import queue_action
from ..services.drafting import TONE_OPENERS, draft_followup
from ..services.llm_client import LLMError

bp = Blueprint("email_centre", __name__, url_prefix="/email")


@bp.route("/")
@login_required
def index():
    tasks = Task.query.filter(Task.status.notin_([DRAFT, DONE])).order_by(Task.due_date).all()
    sent = Approval.query.filter_by(kind="email").order_by(Approval.id.desc()).limit(20).all()
    return render_template("email_centre/index.html", tasks=tasks, sent=sent, tones=list(TONE_OPENERS))


@bp.post("/draft/<int:task_id>")
@login_required
def draft(task_id):
    task = db.get_or_404(Task, task_id)
    tone = request.form.get("tone", "friendly")
    to = request.form.get("to", "").strip() or "recipient@example.invalid"
    try:
        d = draft_followup(task, tone)
    except LLMError as exc:
        flash(f"{exc} Nothing was lost; please retry.", "danger")
        return redirect(url_for("email_centre.index"))
    queue_action(task, "email", {"to": to, "subject": d["subject"], "body": d["body"], "tone": tone},
                 current_user.id, ai_generated=True)
    flash("AI draft created. Review and approve it in the Approval Queue.", "success")
    return redirect(url_for("approvals.queue"))
