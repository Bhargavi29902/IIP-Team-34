"""Personal data masking: hide emails, phone numbers and NRIC before text goes to the AI service."""
import re

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
NRIC_RE = re.compile(r"\b[STFGM]\d{7}[A-Z]\b", re.I)
PHONE_RE = re.compile(r"(?<![\w\[])(?:\+65[\s-]?)?[689]\d{3}[\s-]?\d{4}(?!\w)")

_PATTERNS = (("EMAIL", EMAIL_RE), ("NRIC", NRIC_RE), ("PHONE", PHONE_RE))


def mask_text(text: str) -> tuple[str, dict[str, str]]:
    mapping: dict[str, str] = {}
    counters: dict[str, int] = {}

    for label, pattern in _PATTERNS:
        def repl(m, label=label):
            counters[label] = counters.get(label, 0) + 1
            token = f"[{label}_{counters[label]}]"
            mapping[token] = m.group(0)
            return token

        text = pattern.sub(repl, text)
    return text, mapping


def unmask_text(text: str | None, mapping: dict[str, str]) -> str | None:
    if text is None:
        return None
    for token, original in mapping.items():
        text = text.replace(token, original)
    return text
