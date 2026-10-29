from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import login_required

from ..models import ActivityLog, AICallLog, EmailTemplate, Holiday
from ..seed import seed_demo
from ..utils import manager_required

bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/")
@login_required
@manager_required
def index():
    return render_template(
        "settings/index.html",
        holidays=Holiday.query.order_by(Holiday.date).all(),
        templates=EmailTemplate.query.all(),
        audit=ActivityLog.query.order_by(ActivityLog.id.desc()).limit(50).all(),
        ai_calls=AICallLog.query.order_by(AICallLog.id.desc()).limit(20).all(),
        cfg=current_app.config)


@bp.post("/reset-demo")
@login_required
@manager_required
def reset_demo():
    seed_demo(reset=True)
    flash("Demo reset. You have been signed out because users were re-created.", "info")
    return redirect(url_for("auth.login"))
