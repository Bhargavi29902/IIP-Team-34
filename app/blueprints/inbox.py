from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import Client, SourceMessage, Task, User
from ..services.extraction import ExtractionError
from ..services.pipeline import process_message
from ..utils import log_activity, today_sg

bp = Blueprint("inbox", __name__, url_prefix="/inbox")


@bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if not body:
            flash("Paste an email or note first.", "warning")
            return redirect(url_for("inbox.index"))
        try:
            sent = datetime.strptime(request.form.get("sent_on", ""), "%Y-%m-%d")
        except ValueError:
            sent = datetime.combine(today_sg(), datetime.min.time())
        msg = SourceMessage(kind=request.form.get("kind", "email"), subject=request.form.get("subject", "")[:200],
                            sender=request.form.get("sender", "")[:120], body=body, sent_at=sent,
                            is_demo=False, created_by=current_user.id)
        db.session.add(msg)
        db.session.commit()
        return _extract(msg)
    demo = SourceMessage.query.filter_by(is_demo=True, processed=False).order_by(SourceMessage.id).all()
    recent = SourceMessage.query.filter_by(processed=True).order_by(SourceMessage.id.desc()).limit(8).all()
    return render_template("inbox/index.html", demo=demo, recent=recent, today=today_sg().isoformat())


@bp.post("/extract/<int:message_id>")
@login_required
def extract_demo(message_id):
    return _extract(db.get_or_404(SourceMessage, message_id))


def _extract(msg: SourceMessage):
    try:
        tasks = process_message(msg, current_user.id)
    except ExtractionError as exc:
        flash(str(exc), "danger")  # text stays saved in the inbox; nothing is lost
        return redirect(url_for("inbox.index"))
    flash(f"{len(tasks)} suggested task(s). Review each one before confirming." if tasks
          else "No tasks found in this message.", "success" if tasks else "info")
    return redirect(url_for("inbox.review", message_id=msg.id))


@bp.route("/review/<int:message_id>")
@login_required
def review(message_id):
    msg = db.get_or_404(SourceMessage, message_id)
    return render_template("inbox/review.html", msg=msg, tasks=msg.tasks,
                           clients=Client.query.order_by(Client.name).all(),
                           users=User.query.order_by(User.name).all())
