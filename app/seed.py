"""Fictional demo data. Everything seeded here is labelled demo data (is_demo=True)."""
import json
from datetime import date, datetime

from .config import Config
from .extensions import db
from .models import (ActivityLog, AICallLog, Approval, Client, EmailTemplate, Holiday,
                     SourceMessage, Task, TaskDependency, User)

CLIENTS = [("Harbourview Logistics Pte Ltd", "audit"), ("Lotus Bay Hotels", "tax"),
           ("Meridian Foods Pte Ltd", "advisory")]

# Fixed-date Singapore holidays only. Movable ones (CNY, Hari Raya, Vesak, Deepavali, Good Friday)
# must be added from MOM's official list: https://www.mom.gov.sg/employment-practices/public-holidays
HOLIDAYS = [(date(2026, 12, 25), "Christmas Day"), (date(2027, 1, 1), "New Year's Day"),
            (date(2027, 5, 1), "Labour Day"), (date(2027, 8, 9), "National Day")]

TEMPLATES = {
    "audit": ("Audit follow-up: {title} ({client})",
              "we are following up on the audit item \"{title}\" for {client}. It was due on {due}. Could you share an update?\n\nThank you."),
    "tax": ("Tax follow-up: {title} ({client})",
            "a quick follow-up on \"{title}\" for {client}, due {due}, so we can meet the filing timeline.\n\nThank you."),
    "ipo": ("IPO workstream: {title} ({client})",
            "please confirm status on \"{title}\" for {client} (due {due}) as it affects the listing timetable.\n\nThank you."),
    "advisory": ("Advisory follow-up: {title} ({client})",
                 "checking in on \"{title}\" for {client}, due {due}. Let us know if you need anything from us.\n\nThank you."),
}


def seed_demo(reset: bool = False) -> None:
    if reset:
        for model in (TaskDependency, Approval, Task, SourceMessage, ActivityLog, AICallLog,
                      EmailTemplate, Holiday, Client, User):
            db.session.query(model).delete()
        db.session.commit()
    if User.query.first():
        return

    for name, email, role in [("Priya Demo", "priya@demo.local", "staff"),
                              ("Marcus Demo", "marcus@demo.local", "staff"),
                              ("Morgan Manager", "morgan@demo.local", "manager")]:
        u = User(name=name, email=email, role=role)
        u.set_password("demo1234")
        db.session.add(u)
    for name, line in CLIENTS:
        db.session.add(Client(name=name, service_line=line))
    for d, n in HOLIDAYS:
        db.session.add(Holiday(date=d, name=n))
    for line, (subject, body) in TEMPLATES.items():
        db.session.add(EmailTemplate(service_line=line, subject=subject, body=body))

    for case in json.loads(Config.EVAL_FILE.read_text(encoding="utf-8")):
        y, m, d = map(int, case["sent_on"].split("-"))
        db.session.add(SourceMessage(kind="email", subject=f"[DEMO] {case['subject']}",
                                     sender=case["sender"], body=case["body"],
                                     sent_at=datetime(y, m, d, 9, 0), is_demo=True))
    db.session.commit()
