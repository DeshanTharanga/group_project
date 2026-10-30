# MediLink asynchronous backend

FastAPI + SQLAlchemy/asyncpg + PostgreSQL, with Redis request protection and Celery workers.
The supplied **MediLink Developer Guide v1.0** defines 124 operations across 12 screen workflows.
REST endpoints live under `/api/v1`; the two limited FHIR projections live under `/fhir/r4`.
Interactive documentation: `http://localhost:8000/docs`.

## Run on Windows with Docker Desktop

1. Copy `.env.example` to `.env`.
2. Set `DB_NAME=medilink`, `DB_USER=postgres`, a strong `DB_PASSWORD`, and your `FIREBASE_PROJECT_ID`.
3. Set `FIREBASE_CREDENTIALS_FILE` to your Firebase Admin service-account JSON file
   (for example `C:/secrets/medilink-firebase.json`). Keep it outside this repository.
4. Run:

```bash
docker compose up --build -d
docker compose logs -f api worker beat
```

Compose starts PostgreSQL, Redis, a one-shot migration, the API, a worker, and one Beat scheduler.
Database/Redis ports remain private; the API binds to `127.0.0.1:8000`.
API and worker share a private upload volume. Containers run as an unprivileged application user.
Never use `docker compose down -v` when you need to retain the database and uploaded files.

The frontend signs users in through Firebase and sends its ID token as `Authorization: Bearer …`.
The backend verifies it with Firebase Admin, including revocation, and loads current local privileges.
There is no development token bypass. Set `CORS_ORIGINS` to your explicit frontend origin.

## First account and profiles

Call `POST /api/v1/me/onboard` using a real Firebase ID token. Public roles are only patient,
doctor, pharmacist and lab staff. Requesting a professional role does not approve it.
Patient onboarding initially returns `patient_profile: null`: finish it with
`PATCH /api/v1/me/patient-profile`, including **both** `date_of_birth` and `sex` on first creation.
The server never invents a birth date to satisfy the ER constraint.

An operator can bootstrap the first Super Admin **after that identity has onboarded**:

```bash
docker compose exec api python -m app.database.bootstrap_super_admin --firebase-uid YOUR_VERIFIED_FIREBASE_UID
```

Admin-role and integration-key operations require a Firebase MFA sign-in from the last ten minutes.
The bootstrap is an operator command, not a public endpoint. Audit access for ordinary Admins also
requires the Firebase custom claim `medilink_permissions: ["audit:read"]`, set by your trusted operator.

## Architecture

- **Routers** parse typed requests and select response models.
- **Services** enforce ownership, current consent, verification, source and lifecycle rules.
- **Repositories** execute authorized async queries using a request-scoped `AsyncSession`.
- **PostgreSQL** owns clinical state, audit history, idempotency records and durable job intent.
- **Redis** applies atomic request limits and brokers Celery messages. It never authorizes clinical access.
- **Celery** enters async work through a synchronous task wrapper, using a fresh async engine per run.

No migrations run during API startup. Schema changes use Alembic. Mutation responses are validated
and committed alongside their audit/idempotency records before the route returns.
Protected requests recheck live consent and organization membership; they do not use cached permissions.

## Background work

Beat checks durable queued jobs every ten seconds and medication reminders every minute.
A request saves its `job_runs` intent in its database transaction. Workers poll committed intent,
so a broker failure between a database commit and task publication does not lose the work.
Unique occurrence and notification keys prevent repeated delivery from duplicating records.

Schedules support fixed local times in IANA timezones, including `Asia/Colombo`. PRN items cannot
be scheduled. Spring-forward nonexistent times are skipped; a repeated fall-back time fires once.
The generator backfills at most the preceding 24 hours and generates the next 48 hours.
Alerts contain generic text rather than medicine details. Taken/Skipped is patient-reported;
corrections append a chain and adherence counts the latest response only.

Printed-text OCR uses Tesseract/Poppler in the image, or a text layer in a PDF. It returns untrusted
`raw_text` for human review. It does not infer medication instructions or recognize handwriting.
A separate review action creates a patient-source draft, followed by explicit patient confirmation.
Failures retain the job with a safe error code; retries are bounded.

## Tests and development

Python 3.13 is the deployment target. The lockfiles were resolved with Python 3.12; CI exercises 3.13.
For local development, use a virtual environment and install the complete development lock:

```bash
python -m pip install -r requirements-dev.lock
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Set `GOOGLE_APPLICATION_CREDENTIALS` for a process running outside Docker. In separate terminals:

```bash
python -m celery -A app.workers.celery_app:celery_app worker --loglevel=INFO
python -m celery -A app.workers.celery_app:celery_app beat --loglevel=INFO
```

Use the Docker worker on Windows. A local `--pool=solo` worker is suitable only for development.
Stop the API, worker and Beat independently when you run them in separate terminals.

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

PostgreSQL integration tests require **a disposable, migrated database** through
`TEST_DATABASE_URL=postgresql+asyncpg://…/medilink_test`. Redis integration tests use
`TEST_REDIS_URL=redis://localhost:6379/15`. Without these, service integration tests skip explicitly.
The GitHub Actions workflow provides PostgreSQL and Redis and runs migrations and tests.
See [implementation notes](docs/implementation.md) for alignment decisions and verification limits.
