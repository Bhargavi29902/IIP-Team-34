from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("assistant", __name__, url_prefix="/assistant")


@bp.route("/")
@login_required
def index():
    # TODO (AI owner, Wow): questions with citations. The AI picks from ALLOWED FILTERS only
    # (client, status, due range); the app runs a parameterised query. It never writes raw SQL.
    return render_template("assistant/index.html")
