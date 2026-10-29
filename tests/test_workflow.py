from app.extensions import db
from app.models import EXECUTED, FAILED, PENDING, Approval, SourceMessage, Task
from app.services.approvals import approve, queue_action, reject


def _confirmed_task(client, login):
    login()
    msg = SourceMessage.query.filter(SourceMessage.subject.like("%Engagement letter%")).first()
    client.post(f"/inbox/extract/{msg.id}", follow_redirects=True)
    task = Task.query.first()
    client.post(f"/tasks/{task.id}/confirm", data={"title": task.title, "due_date": "2026-11-05"})
    return Task.query.first()


def test_login_required(client):
    assert client.get("/").status_code == 302


def test_extract_confirm_queues_calendar_approval(client, login, app):
    task = _confirmed_task(client, login)
    assert task.status == "open"
    a = Approval.query.filter_by(task_id=task.id, kind="calendar").one()
    assert a.status == PENDING  # nothing scheduled until a human approves


def test_cannot_confirm_without_date_or_explicit_no_date(client, login, app):
    login()
    msg = SourceMessage.query.filter(SourceMessage.subject.like("%Inventory%")).first()
    client.post(f"/inbox/extract/{msg.id}")
    task = Task.query.first()
    assert task.needs_confirmation and task.due_date is None
    client.post(f"/tasks/{task.id}/confirm", data={"title": task.title})
    assert Task.query.first().status == "draft"


def test_idempotent_queue_and_double_approve(client, login, app):
    task = _confirmed_task(client, login)
    a1, created1 = queue_action(task, "calendar", {"summary": "x", "date": "2026-11-05"}, 1)
    a2, created2 = queue_action(task, "calendar", {"summary": "x", "date": "2026-11-05"}, 1)
    assert created1 and not created2 and a1.id == a2.id
    first = approve(a1, 1)
    again = approve(a1, 1)
    assert first.status == again.status == EXECUTED and first.external_id == again.external_id
    assert "SIMULATED" in first.result_message


def test_failure_is_truthful_and_retryable(client, login, app):
    task = _confirmed_task(client, login)
    app.config["INTEGRATIONS_MODE"] = "live"  # not wired up yet -> must fail honestly
    a = Approval.query.filter_by(kind="calendar").first()
    approve(a, 1)
    assert a.status == FAILED and "not connected" in a.result_message
    assert "created" not in a.result_message.lower().replace("not", "")  # never claims success
    app.config["INTEGRATIONS_MODE"] = "simulated"
    approve(a, 1)
    assert a.status == EXECUTED


def test_reject_does_nothing_external(client, login, app):
    task = _confirmed_task(client, login)
    a = Approval.query.first()
    reject(a, 1)
    assert a.status == "rejected" and a.external_id is None


def test_reply_stops_reminders_flag(client, login, app):
    task = _confirmed_task(client, login)
    client.post(f"/tasks/{task.id}/reply", data={"kind": "reply"})
    assert Task.query.first().reply_received is True


def test_pages_render(client, login, app):
    login("morgan@demo.local")
    for path in ("/", "/inbox/", "/tasks/", "/approvals/", "/calendar/", "/email/", "/team/",
                 "/engagements/", "/assistant/", "/reports/", "/settings/", "/about/"):
        assert client.get(path).status_code == 200, path


def test_staff_cannot_open_manager_pages(client, login, app):
    login("priya@demo.local")
    assert client.get("/settings/").status_code == 403
    assert client.get("/team/").status_code == 403
