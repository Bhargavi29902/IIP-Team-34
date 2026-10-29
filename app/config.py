import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _db_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    default = f"sqlite:///{BASE_DIR / 'instance' / 'followup.db'}"
    if not url:
        return default
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////") and ":memory:" not in url:
        return f"sqlite:///{BASE_DIR / url[len('sqlite:///'):]}"  # relative -> project folder
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = _db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TIMEZONE = "Asia/Singapore"

    # AI
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")  # mock | anthropic
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    MASK_PERSONAL_DATA = _bool("MASK_PERSONAL_DATA", "true")
    EXTRACTION_PROMPT = "extraction_v1"
    DRAFT_PROMPT = "email_draft_v1"

    # Google / integrations
    INTEGRATIONS_MODE = os.getenv("INTEGRATIONS_MODE", "simulated")  # simulated | live
    GOOGLE_CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "credentials.json")

    # Misc
    SCHEDULER_ENABLED = _bool("SCHEDULER_ENABLED", "true")
    DEMO_RETENTION_DAYS = int(os.getenv("DEMO_RETENTION_DAYS", "30"))
    AI_LABEL_IN_EMAILS = True
    EVAL_FILE = BASE_DIR / "eval" / "labelled_emails.json"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    SCHEDULER_ENABLED = False
    LLM_PROVIDER = "mock"
    INTEGRATIONS_MODE = "simulated"
    SECRET_KEY = "test"