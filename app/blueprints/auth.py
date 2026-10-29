
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired

from ..models import User
from ..utils import log_activity

bp = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        # Temporary debugging information
        print("DEBUG: Login route reached")
        print("DEBUG: Submitted email:", repr(email))
        print("DEBUG: User found:", user is not None)

        if user:
            password_matches = user.check_password(password)
            print("DEBUG: Password matches:", password_matches)
        else:
            password_matches = False

        if user and password_matches:
            login_user(user)
            log_activity("auth.login", "user", user.id, commit=True)

            next_url = request.args.get("next", "")

            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)

            return redirect(url_for("dashboard.index"))

        flash("Wrong email or password.", "danger")

    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        log_activity("auth.logout", "user", current_user.id, commit=True)
        logout_user()

    return redirect(url_for("auth.login"))
