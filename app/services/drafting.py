"""AI-drafted follow-up emails. Mock mode uses the template table so dev works offline."""
import json
import re

from flask import current_app

from ..models import EmailTemplate, Task
from .llm_client import LLMError, call_llm, load_prompt
from .masking import mask_text

TONE_OPENERS = {
    "friendly": "Hope you're well! ",
    "formal": "Dear colleague, ",
    "firm": "Following up on an outstanding item: ",
}
AI_FOOTER = "\n\n[Drafted with AI assistance and approved by a team member]"


def draft_followup(task: Task, tone: str = "friendly") -> dict:
    cfg = current_app.config
    service_line = (task.client.service_line if task.client else "audit") or "audit"
    due = task.due_date.strftime("%d %b %Y") if task.due_date else "the agreed date"
    client = task.client.name if task.client else "your team"
    if cfg["LLM_PROVIDER"] == "mock":
        tpl = EmailTemplate.query.filter_by(service_line=service_line).first()
        subject = (tpl.subject if tpl else "Follow-up: {title}").format(
            client=client, title=task.title, due=due, owner=task.owner_name or "")
        body = (tpl.body if tpl else "Could you please update us on: {title}? Due: {due}.").format(
            client=client, title=task.title, due=due, owner=task.owner_name or "")
        result = {"subject": subject, "body": TONE_OPENERS.get(tone, "") + body}
    else:
        system = load_prompt(cfg["DRAFT_PROMPT"], tone=tone, service_line=service_line)
        masked, _ = mask_text(f"{task.title} | client: {client} | due: {due}")
        try:
            out = call_llm(system, f"<task>{masked}</task>", "draft", cfg["DRAFT_PROMPT"])
            result = json.loads(re.sub(r"^```(?:json)?|```$", "", out.strip(), flags=re.M).strip())
        except (LLMError, json.JSONDecodeError) as exc:
            raise LLMError(f"Draft failed: {exc}") from exc
    if cfg["AI_LABEL_IN_EMAILS"]:
        result["body"] += AI_FOOTER
    return result
