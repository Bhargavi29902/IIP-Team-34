from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import EXECUTED, FAILED, PENDING, REJECTED, Approval
from ..services.approvals import approve, reject

bp = Blueprint("approvals", __name__, url_prefix="/approvals")


@bp.route("/")
@login_required
def queue():
    pending = Approval.query.filter(Approval.status.in_([PENDING, FAILED])).order_by(Approval.id).all()
    history = Approval.query.filter(Approval.status.in_([EXECUTED, REJECTED])).order_by(Approval.id.desc()).limit(30).all()
    return render_template("approvals/queue.html", pending=pending, history=history)


@bp.post("/<int:approval_id>/approve")
@login_required
def approve_action(approval_id):
    a = db.get_or_404(Approval, approval_id)
    edits = {k: request.form[k] for k in ("subject", "body", "to") if k in request.form} if a.kind == "email" else None
    a = approve(a, current_user.id, edits)
    flash(a.result_message, "success" if a.status == EXECUTED else "danger")
    return redirect(url_for("approvals.queue"))


@bp.post("/<int:approval_id>/reject")
@login_required
def reject_action(approval_id):
    reject(db.get_or_404(Approval, approval_id), current_user.id)
    flash("Rejected. Nothing was sent or scheduled.", "info")
    return redirect(url_for("approvals.queue"))
