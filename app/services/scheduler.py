"""APScheduler: reminders, digests, cleanup. Reply-aware: no reminder once a reply is recorded."""
import os

from apscheduler.schedulers.background import BackgroundScheduler

_scheduler: BackgroundScheduler | None = None


def reminder_job(app) -> None:
    from ..models import DONE, Task

    with app.app_context():
        tasks = Task.query.filter(Task.status != DONE, Task.reply_received.is_(False),
                                  Task.status == "waiting").all()
        for t in tasks:
            # TODO (Integrations owner): escalation ladder -> queue reminder 1, 2, then manager notice.
            app.logger.info("Reminder candidate: task %s (%s)", t.id, t.title)


def start_scheduler(app) -> None:
    global _scheduler
    if _scheduler or (app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true"):
        return  # avoid double start under the Flask reloader
    _scheduler = BackgroundScheduler(timezone=app.config["TIMEZONE"])
    _scheduler.add_job(reminder_job, "interval", minutes=30, args=[app], id="reminders")
    _scheduler.start()
