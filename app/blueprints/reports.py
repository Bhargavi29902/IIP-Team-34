import json

from flask import Blueprint, render_template
from flask_login import login_required

from ..config import Config
from ..models import EXECUTED, FAILED, ActivityLog, Approval, Task, DRAFT

bp = Blueprint("reports", __name__, url_prefix="/reports")


@bp.route("/")
@login_required
def index():
    confirmed = ActivityLog.query.filter_by(action="task.confirmed").count()
    corrected = ActivityLog.query.filter_by(action="task.corrected").count()
    stats = {
        "tasks_total": Task.query.count(),
        "tasks_confirmed": confirmed,
        "correction_rate": round(100 * corrected / confirmed) if confirmed else None,
        "actions_executed": Approval.query.filter_by(status=EXECUTED).count(),
        "actions_failed": Approval.query.filter_by(status=FAILED).count(),
        "labelled_emails": len(json.loads(Config.EVAL_FILE.read_text(encoding="utf-8"))),
    }
    return render_template("reports/index.html", stats=stats)
