from datetime import date, datetime
from functools import wraps
from zoneinfo import ZoneInfo

from flask import abort, current_app
from flask_login import current_user

from .extensions import db
from .models import ActivityLog


def today_sg() -> date:
    return datetime.now(ZoneInfo(current_app.config["TIMEZONE"])).date()


def manager_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager:
            abort(403)
        return fn(*args, **kwargs)

    return wrapper


def log_activity(action: str, entity_type: str | None = None, entity_id: int | None = None,
                 detail: str = "", user_id: int | None = None, commit: bool = False) -> None:
    uid = user_id
    if uid is None and current_user and current_user.is_authenticated:
        uid = current_user.id
    db.session.add(ActivityLog(user_id=uid, action=action, entity_type=entity_type,
                               entity_id=entity_id, detail=detail))
    if commit:
        db.session.commit()
