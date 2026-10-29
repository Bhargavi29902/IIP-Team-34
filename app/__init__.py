import os

from flask import Flask, render_template

from .config import BASE_DIR, Config
from .extensions import csrf, db, login_manager

NAV = [  # (endpoint, label, manager_only)
    ("dashboard.index", "Dashboard", False),
    ("inbox.index", "Task Inbox", False),
    ("tasks.list_tasks", "All Tasks", False),
    ("approvals.queue", "Approval Queue", False),
    ("calendar_view.index", "Calendar", False),
    ("email_centre.index", "Email Centre", False),
    ("team.index", "Team", True),
    ("engagements.index", "Engagements", False),
    ("assistant.index", "AI Assistant", False),
    ("reports.index", "Reports", False),
    ("settings.index", "Settings", True),
]


def create_app(config_object=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    os.makedirs(BASE_DIR / "instance", exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .blueprints import (approvals, assistant, auth, about, calendar_view, dashboard,
                             email_centre, engagements, inbox, reports, settings, tasks, team)
    for mod in (auth, dashboard, inbox, tasks, approvals, calendar_view, email_centre, team,
                engagements, assistant, reports, settings, about):
        app.register_blueprint(mod.bp)

    @app.context_processor
    def inject_globals():
        return {"NAV": NAV, "integrations_mode": app.config["INTEGRATIONS_MODE"],
                "llm_provider": app.config["LLM_PROVIDER"]}

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("errors/error.html", code=403,
                               message="You don't have access to this page."), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/error.html", code=404, message="Page not found."), 404

    @app.cli.command("seed")
    def seed_cmd():
        """Create tables and load fictional demo data."""
        from .seed import seed_demo
        db.create_all()
        seed_demo()
        print("Demo data ready. Login: priya@demo.local / demo1234 (manager: morgan@demo.local)")

    with app.app_context():
        db.create_all()

    if app.config["SCHEDULER_ENABLED"] and not app.config.get("TESTING"):
        from .services.scheduler import start_scheduler
        start_scheduler(app)
    return app
