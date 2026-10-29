from flask import Blueprint, render_template
from flask_login import login_required

from ..models import DONE, DRAFT, Holiday, Task

bp = Blueprint("calendar_view", __name__, url_prefix="/calendar")


@bp.route("/")
@login_required
def index():
    tasks = Task.query.filter(Task.due_date.isnot(None), Task.status.notin_([DRAFT, DONE])).order_by(Task.due_date).all()
    holidays = {h.date: h.name for h in Holiday.query.all()}
    return render_template("calendar/index.html", tasks=tasks, holidays=holidays)
