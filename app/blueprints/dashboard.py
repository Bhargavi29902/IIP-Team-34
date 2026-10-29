from datetime import timedelta

from flask import Blueprint, render_template
from flask_login import login_required

from ..models import BLOCKED, DONE, DRAFT, PENDING, WAITING, Approval, Task
from ..services.priority import refresh_priorities
from ..utils import today_sg

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    today = today_sg()
    refresh_priorities(today)
    live = Task.query.filter(Task.status != DONE)
    confirmed = live.filter(Task.status != DRAFT)
    stats = {
        "overdue": confirmed.filter(Task.due_date < today).count(),
        "due_soon": confirmed.filter(Task.due_date >= today, Task.due_date <= today + timedelta(days=7)).count(),
        "waiting": live.filter(Task.status == WAITING, Task.reply_received.is_(False)).count(),
        "blocked": live.filter(Task.status == BLOCKED).count(),
        "to_review": live.filter(Task.status == DRAFT).count(),
        "pending_approvals": Approval.query.filter_by(status=PENDING).count(),
    }
    top = confirmed.order_by(Task.priority_score.desc()).limit(5).all()
    return render_template("dashboard/index.html", stats=stats, top=top)
