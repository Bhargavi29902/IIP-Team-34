"""Google Calendar / Gmail. 'simulated' mode fakes results and says so; 'live' fails honestly
until OAuth is wired up. 'Sent' / 'created' is only ever shown after a real confirmation."""
import uuid

from flask import current_app


class IntegrationError(Exception):
    pass


def run_action(kind: str, payload: dict) -> dict:
    mode = current_app.config["INTEGRATIONS_MODE"]
    if mode == "simulated":
        return {"id": f"SIMULATED-{uuid.uuid4().hex[:10]}", "simulated": True}
    if kind == "calendar":
        return _create_calendar_event(payload)
    if kind == "email":
        return _send_email(payload)
    raise IntegrationError(f"Unknown action kind '{kind}'")


def _create_calendar_event(payload: dict) -> dict:
    # TODO (Integrations owner): build a service with google-api-python-client using OAuth2
    # credentials, call events().insert(calendarId="primary", body=...), return {"id": event["id"]}.
    raise IntegrationError("Google Calendar is not connected yet (OAuth not configured).")


def _send_email(payload: dict) -> dict:
    # TODO (Integrations owner): Gmail users().messages().send(...). Return {"id": sent["id"]}
    # only when the API confirms; otherwise raise IntegrationError so the draft is kept.
    raise IntegrationError("Gmail is not connected yet (OAuth not configured).")
