from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from ..extensions import db
from ..models import ActivityLog, Client, Task

bp = Blueprint("engagements", __name__, url_prefix="/engagements")


@bp.route("/")
@login_required
def index():
    counts = dict(db.session.query(Task.client_id, func.count(Task.id)).group_by(Task.client_id).all())
    return render_template("engagements/index.html", clients=Client.query.order_by(Client.name).all(), counts=counts)


@bp.route("/<int:client_id>")
@login_required
def timeline(client_id):
    client = db.get_or_404(Client, client_id)
    tasks = Task.query.filter_by(client_id=client.id).order_by(Task.created_at).all()
    ids = [t.id for t in tasks]
    logs = (ActivityLog.query.filter(ActivityLog.entity_type == "task", ActivityLog.entity_id.in_(ids))
            .order_by(ActivityLog.created_at).all() if ids else [])
    return render_template("engagements/timeline.html", client=client, tasks=tasks, logs=logs)
