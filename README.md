# FollowUp AI

**IIP Team 34 | SCCCI × NYP AI Innovation Challenge 26S2**

FollowUp AI is an AI-assisted follow-up management application designed to help teams organise follow-ups, review suggested actions, and maintain a traceable record of decisions.

> **AI proposes. A human decides. Every step leaves evidence.**

The project demonstrates how AI can support follow-up workflows while keeping human users responsible for decisions and approvals.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Principles](#key-principles)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Demo Accounts](#demo-accounts)
- [Running Tests](#running-tests)
- [Docker Setup](#docker-setup)
- [Troubleshooting](#troubleshooting)
- [Responsible AI and Security](#responsible-ai-and-security)
- [Team Contributions](#team-contributions)
- [Future Improvements](#future-improvements)

---

## Project Overview

FollowUp AI explores how artificial intelligence can help teams manage follow-up activities more consistently.

The application is designed around three ideas:

1. AI can suggest possible actions and follow-up messages.
2. Human users should review and approve important decisions.
3. Important actions should leave an auditable record.

The project supports a demonstration environment using mock AI responses and simulated integrations, allowing the core workflow to be explored without requiring live external services.

**Demo data is fictional.** Do not use real confidential information when demonstrating the application.

## Key Principles

### Human-in-the-loop

AI-generated recommendations are suggestions. Users remain responsible for reviewing and deciding what action to take.

### Traceability

Important actions and decisions should be recorded so that users can understand what happened during a workflow.

### Responsible AI

The application should avoid unsupported claims, clearly distinguish simulated actions from real actions, and protect sensitive information.

### Offline-friendly demonstration

The default configuration is designed to support a demo using mock AI and simulated integrations.

---

## Features

The project is intended to demonstrate the following capabilities. Availability of individual features depends on the current implementation in the repository.

| Feature | Description |
|---|---|
| AI-assisted follow-ups | Suggest possible next steps and follow-up content |
| Human review | Keep users responsible for important decisions |
| Traceability | Record important workflow actions and decisions |
| Mock AI provider | Support demonstrations without a live AI provider |
| Simulated integrations | Demonstrate integration workflows without live external actions |
| Database support | Store application data using SQLite in the local development setup |
| Automated tests | Verify application behaviour |
| Evaluation resources | Support evaluation of selected application behaviours |

Refer to the application code and tests for the definitive list of implemented features.

## Technology Stack

The repository includes the following technologies and components:

- **Python** — application programming language
- **Flask** — web application framework
- **Flask-SQLAlchemy / SQLAlchemy** — database integration
- **SQLite** — local development database
- **pytest** — automated testing
- **Docker and Docker Compose** — containerised development, where configured
- **Mock AI and simulated integrations** — demonstration support

For exact dependency versions, refer to `requirements.txt`.

---

## Project Structure

```text
IIP-Team-34/
├── .github/              # GitHub workflows and configuration
├── app/                  # Application code
├── eval/                 # Evaluation resources
├── instance/             # Flask instance data and database
├── tests/                # Automated tests
├── .env                  # Local environment configuration
├── .env.example          # Example environment configuration
├── .gitignore            # Git ignore rules
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
├── run.py                # Flask application entry point
└── README.md              # Project documentation
```

Keep local secrets and sensitive environment settings out of version control.

---

## Prerequisites

Before running the application, ensure you have:

- Python installed
- PowerShell on Windows, or a compatible terminal
- Git, if you are cloning the repository
- Docker Desktop, if you intend to use Docker

You should also have access to the project files.

## Installation and Setup

### Step 1: Open the project directory

Open PowerShell and navigate to the actual project directory containing `run.py` and `requirements.txt`.

Example:

```powershell
cd C:\Users\perur\Downloads\IIP-Team-34\IIP-Team-34
```

Your path may be different. Use the correct location on your computer.

Check that you are in the right directory:

```powershell
ls
```

You should see files such as:

```text
app/
instance/
tests/
eval/
.env
.env.example
requirements.txt
run.py
```

**Important:** If you see another folder named `IIP-Team-34` inside your current directory, check whether the actual project files are inside that nested folder before continuing.

### Step 2: Create a virtual environment

If you have not already created a virtual environment for the project, run:

```powershell
py -m venv .venv
```

A virtual environment keeps the project's Python dependencies separate from other Python projects.

If `.venv` already exists and works, you do not need to recreate it.

### Step 3: Activate the virtual environment

If `.venv` is located in your current project directory, activate it with:

```powershell
.\.venv\Scripts\Activate.ps1
```

If your virtual environment is located in the parent directory, use the path to that existing environment instead. For example, from the nested project directory:

```powershell
..\.venv\Scripts\Activate.ps1
```

When activated, PowerShell normally displays `(.venv)` at the beginning of the prompt.

### Step 4: Install the dependencies

Run this command from the directory containing `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Wait for the installation to complete before proceeding.

A pip notice saying that a newer version is available is informational and does not necessarily indicate a failure.

---

## Environment Configuration

The repository includes `.env.example`, which provides example environment settings.

If you do not have a `.env` file yet, create one by running:

```powershell
Copy-Item .env.example .env
```

If `.env` already exists and contains your configuration, do not overwrite it unnecessarily.

Open the file with:

```powershell
notepad .env
```

Review the configuration values and make sure they match your local setup.

The default demonstration configuration is intended to use mock AI and simulated integrations. Check `.env.example` and the application configuration for the exact supported environment variables.

**Never commit API keys, passwords, tokens, or other secrets to GitHub.**

---

## Database Setup

The application uses SQLite for the local development database.

### Recommended Windows configuration

In your `.env` file, use:

```env
DATABASE_URL=sqlite:///followup.db
```

This is the working database configuration for the current Windows setup.

### Why this configuration matters

Flask-SQLAlchemy resolves a relative SQLite database path against Flask's instance directory. Therefore, using:

```env
DATABASE_URL=sqlite:///instance/followup.db
```

can cause the application to look for a nested `instance` directory, depending on the application's configuration.

For this project, use:

```env
DATABASE_URL=sqlite:///followup.db
```

Save `.env` after changing the setting.

### Initialise the database and seed demo data

From the directory containing `run.py`, run:

```powershell
python -m flask --app run seed
```

This invokes the project's `seed` command to prepare the demonstration data.

If the command completes successfully, continue to the next section.

**Do not delete existing database files to fix a database-path error.** Check the configured path first so that existing data is preserved.

---

## Running the Application

Make sure that:

- Your virtual environment is activated.
- Dependencies have been installed.
- `.env` is configured.
- The database initialisation and seed command has completed successfully.

Start the application with:

```powershell
python -m flask --app run run
```

Read the terminal output for the local address provided by Flask, then open that address in your browser.

Keep the terminal running while using the application.

To stop the development server, press:

```text
Ctrl+C
```

---

## Demo Accounts

Use the fictional demo accounts specified in the project configuration or the team's demonstration instructions.

If the usernames and passwords are not documented in this README, check the current application configuration or ask the team for the correct demo credentials.

Do not use real personal credentials for demonstration purposes.

---

## Running Tests

The repository includes a `tests/` directory for automated tests.

Run the test suite with:

```powershell
python -m pytest
```

Review the output to identify passed tests and any failures.

If a test fails, read the error message and traceback before changing the application code.

### Evaluation resources

The `eval/` directory contains evaluation-related resources.

Refer to the files in that directory and the GitHub workflow configuration for the evaluation commands and criteria used by the project.

---

## Docker Setup

Docker is an alternative way to run the application if Docker Desktop and the project's container configuration are available.

From the directory containing `docker-compose.yml`, run:

```powershell
docker compose up --build
```

Wait for the containers to start and check the terminal output for errors and the application URL.

To stop the containers, press `Ctrl+C`.

If the containers were started in detached mode, stop them with:

```powershell
docker compose down
```

Follow the project's Docker configuration for any additional environment variables or database requirements.

---

## Troubleshooting

### 1. `requirements.txt` not found

**Error:**

```text
ERROR: Could not open requirements file:
[Errno 2] No such file or directory: 'requirements.txt'
```

**Cause:** The terminal is in a directory that does not contain `requirements.txt`.

**Solution:**

Check the current directory:

```powershell
ls
```

Navigate into the project directory containing both `requirements.txt` and `run.py`.

Then retry:

```powershell
python -m pip install -r requirements.txt
```

Do not run the installation command from the parent folder unless `requirements.txt` is actually located there.

### 2. `sqlite3.OperationalError: unable to open database file`

**Error:**

```text
sqlite3.OperationalError: unable to open database file
```

This error may occur when Flask-SQLAlchemy attempts to create database tables before the `seed` command starts.

**Cause:** The database URL may point to a location that does not exist or cannot be accessed.

**Solution for this project:**

1. Open `.env`:

   ```powershell
   notepad .env
   ```

2. Check the database URL. Use the working configuration:

   ```env
   DATABASE_URL=sqlite:///followup.db
   ```

3. Save the file and close Notepad.

4. Confirm that your terminal is in the directory containing `run.py`.

5. Run the seed command again:

   ```powershell
   python -m flask --app run seed
   ```

6. If the error continues, inspect `app/config.py` to confirm how `BASE_DIR`, Flask's instance directory, and `SQLALCHEMY_DATABASE_URI` are configured.

**Important:** Do not delete the database or recreate the project just to resolve this error. Verify the database path first.

### 3. PowerShell cannot activate the virtual environment

If PowerShell blocks the activation script, read the error message carefully and follow the approved Python setup instructions for your environment.

You can also invoke the environment's Python executable directly, if it exists:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Adjust the path if `.venv` is located in the parent directory.

### 4. Flask cannot find the application

If Flask cannot import `run`, verify that the terminal is in the directory containing `run.py`.

Check:

```powershell
ls
```

Then retry:

```powershell
python -m flask --app run run
```

### 5. Dependency installation errors

If installation fails:

1. Confirm that the virtual environment is activated.
2. Check the first actual error in the terminal output.
3. Confirm that the correct Python interpreter is being used.
4. Check the package requirements in `requirements.txt`.
5. Avoid changing dependency versions without checking compatibility.

### 6. General debugging checklist

Before requesting help, collect the following information:

```powershell
python --version
python -m pip --version
python -m flask --version
```

Also check:

```powershell
ls
```

Share the relevant error message and traceback, but remove passwords, API keys, tokens, and other sensitive values before sharing logs.

---

## Responsible AI and Security

FollowUp AI is designed to demonstrate responsible use of AI in follow-up workflows.

The project should follow these principles:

- **Human oversight:** Important actions require appropriate human review.
- **Transparency:** AI suggestions should not be presented as guaranteed facts.
- **Traceability:** Record relevant workflow actions and decisions.
- **Privacy:** Use fictional data in demos and avoid exposing personal information.
- **Credential protection:** Keep secrets out of source control.
- **Honest demonstrations:** Clearly distinguish simulated integrations from real external actions.
- **Verification:** Review AI-generated content before acting on it.

The application should not be treated as a substitute for human judgement.

---

## Team Contributions

**Team:** IIP Team 34

The team is responsible for developing, testing, documenting, and demonstrating FollowUp AI as part of the SCCCI × NYP AI Innovation Challenge 26S2.

Update this section with the team's agreed member names and specific responsibilities before the final submission.

| Team responsibility | Description |
|---|---|
| Application development | Implement and maintain application features |
| AI workflow | Develop and evaluate AI-assisted follow-up behaviour |
| Testing and evaluation | Verify application behaviour and review evaluation results |
| Documentation | Maintain setup instructions and project documentation |
| Demonstration | Prepare the demo workflow and communicate the project's responsible AI approach |

Replace or refine these descriptions to reflect the actual allocation of work within the team.

---

## Future Improvements

Potential future improvements include:

- Improving the quality and consistency of AI-generated suggestions.
- Expanding automated test coverage.
- Strengthening validation and error handling.
- Improving traceability and audit information.
- Enhancing the user interface and accessibility.
- Evaluating AI responses against documented criteria.
- Adding real integrations only when authentication, permissions, and safeguards are properly implemented.

These are potential improvements, not claims that the features are already implemented.

---

## 8. Demo Accounts

Use the following credentials to explore the application locally.

| Role | Email | Password |
|:---|:---|:---|
| 👤 Staff | `priya@demo.local` | `demo1234` |
| 👤 Staff | `marcus@demo.local` | `demo1234` |
| 🛡️ Manager | `morgan@demo.local` | `demo1234` |

> **Note:** These accounts are intended for local development and demonstration only. Do not use demo credentials in production or expose them in a public deployment.

## Development Notes

To keep the project easy for new contributors to set up:

- Update this README whenever setup commands change.
- Keep `.env.example` aligned with the configuration expected by the application.
- Document new environment variables.
- Keep demo instructions consistent with the current code.
- Record known issues and their verified solutions.
- Never commit secrets or sensitive local data.

---

**FollowUp AI — IIP Team 34**

*AI proposes. A human decides. Every step leaves evidence.*

