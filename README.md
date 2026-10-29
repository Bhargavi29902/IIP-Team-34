# FollowUp AI — IIP Team 34

**SCCCI × NYP AI Innovation Challenge 26S2**

FollowUp AI turns scattered audit commitments into a structured, trackable workflow.

> **AI proposes. A human decides. Every step leaves evidence.**

All data included in this repository is fictional demo data.

## Getting Started

### Prerequisites

- Python installed on your system
- Git (if cloning the repository)
- Docker Desktop (optional, for running with Docker)

### 1. Create a Virtual Environment

**Windows PowerShell**

Run these commands from the project root directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run the following command in the current terminal, then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Update `.env` only if you need to change the default configuration. Keep API keys and other secrets out of version control.

### 4. Initialise the Application

Create the database tables and populate the application with fictional demo data:

```powershell
flask --app run seed
```

### 5. Start the Application

```powershell
flask --app run run
```

Open the application at:

**http://127.0.0.1:5000**

### Demo Login Credentials

| Role | Email | Password |
|---|---|---|
| Staff | `priya@demo.local` | `demo1234` |
| Manager | `morgan@demo.local` | `demo1234` |

These credentials are intended for local demonstration only.

### Alternative: Run with Docker

If Docker Compose is configured for your environment:

```bash
docker compose up --build
```

## Default Configuration

FollowUp AI runs in **offline demo mode** by default:

- `LLM_PROVIDER=mock`
- `INTEGRATIONS_MODE=simulated`

This allows the application to run without external API keys or live integrations.

Simulated integration results are explicitly labelled **SIMULATED** in the UI. They must not be mistaken for real emails sent or calendar events created.

## Tests and AI Evaluation

Run the automated test suite:

```powershell
pytest -q
```

Evaluate extraction accuracy against the labelled email dataset:

```powershell
python eval/run_eval.py --mock
```

The evaluation reports per-field extraction accuracy using `eval/labelled_emails.json`.

The CI workflow at `.github/workflows/ci.yml` runs the checks on every push and fails if the configured extraction accuracy falls below **90%**.

## Features and Implementation Status

The following table distinguishes implemented functionality from planned work.

| Area | Status | Details |
|---|---|---|
| Authentication and security | Built | Login, staff/manager roles, CSRF protection and password hashing |
| Task Inbox | Built | Paste text, demo inbox, task extraction, draft tasks, source evidence, confidence scores and date explanations |
| AI extraction | Built | Mock extractor by default; real LLM integration available through `LLM_PROVIDER=anthropic` |
| Date validation | Built | Missing or vague dates require confirmation; holiday/weekend and duplicate warnings |
| Privacy and evidence | Built | Personal data masking and evidence checks |
| Task confirmation | Built | Edit and confirm tasks; corrections are logged and calendar actions enter the approval queue |
| Approval Queue | Built | Approve, edit or reject actions; idempotency keys, failure reporting and retry support |
| Email Centre | Built | AI-generated email drafts, tone selection, service-line templates and AI labelling |
| Dashboard and task management | Basic implementation | Dashboard, All Tasks, Task Details, Calendar list and Engagements timeline |
| Reports and settings | Basic implementation | Reports, Settings, Audit Log and AI Call Log |
| Reply-aware reminders | Partially built | Reply logging is implemented; scheduler job remains a stub |
| Google Calendar and Gmail | TODO | Live OAuth 2.0 integrations in `app/services/integrations.py` |
| Escalation and scheduling | TODO | Escalation ladder, smart send time and weekly digest in `app/services/scheduler.py` |
| Additional AI features | TODO | AI Assistant, PBC tracker, slip predictor, what-if analysis, handover, `.ics` export, batch upload, dictation and bookmarklet |

**Note:** “Built” describes the current implementation, not a guarantee that every feature is production-ready. Verify each feature and its integration mode before presenting it as complete.

## Team Responsibilities

Based on the team plan:

| Workstream | Main Files and Directories |
|---|---|
| Backend | `app/models.py`, `app/blueprints/`, `app/services/approvals.py` |
| Frontend | `app/templates/`, `app/static/` |
| AI and Prompt Engineering | `app/prompts/`, `app/services/extraction.py`, `app/services/drafting.py`, `eval/labelled_emails.json` |
| Integrations and Scheduling | `app/services/integrations.py`, `app/services/scheduler.py` |
| Testing and Evaluation | `tests/`, `eval/` |

The planned frontend workflow includes creating Figma wireframes for the Task Inbox, Dashboard, Approval Queue and Task Details.

## Core Safety and Reliability Rules

FollowUp AI is designed around human oversight, traceability and reliable execution.

1. **Human approval is required.** External actions must have an approved record in the Approval Queue before execution.
2. **Dates are never guessed.** Missing or ambiguous dates are flagged as `Needs confirmation`.
3. **Execution status must be truthful.** The application displays “sent” or “created” only after confirmation from the relevant provider. Failures preserve the draft and allow retries.
4. **Emails are untrusted input.** Text inside an email is treated as data, not as instructions to the AI. AI-generated output must not independently trigger external actions.
5. **Holiday data must be maintained.** `app/seed.py` currently seeds fixed-date holidays only. Movable holidays must be added using the relevant official Ministry of Manpower (MOM) information.

## Project Structure

```text
IIP-Team-34/
├── app/
│   ├── blueprints/
│   ├── prompts/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── models.py
│   └── seed.py
├── eval/
│   ├── labelled_emails.json
│   └── run_eval.py
├── tests/
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

*This is an indicative structure. Some files or directories may differ in the current repository.*

## Project Goal

FollowUp AI helps teams turn audit-related commitments into actionable, traceable tasks while keeping people in control of decisions and external actions.

The project prioritises transparency, evidence-based task extraction, human approval and clear separation between simulated demonstrations and real integrations.
