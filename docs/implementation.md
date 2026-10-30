# Implementation and review notes

## Sources and contract

The supplied `MediLink_Developer_Guide.html` (v1.0, 27 October 2026) is the interface source;
`er-diagram.html` is the structural database source. `contract.json` records the extracted
124 operations, fields, response projections, status codes and business-rule descriptions.
The request/response classes and routes are static Python, not runtime-generated CRUD endpoints.
There are no generic object update endpoints. The running `/openapi.json` describes the executable API.

Models cover the 45 ER tables, including foreign keys, check constraints and ordinary/unique indexes.
The ER export names enum types but does not provide their complete label sets. The initial enum
labels combine labels explicitly used in ER defaults/constraints with the developer guide's workflows.
**Compare these against the original approved SQL before applying this baseline to an existing system.**
The immutable `0001_baseline.sql` is a fresh-database migration, not an upgrade that rewrites existing
clinical data. Existing installations must be backed up and reconciled with the baseline before any
Alembic stamp. Do not stamp a database merely to bypass a migration conflict.

## Explicit alignment decisions

| Difference or extension | Implementation |
| --- | --- |
| Onboarding has no birth date, but patient profiles require one | Keep the profile absent until the patient submits both required demographic fields. |
| ER sex constraint permits only female/male; guide lists five values | Baseline constraint permits female, male, intersex, another and prefer_not_to_say. |
| ER omits partial-index predicates | Use an active-only template-name index; keep deduplication indexes conservatively unique. |
| Multiple concurrent medication responses/corrections | Add one initial-response index and one successor per correction. |
| Multiple simultaneous schedules for one medicine item | Permit only one active/paused schedule; replacements retain the old schedule and increment version. |
| Clinical/report correction branches | Permit one successor per superseded record, preserving the whole chain. |
| Printed-text OCR output | Add optional `raw_text` to the extracted-fields response. No medicine values are guessed. |
| Discarding drafts versus retained OCR/evidence links | DELETE draft soft-cancels the retained draft and never deletes original evidence. |
| One-time credentials and claim/request tokens | Persist only hashes; plaintext appears only in its creation response and is not stored in an idempotency replay body. |
| Backup operation endpoints are read-only in the contract | Return actual retained backup status; no fabricated successful backups or automatic destructive restore job. |

## Transaction and access boundaries

The API owns one `AsyncSession` per request. Domain methods flush, but do not commit or publish
broker messages. The common invocation boundary validates the authorized response projection before
committing clinical changes, audit and replay records. Database constraints back the application rules.
Actor-scoped advisory locks serialize mutations, and row locks protect grants, claims, request
consumption, prescription items, response chains and retained versions.

Mandatory `Idempotency-Key` routes use PostgreSQL advisory transaction locks and retained records
scoped by actor, operation, URL and key. The digest includes the validated payload and uploaded
content hash. A changed payload returns 409. A replay rechecks current access rather than returning
clinical data after consent/verification/organization access has disappeared. One-time secret creation
uses fresh opaque secrets and avoids caching plaintext. Reads are never cached as replay responses.

Dispensing rechecks confirmed share, claimant, pharmacy, active doctor source, units and net remaining
quantity while holding prescription/item locks. Reversals append a whole-event inverse once;
patient-source confirmation and doctor review never permit dispensing. A replacement prescription
supersedes the prior doctor order only after explicit issue.

Files are detected from content, bounded to 10 MiB and stored by server-generated keys outside public
paths. Download authorization follows the parent record, or applicant/reviewer verification evidence.
Failed request transactions clean up files created by that request. A hard process/host failure can
still leave an orphan file; an operator should reconcile unused storage keys when maintaining backups.
Production malware scanning and remote/object storage are separate deployment extensions.

Human authentication uses Firebase Admin with revoked-token checks. Public onboarding cannot grant
admin privileges or professional approval. Every clinical request uses local current state. Admins
have operational access, not implicit patient-record access. Privileged role/key actions require recent
Firebase MFA. Rate limits use Redis Lua and fail with a safe 503 when protection is unavailable.

## Worker behavior and limits

Redis brokers only fixed periodic task names. Clinical payloads, credentials and medicine instructions
are not task arguments and are not saved in a Celery result backend. Durable `job_runs` intents are
committed with the originating business operation and drained under database locks.
Celery's normal synchronous task entry points call async code with a new `NullPool` engine that is
disposed before the loop closes. Database objects and request sessions are never passed to workers.
Late acknowledgment/redelivery is safe because occurrences, notifications and queued jobs are deduped.
A crash before the worker transaction commits leaves the job queued for another pass.

The periodic worker also expires grants/share/upload tokens, removes expired idempotency bodies, and creates deduplicated vaccination-date alerts from recorded next-dose dates. It never infers a next dose.

Only one Beat service should be deployed. Advisory locks also prevent overlapping periodic scans.
Reminders are in-app notifications while local services are running; they are not push notifications,
SMS delivery guarantees or clinical monitoring. The configured 24-hour backfill intentionally avoids
flooding a patient after long downtime; adherence cannot count occurrences never generated while off.
Printed-text OCR uses bounded pages, subprocess timeouts and a human review step. Tesseract availability
and real Firebase credentials must be verified in the deployment environment.

## Verification

The local suite covers route and response contracts, error envelopes, strict input handling, source
spoof rejection, unit validation, file detection and DST/local-time calculations. PostgreSQL integration
tests cover consent revocation, clinical isolation from admins, concurrent overfill protection,
idempotency replay, retained reversals, patient-source sharing denial, reminder deduplication,
latest-response adherence and single-use report publication. Redis integration verifies atomic limits.
CI runs these against PostgreSQL and Redis, and checks Alembic migration and Ruff formatting.

Live Firebase sign-in/MFA, Docker image startup, OCR system binaries, frontend workflows and backup/
restore procedures require deployment verification; unit checks do not establish production readiness.
