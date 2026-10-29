"""Database tables. Mirrors the feature map: tasks, approvals, activity_logs, holidays, AI call log."""
import json
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Task statuses
DRAFT, OPEN, WAITING, BLOCKED, DONE = "draft", "open", "waiting", "blocked", "done"
OPEN_STATUSES = (DRAFT, OPEN, WAITING, BLOCKED)

# Approval statuses
PENDING, EXECUTED, FAILED, REJECTED = "pending", "executed", "failed", "rejected"


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="staff")  # staff | manager

    def set_password(self, pw: str) -> None:
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        return check_password_hash(self.password_hash, pw)

    @property
    def is_manager(self) -> bool:
        return self.role == "manager"


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    service_line = db.Column(db.String(30), default="audit")  # audit | tax | ipo | advisory
    tasks = db.relationship("Task", back_populates="client")


class SourceMessage(db.Model):
    __tablename__ = "source_messages"
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(20), default="email")  # email | note | transcript
    subject = db.Column(db.String(200))
    sender = db.Column(db.String(120))
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=utcnow)
    is_demo = db.Column(db.Boolean, default=False)  # fictional data is always labelled
    processed = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=utcnow)
    tasks = db.relationship("Task", back_populates="message")


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("source_messages.id"))
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner_name = db.Column(db.String(80))
    title = db.Column(db.String(300), nullable=False)
    due_date = db.Column(db.Date)
    due_date_text = db.Column(db.String(120))  # the original wording, e.g. "by Thursday"
    due_reason = db.Column(db.Text)  # "Why this date?"
    source_quote = db.Column(db.Text)  # source evidence
    confidence = db.Column(db.Float, default=0.0)
    needs_confirmation = db.Column(db.Boolean, default=True)
    flags = db.Column(db.Text, default="")  # pipe-separated warnings
    status = db.Column(db.String(20), default=DRAFT)
    priority_score = db.Column(db.Integer, default=0)
    priority_reason = db.Column(db.String(200))
    thread_summary = db.Column(db.Text)
    calendar_event_id = db.Column(db.String(200))
    reply_received = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    message = db.relationship("SourceMessage", back_populates="tasks")
    client = db.relationship("Client", back_populates="tasks")
    owner = db.relationship("User", foreign_keys=[owner_id])

    @property
    def flag_list(self) -> list[str]:
        return [f for f in (self.flags or "").split("|") if f]

    def set_flags(self, flags: list[str]) -> None:
        self.flags = "|".join(dict.fromkeys(flags))


class TaskDependency(db.Model):
    __tablename__ = "task_dependencies"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)  # waits for...
    depends_on_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)


class Approval(db.Model):
    """Every external action (calendar, email) starts here and waits for a human."""
    __tablename__ = "approvals"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    kind = db.Column(db.String(20), nullable=False)  # calendar | email
    payload = db.Column(db.Text, nullable=False)  # JSON
    status = db.Column(db.String(20), default=PENDING)
    idempotency_key = db.Column(db.String(64), unique=True, nullable=False)
    result_message = db.Column(db.Text)
    external_id = db.Column(db.String(200))
    simulated = db.Column(db.Boolean, default=False)
    ai_generated = db.Column(db.Boolean, default=False)
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    decided_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    decided_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=utcnow)

    task = db.relationship("Task")

    @property
    def data(self) -> dict:
        return json.loads(self.payload)

    def set_data(self, d: dict) -> None:
        self.payload = json.dumps(d, ensure_ascii=False)


class ActivityLog(db.Model):
    """Audit log: who changed, approved or sent what, and the result."""
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(60), nullable=False)
    entity_type = db.Column(db.String(40))
    entity_id = db.Column(db.Integer)
    detail = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)
    user = db.relationship("User")


class Holiday(db.Model):
    __tablename__ = "holidays"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)


class EmailTemplate(db.Model):
    __tablename__ = "email_templates"
    id = db.Column(db.Integer, primary_key=True)
    service_line = db.Column(db.String(30), unique=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)  # {client} {title} {due} {owner}


class AICallLog(db.Model):
    __tablename__ = "ai_call_logs"
    id = db.Column(db.Integer, primary_key=True)
    purpose = db.Column(db.String(40))
    prompt_version = db.Column(db.String(60))
    model = db.Column(db.String(80))
    latency_ms = db.Column(db.Integer)
    success = db.Column(db.Boolean, default=True)
    error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow)
