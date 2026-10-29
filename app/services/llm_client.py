"""One place that talks to the LLM. Every call is logged (latency, failures)."""
import time
from pathlib import Path
from string import Template

from flask import current_app

from ..extensions import db
from ..models import AICallLog

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


class LLMError(Exception):
    pass


def load_prompt(name: str, **values) -> str:
    return Template((PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8")).safe_substitute(**values)


def call_llm(system: str, user: str, purpose: str, prompt_version: str) -> str:
    cfg = current_app.config
    provider, model = cfg["LLM_PROVIDER"], cfg["LLM_MODEL"]
    start = time.perf_counter()
    try:
        if provider != "anthropic":
            raise LLMError(f"LLM_PROVIDER '{provider}' cannot call a model (use 'anthropic').")
        if not cfg["ANTHROPIC_API_KEY"]:
            raise LLMError("ANTHROPIC_API_KEY is not set.")
        import anthropic  # imported lazily so mock mode needs no key

        client = anthropic.Anthropic(api_key=cfg["ANTHROPIC_API_KEY"])
        resp = client.messages.create(
            model=model, max_tokens=1500, system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        _log(purpose, prompt_version, model, start, True, None)
        return text
    except Exception as exc:  # keep the user's draft; show a truthful error upstream
        _log(purpose, prompt_version, model, start, False, str(exc))
        raise LLMError(str(exc)) from exc


def _log(purpose, version, model, start, ok, error):
    db.session.add(AICallLog(purpose=purpose, prompt_version=version, model=model,
                             latency_ms=int((time.perf_counter() - start) * 1000),
                             success=ok, error=error))
    db.session.commit()
