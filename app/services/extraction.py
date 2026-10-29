"""Structured extraction: LLM (or offline mock) -> JSON -> Pydantic -> evidence + date checks."""
import json
import re
from datetime import date

from flask import current_app
from pydantic import BaseModel, Field, ValidationError

from .dates import VAGUE_RE, resolve_due_date
from .llm_client import LLMError, call_llm, load_prompt
from .masking import mask_text, unmask_text


class ExtractionError(Exception):
    pass


class ExtractedTask(BaseModel):
    title: str
    owner: str | None = None
    due_date_text: str | None = None
    due_date: date | None = None
    client: str | None = None
    source_quote: str
    confidence: float = Field(default=0.5, ge=0, le=1)
    needs_confirmation: bool = False
    due_reason: str | None = None
    flags: list[str] = []


class ExtractionResult(BaseModel):
    tasks: list[ExtractedTask] = []


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def extract_tasks(body: str, sent_on: date, client_names: list[str]) -> ExtractionResult:
    cfg = current_app.config
    if cfg["LLM_PROVIDER"] == "mock":
        raw = mock_extract(body, client_names)
    else:
        raw = _llm_extract(body, sent_on, client_names)
    return _postprocess(raw, body, sent_on)


def _llm_extract(body: str, sent_on: date, client_names: list[str]) -> ExtractionResult:
    cfg = current_app.config
    mapping: dict[str, str] = {}
    text = body
    if cfg["MASK_PERSONAL_DATA"]:
        text, mapping = mask_text(body)
    system = load_prompt(cfg["EXTRACTION_PROMPT"], client_list=", ".join(client_names) or "none",
                         sent_on=sent_on.isoformat())
    try:
        out = call_llm(system, f"<email>\n{text}\n</email>", "extraction", cfg["EXTRACTION_PROMPT"])
    except LLMError as exc:
        raise ExtractionError(f"The AI service failed: {exc}. Your text is kept; please retry.") from exc
    out = re.sub(r"^```(?:json)?|```$", "", out.strip(), flags=re.M).strip()
    try:
        result = ExtractionResult.model_validate(json.loads(out))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ExtractionError("The AI returned an unreadable answer. Please retry.") from exc
    for t in result.tasks:  # put real emails/phones back (quotes must match the original)
        t.title = unmask_text(t.title, mapping)
        t.owner = unmask_text(t.owner, mapping)
        t.source_quote = unmask_text(t.source_quote, mapping)
    return result


def _postprocess(result: ExtractionResult, body: str, sent_on: date) -> ExtractionResult:
    nbody = _norm(body)
    for t in result.tasks:
        flags = list(t.flags)
        # 1. evidence must really be in the source
        if not t.source_quote or _norm(t.source_quote) not in nbody:
            flags.append("Source quote not found in the original text")
            t.needs_confirmation = True
            t.confidence = min(t.confidence, 0.4)
        # 2. never trust/guess dates: resolve wording ourselves
        res = resolve_due_date(t.due_date_text, sent_on) if t.due_date_text else None
        if res and res.value:
            t.due_date, t.due_reason = res.value, res.reason
        elif t.due_date and t.due_date_text is None:
            t.due_reason = "Date supplied by the AI without wording to check; please confirm."
            t.needs_confirmation = True
        else:
            t.due_date = None
            t.due_reason = res.reason if res else "No date mentioned."
            t.needs_confirmation = True
            flags.append("Needs confirmation: due date")
        if not t.owner:
            flags.append("Owner missing")
        t.flags = flags
    return result


# ---------------- offline mock (dev + CI, no API key needed) ----------------
_ACTION = re.compile(
    r"\b(please|kindly|can you|could you|need to|must|remember to|don't forget|follow up|"
    r"send|provide|submit|share|confirm|review|prepare|upload|chase|finali[sz]e|complete)\b", re.I)
_INJECTION = re.compile(r"ignore (all |any )?(previous|prior|your|the above)[^.]*instructions", re.I)
_DAYS = r"(?:next\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
_MONTHS = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
_DATE_PHRASE = re.compile(
    rf"\b(?:by|before|on|due|until)\s+({_DAYS}|tomorrow|today|end of (?:the )?month|"
    rf"\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTHS}(?:\s+\d{{4}})?)", re.I)
_GREETING = re.compile(r"\b(?i:hi|hello|dear)\s+([A-Z][a-z]+)")
_NOT_A_NAME = {"Team", "All", "Everyone", "Both", "There", "Folks"}
_LEAD = re.compile(r"^(?:also,?\s+|and\s+|please\s+|kindly\s+|could you\s+|can you\s+|remember to\s+)+", re.I)


def mock_extract(body: str, client_names: list[str]) -> ExtractionResult:
    g = _GREETING.search(body)
    owner = g.group(1) if g and g.group(1) not in _NOT_A_NAME else None
    tasks = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", body):
        s = sentence.strip()
        if not s or _INJECTION.search(s) or not _ACTION.search(s):
            continue
        m = _DATE_PHRASE.search(s)
        v = VAGUE_RE.search(s)
        date_text = m.group(1) if m else (v.group(0) if v else None)
        title = re.sub(r"^(?:hi|hello|dear)\s+[A-Za-z]+,?\s*", "", re.sub(r"[?.!]+$", "", s), flags=re.I)
        title = _LEAD.sub("", title).strip()
        title = re.sub(r"\s+(?:by|before|on|due|until)\s+" + re.escape(date_text) + r"$", "", title, flags=re.I) \
            if date_text else title
        title = title[:1].upper() + title[1:]
        client = next((n for n in client_names
                       if n.lower() in s.lower() or n.split()[0].lower() in s.lower()), None)
        tasks.append(ExtractedTask(title=title[:250], owner=owner, due_date_text=date_text,
                                   client=client, source_quote=s,
                                   confidence=0.85 if m else 0.55))
    return ExtractionResult(tasks=tasks)
