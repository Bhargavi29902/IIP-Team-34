from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from ..extensions import db
from ..models import DONE, Task
from ..utils import manager_required

bp = Blueprint("team", __name__, url_prefix="/team")


@bp.route("/")
@login_required
@manager_required
def index():
    rows = (db.session.query(func.coalesce(Task.owner_name, "Unassigned"), func.count(Task.id))
            .filter(Task.status != DONE).group_by(Task.owner_name).all())
    return render_template("team/index.html", workload=rows)
