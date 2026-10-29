"""Date resolution: turn 'by Thursday' into a real date, never guess vague wording."""
import calendar
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from dateutil import parser as dparser

WEEKDAYS = {n: i for i, n in enumerate(
    ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])}
VAGUE_RE = re.compile(
    r"\b(asap|as soon as possible|soon|shortly|later|when you can|next week|this week|"
    r"end of (the )?week|eod|urgent)\b", re.I)
_PREFIX = re.compile(r"^(by|before|on|due|until)\s+", re.I)


@dataclass
class DateResolution:
    value: date | None
    reason: str
    ambiguous: bool = False


def _fmt(d: date) -> str:
    return d.strftime("%a %d %b %Y")


def resolve_due_date(text: str | None, sent_on: date) -> DateResolution:
    if not text or not text.strip():
        return DateResolution(None, "No date mentioned.", True)
    t = _PREFIX.sub("", text.strip().lower())

    if VAGUE_RE.search(t):
        return DateResolution(None, f"'{text.strip()}' is too vague to turn into a date.", True)
    if t == "today":
        return DateResolution(sent_on, f"'today' from email sent {_fmt(sent_on)}.")
    if t == "tomorrow":
        d = sent_on + timedelta(days=1)
        return DateResolution(d, f"'tomorrow' from email sent {_fmt(sent_on)} -> {_fmt(d)}.")

    m = re.fullmatch(r"(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", t)
    if m:
        delta = (WEEKDAYS[m.group(2)] - sent_on.weekday()) % 7 or 7
        d = sent_on + timedelta(days=delta)
        if m.group(1) and d.isocalendar()[:2] == sent_on.isocalendar()[:2]:
            d += timedelta(days=7)
        return DateResolution(d, f"'{text.strip()}' from email sent {_fmt(sent_on)} -> {_fmt(d)}.")

    if re.fullmatch(r"end of (the )?month", t):
        last = calendar.monthrange(sent_on.year, sent_on.month)[1]
        d = sent_on.replace(day=last)
        return DateResolution(d, f"End of month from email sent {_fmt(sent_on)} -> {_fmt(d)}.")

    try:
        default = datetime(sent_on.year, sent_on.month, sent_on.day)
        parsed = dparser.parse(t, default=default, dayfirst=True).date()
        if not re.search(r"\b\d{4}\b", t) and parsed < sent_on:
            parsed = parsed.replace(year=parsed.year + 1)
        return DateResolution(parsed, f"Read '{text.strip()}' as {_fmt(parsed)}.")
    except (ValueError, OverflowError):
        return DateResolution(None, f"Could not read '{text.strip()}' as a date.", True)


def date_warnings(d: date | None, holidays: dict[date, str]) -> list[str]:
    if d is None:
        return []
    out = []
    if d in holidays:
        out.append(f"Due date is a Singapore public holiday ({holidays[d]})")
    if d.weekday() >= 5:
        out.append(f"Due date falls on a {d.strftime('%A')}")
    return out
