# FollowUp AI (IIP Team 34)

SCCCI × NYP AI Innovation Challenge 26S2. Turns scattered audit commitments into a trackable workflow.
**AI proposes, a human decides, every step leaves evidence.** All data in this repo is fictional demo data.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # Windows: copy .env.example .env
flask --app run seed                                   # creates tables + fictional demo data
flask --app run run                                    # http://127.0.0.1:5000
```

Login: `priya@demo.local` (staff) or `morgan@demo.local` (manager), password `demo1234`.
Or with Docker: `docker compose up --build`.

By default the app runs **offline** (`LLM_PROVIDER=mock`, `INTEGRATIONS_MODE=simulated`), so everyone can
work without API keys. Simulated results are always labelled "SIMULATED" in the UI.

## Tests and AI evaluation

```bash
pytest -q                          # unit tests + extraction accuracy check
python eval/run_eval.py --mock     # per-field accuracy on eval/labelled_emails.json
```
CI (`.github/workflows/ci.yml`) runs the same on every push and fails if accuracy drops below 90%.

## What is built (base) vs. what is TODO

| Area | Status |
|---|---|
| Login, staff/manager roles, CSRF, password hashing | Built |
| Task Inbox: paste text, demo inbox, extraction -> draft tasks with source evidence, confidence, "Why this date?" | Built (mock extractor; real LLM via `LLM_PROVIDER=anthropic`) |
| Never-guess dates, holiday/weekend warning, duplicate warning, personal data masking, evidence check | Built |
| Edit and confirm (corrections are logged) -> queues calendar approval | Built |
| Approval Queue: approve/edit/reject, idempotency keys, truthful success/failure + retry | Built |
| Email Centre: AI draft with tone + service-line templates + AI label | Built |
| Dashboard, All Tasks, Task Details, Calendar list, Engagements timeline, Reports (basic), Settings/Audit/AI call log | Built (basic) |
| Reply-aware reminders: logging a reply stops reminders | Flag built; scheduler job is a stub |
| Real Google Calendar + Gmail (OAuth 2.0) | **TODO** `app/services/integrations.py` |
| Escalation ladder, smart send time, weekly digest | **TODO** `app/services/scheduler.py` |
| AI Assistant, PBC tracker, slip predictor, what-if, handover, .ics, batch upload, dictation, bookmarklet | **TODO (Wow, pick ~5)** |

## Who edits what (from the team plan)

- **Backend:** `app/models.py`, `app/blueprints/`, `app/services/approvals.py`
- **Frontend:** `app/templates/`, `app/static/` (wireframe Task Inbox, Dashboard, Approval Queue, Task Details in Figma first)
- **AI:** `app/prompts/` (versioned), `app/services/extraction.py`, `app/services/drafting.py`, `eval/labelled_emails.json`
- **Integrations:** `app/services/integrations.py`, `app/services/scheduler.py`
- **Testing / pitch:** `tests/`, `eval/`

## Rules the code already follows
1. Nothing external happens without an approved row in the Approval Queue.
2. Missing or vague dates are flagged "Needs confirmation", never guessed.
3. "Sent" / "created" appears only after the provider confirms; failures keep the draft and allow retry.
4. Text inside an email is data, never instructions; AI output can never trigger an action.
5. Holidays in `app/seed.py`: only fixed-date ones are seeded. Add movable ones from MOM's official list.
