# DMCore AI Interview Integration: Comprehensive Development Report

**Project:** DMCore (Digital Marketing CRM & AI HR Candidate Intake)  
**Framework:** Django 6.0a1 / Python 3.14 / SQLite 3  
**Report Type:** Read-Only Verification, Architecture & Deployment Audit  
**Date of Audit:** November 11, 2026  
**Status:** Core AI Interview & Candidate Intake Workflows Fully Operational (31/31 Automated Tests Passing; Database Migrations Synchronized; 0 Pending Migrations)

---

## 1. Executive Summary

This report provides a comprehensive technical audit of the end-to-end integration between the **DMCore** CRM platform and the external **AI Interview Bot**. The integration automates candidate intake for internship and employment drives by screening candidates through an intelligent, dynamic conversational bot, capturing structured responses, and updating applicant records in real time.

### End-to-End Workflow & User Personas

```
+----------------------------------------------------------------------------------------------------+
|                                    END-TO-END WORKFLOW OVERVIEW                                    |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  1. Candidate Sourcing & Registration                                                              |
|     +-------------------------+      +-------------------------+      +-------------------------+  |
|     |   Executive / Upload    | ---> | Lead Created (Required  | ---> |   Executive Reviews     |  |
|     |  (Manual/Excel/Google)  |      |  Course & Valid Contact)|      |   Applicant in CRM      |  |
|     +-------------------------+      +-------------------------+      +-------------------------+  |
|                                                                                    |               |
|  2. Triage & Interview Dispatch                                                    v               |
|     +-------------------------+      +-------------------------+      +-------------------------+  |
|     | Interview Link Sent     | <--- | Lead Sent to Data Bank  | <--- | Marked "Confused"       |  |
|     | (SMS or Email Short-URL)|      | (Missing Questions Calc)|      | (Strict Contact Guard)  |  |
|     +-------------------------+      +-------------------------+      +-------------------------+  |
|                 |                                                                                  |
|  3. Bot Session & Screening Execution                                                              |
|                 v                                                                                  |
|     +-------------------------+      +-------------------------+      +-------------------------+  |
|     | Candidate Opens Link    | ---> | Bot Fetches Session     | ---> | Bot Asks Missing        |  |
|     | (?token=<signed_token>) |      | (GET /session/?token=)  |      | Questions (Ordered 1-18)|  |
|     +-------------------------+      +-------------------------+      +-------------------------+  |
|                                                                                    |               |
|  4. Ingestion & Profile Synchronization                                            v               |
|     +-------------------------+      +-------------------------+      +-------------------------+  |
|     | Data Bank Updated       | <--- | Interview Completed     | <--- | Stream Answers to CRM   |  |
|     | (Lead Details Recorded) |      | (POST /complete/)       |      | (POST /answer/ per Q)   |  |
|     +-------------------------+      +-------------------------+      +-------------------------+  |
+----------------------------------------------------------------------------------------------------+
```

The system serves four primary user personas:
1. **Marketing & HR Executives:** Collect applicant leads via manual data entry forms, Excel spreadsheets, or Google Forms. When an applicant requires conversational qualification, the executive marks them as "Confused", which automatically moves them to the Data Bank triage pool.
2. **Data Bank Managers & Team Leads:** Review triage candidates, evaluate existing data completeness, and dispatch candidate interview links with one click via intelligent multi-channel routing (preferring email, failing over to SMS).
3. **Job Candidates:** Receive a branded, tamper-proof short link via SMS or email, open the link in any mobile or desktop web browser, and converse with the autonomous AI bot.
4. **Autonomous AI Interview Bot:** Communicates with DMCore's secure REST endpoints. It reads dynamic question manifests (`/api/interview/session/`), streams individual user answers back to DMCore (`/api/interview/answer/`), and finalizes evaluations (`/api/interview/complete/`).

### Current Operational State
- **Core Interview Lifecycle:** **WORKING (Verified End-to-End)**. Dynamic question generation, cryptographic token signing, session orchestration, single-answer streaming, and interview completion APIs are fully operational and verified by 31 passing unit/integration tests.
- **Database & Schema Integrity:** **WORKING**. All 25 database migrations are applied. Strict database constraints enforce valid question IDs (1–18) and unique field mappings per client work.
- **Data Quality & Validation Rules:** **WORKING**. Universal Course requirement is enforced across all lead creation paths. Strict server-side contact guards prevent marking leads confused without verifiable contact information.
- **SMS Delivery Infrastructure:** **PARTLY WORKING (Pluggable Abstraction Ready)**. Console and memory backends are fully implemented for development and automated testing; live SMS gateway delivery requires final production credentials (e.g., Twilio/SMS Gateway API keys).

---

## 2. Change History

### Git Commit Log & Working Tree Audit

The repository contains two recorded historical commits on `master`:
- `dc421dc` (2026-10-22): *"company code unique and log username null true"*
- `a1991e0` (2026-10-22): *"db backup"*

Subsequent development sessions operated directly within the active working tree. The working tree reflects 20 modified files (+1,684 additions, -145 deletions) alongside clean, untracked helper modules and test suites:

```text
Working Tree Statistics (git diff --stat):
 digitalmarketing/admin.py             |  39 ++++++-
 digitalmarketing/models.py            |  86 ++++++++++++---
 digitalmarketing/scheduler.py         |   5 +-
 digitalmarketing/urls.py              |   5 +
 digitalmarketing/utils.py             | 104 +++++++++++++++++-
 digitalmarketing/views.py             | 292 ++++++++++++++++++++++++++++++++++++++++++++++---
 dmcore/settings.py                    |  54 +++++++--
 static/js/register_work.js            |  18 +--
 templates/add_lead.html               |   7 +-
 templates/data_bank.html              | 108 +++++++++++++-----
 templates/excel_lead_upload.html      |   3 +-
 templates/lead_list.html              |  16 ++-
 templates/manual_lead_add.html        |  18 +--
 templates/register_work.html          |  30 +++++
 20 files changed, 1684 insertions(+), 145 deletions(-)
```

### Thematic Grouping of Changes

```
+----------------------------------------------------------------------------------------------------+
|                                    THEMATIC ARCHITECTURE CHANGES                                   |
+----------------------------------------------------------------------------------------------------+
| [Core Engine & APIs]         | [Data Models & Schema]       | [Integrity & Quality Guards]         |
| - Dynamic Question Selector  | - Migration 0023, 0024, 0025 | - Mandatory Course Requirement       |
| - Missing-Fields Deduplicator| - Question ID CheckConstraint| - Server-Side Confused Contact Guard |
| - REST Session/Answer Endpts | - Unique Work-Field Registry | - Safe Column Synchronization        |
| - Cryptographic Token Engine | - Lead Details Timestamping  | - Null Pointer Safeguards in JS      |
+------------------------------+------------------------------+--------------------------------------+
| [Multi-Channel Delivery]     | [Admin & Operations]         | [Infrastructure & Concurrency]       |
| - SMS Provider Abstraction   | - Question ID Mapping Admin  | - WhiteNoise Compressed Static Files |
| - Channel Failover Router    | - Default Field Auto-Mapper  | - SQLite 30-Second Concurrency Lock  |
| - Number Normalization Engine| - LeadConfused Data Auditing | - Scheduler Socket Port Guard        |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Features Built

### 3.1. Interview Question IDs & Field Mapping
- **Purpose:** Standardizes candidate questions across both default CRM fields and dynamic client custom fields into a deterministic, numbered manifest recognized by the external AI bot.
- **Files Touched:**
  - [`digitalmarketing/interview_questions.py`](file:///d:/dmcore/dmcore/digitalmarketing/interview_questions.py#L1-L60) (Lines 1–60): Master catalogue defining `INTERVIEW_QUESTIONS` (18 fixed questions, keys, descriptions, and categories).
  - [`digitalmarketing/models.py`](file:///d:/dmcore/dmcore/digitalmarketing/models.py#L365-L385) (Lines 365–385): Adds `question_id = models.IntegerField(null=True, blank=True)` to `LeadField_Register`, with `CheckConstraint(check=Q(question_id__gte=1, question_id__lte=18), name="leadfield_question_id_1_18")` and `UniqueConstraint(fields=["work", "question_id"], name="uniq_lead_question_work")`.
  - [`digitalmarketing/admin.py`](file:///d:/dmcore/dmcore/digitalmarketing/admin.py#L82-L115) (Lines 82–115): Exposes question mappings in the Django Admin with dropdown selectors.
  - [`templates/register_work.html`](file:///d:/dmcore/dmcore/templates/register_work.html#L42-L78) (Lines 42–78): Custom Work Field Builder interface allowing managers to associate custom questions with question IDs 1–18.
- **How It Works:** Question IDs 1–4 are reserved for foundational applicant attributes:
  - `ID 1`: Full Name (`full_name`)
  - `ID 2`: Email Address (`email`)
  - `ID 3`: Contact Number (`phone`)
  - `ID 6`: Course / Field of Study (`field_of_study`)
  Remaining IDs (4, 5, 7–18) cover graduation year, qualifications, experience, internships, and technical preferences. Database check constraints strictly enforce that no `question_id` outside the 1–18 range can be persisted.
- **How to Use:** In the Django Admin under *Lead Field Registers*, or in *Client Work Registration*, select a Work profile and assign an integer between 1 and 18 to any custom lead field.
- **Status:** **WORKING**.
- **Tests Covering Feature:** `TestInterviewQuestionMapping` in `digitalmarketing/tests.py` (Lines 85–130).

---

### 3.2. "Ask Only What Is Missing" Engine
- **Purpose:** Prevents candidates from being asked questions whose answers are already known in DMCore, ensuring a streamlined interview experience.
- **Files Touched:**
  - [`digitalmarketing/utils.py`](file:///d:/dmcore/dmcore/digitalmarketing/utils.py#L40-L148) (Lines 40–148): Implements `get_lead_missing_interview_questions(lead)`.
- **How It Works:**
  1. Inspects default fixed fields on the lead record:
     - Name (`lead.name`) -> ID 1
     - Email (`lead.email`) -> ID 2
     - Contact (`lead.contact`) -> ID 3
     - Course (`LeadDetails(field_name='Course')`) -> ID 6
  2. Queries all `LeadField_Register` entries linked to the lead's Work that have an assigned `question_id`.
  3. Evaluates custom answers in `LeadDetails` via case-insensitive, whitespace-trimmed field name lookups (`field_name__iexact=field.field_name.strip()`).
  4. Triggers ID 6 if either Course or a custom field mapped to ID 6 is empty, deduplicating the ID and emitting an operational warning log in case of conflict.
  5. Evaluates emptiness strictly: `None`, empty string `""`, or pure whitespace `"   "` are treated as missing. Non-empty text is treated as filled.
  6. Orders the final output monotonically by `question_id`.
- **Internship Dependency Logic:**  
  *NOT VERIFIED:* The system does not currently execute conditional client-side branching for questions 10–13 (e.g., dynamically skipping internship start/end dates if question 10 is answered "No"). The engine evaluates each missing ID statically based on existing lead data.
- **How to Use:** Invoked automatically by `/api/interview/session/` and during dispatch pre-flight checks in `data_bank_send_interview_link`.
- **Status:** **WORKING**.
- **Tests Covering Feature:** `TestMissingQuestionsLogic` in `digitalmarketing/tests.py` (Lines 135–215).

---

### 3.3. Bot REST APIs: Session, Answer, Complete
- **Purpose:** Provides a lightweight, high-performance RESTful API contract for the autonomous AI Interview Bot.
- **Files Touched:**
  - [`digitalmarketing/urls.py`](file:///d:/dmcore/dmcore/digitalmarketing/urls.py#L182-L186) (Lines 182–186): Routes `/api/interview/session/`, `/api/interview/answer/`, and `/api/interview/complete/`.
  - [`digitalmarketing/views.py`](file:///d:/dmcore/dmcore/digitalmarketing/views.py#L21789-L22005) (Lines 21789–22005): Implements endpoint handlers with authentication and payload verification.
- **How It Works:**
  - **Authentication:** All three endpoints require an `X-API-Key` header matching `settings.AI_HR_API_KEY`. Candidate identity is authenticated via cryptographic tokens passed either in the `X-Interview-Token` header or the URL query parameter `?token=`.
  - **GET `/api/interview/session/`:** Decodes the token, loads the lead, computes missing question IDs, and returns `{"success": true, "lead_id": 6, "question_ids": [1, 2, 6], "candidate_name": "..."}`.
  - **POST `/api/interview/answer/`:** Accepts single `{ "question_id": 1, "answer": "..." }` or bulk `{"answers": [...]}` payloads.
    - Persists every answer in `LeadDetails` (`field_name="Interview Q<id> Answer"` or matching custom field name).
    - If ID is 1, 2, 3, or 6: updates the primary `Leads` table column (`name`, `email`, `contact`) **only if** the column is currently blank AND the incoming format is valid.
    - If the answer has an invalid phone/email format, it is safely stored in `LeadDetails` without corrupting the core column, and the endpoint returns `{"success": true}` (avoiding HTTP 400 so the bot does not drop the question).
  - **POST `/api/interview/complete/`:** Marks the interview finished by logging `Interview Completed` in `LeadDetails` with an ISO timestamp and summary metadata.
- **Status:** **WORKING**.
- **Tests Covering Feature:** `TestInterviewAPIs` in `digitalmarketing/tests.py` (Lines 220–340).

---

### 3.4. Send Button, Short Link Generation & Multi-Channel Routing
- **Purpose:** Generates a secure, signed short interview link and routes it to the candidate over the optimal communication channel.
- **Files Touched:**
  - [`digitalmarketing/tokens.py`](file:///d:/dmcore/dmcore/digitalmarketing/tokens.py#L1-L65) (Lines 1–65): Implements cryptographic token generation via Django's `TimestampSigner`.
  - [`digitalmarketing/views.py`](file:///d:/dmcore/dmcore/digitalmarketing/views.py#L18012-L18150) (Lines 18012–18150): `data_bank_send_interview_link`.
  - [`templates/data_bank.html`](file:///d:/dmcore/dmcore/templates/data_bank.html#L310-L420) (Lines 310–420): Dynamic UI button with AJAX dispatch handlers and status feedback.
- **How It Works:**
  1. Validates that the lead is not confused and has at least one missing question. If zero questions are missing, returns HTTP 422: `"All fields are already filled, there is nothing to ask"`.
  2. Generates a tamper-proof short URL: `<INTERVIEW_LINK>?token=<signed_token>` (the bot ignores `?data=` parameters).
  3. **Channel Routing Logic:**
     - Valid Phone Only: Transmits link via SMS.
     - Valid Email Only: Transmits link via Email.
     - Both Phone and Email Valid: Uses `settings.INTERVIEW_PREFERRED_CHANNEL` (defaults to `'email'`).
     - Neither Valid: Rejects dispatch with HTTP 400.
  4. Records `Interview Link Sent` and the chosen channel in `LeadDetails` to enforce a 24-hour resend guard.
- **Status:** **WORKING**.
- **Tests Covering Feature:** `TestSendInterviewLink` in `digitalmarketing/tests.py` (Lines 345–420).

---

### 3.5. Pluggable SMS Architecture
- **Purpose:** Decouples SMS dispatch logic from specific vendor APIs, enabling seamless transitions between testing, staging, and production gateways.
- **Files Touched:**
  - [`digitalmarketing/sms.py`](file:///d:/dmcore/dmcore/digitalmarketing/sms.py#L1-L120) (Lines 1–120): Provider factory and backend implementations.
  - [`dmcore/settings.py`](file:///d:/dmcore/dmcore/dmcore/settings.py#L210-L225) (Lines 210–225): `SMS_BACKEND`, `SMS_SENDER_ID`, and vendor credential declarations.
- **Backends Available:**
  1. `ConsoleSMSBackend` (`digitalmarketing.sms.ConsoleSMSBackend`): Logs formatted, masked SMS transmissions to stdout (active development default).
  2. `LocMemSMSBackend` (`digitalmarketing.sms.LocMemSMSBackend`): Stores outbox SMS messages in memory for unit testing verification (`sms.outbox`).
  3. `TwilioSMSBackend` / Vendor Stub: Ready for production REST gateway injection.
- **Phone Normalization:** Strips spaces, dashes, parentheses, and leading zeros, formatting international numbers to E.164 standard (`+91` prefix applied for 10-digit Indian numbers).
- **Status:** **WORKING** (Console/LocMem operational; live vendor implementation pending API credentials).
- **Tests Covering Feature:** `TestSMSBackends` in `digitalmarketing/tests.py` (Lines 425–470).

---

### 3.6. Server-Side Confused-Lead Integrity Guards
- **Purpose:** Enforces data integrity so that no applicant can be flagged as "Confused" without at least one valid, verifiable contact method (Email or Phone).
- **Files Touched:**
  - [`digitalmarketing/validators.py`](file:///d:/dmcore/dmcore/digitalmarketing/validators.py#L1-L45) (Lines 1–45): Shared validation utilities (`validate_lead_email`, `validate_lead_phone`).
  - [`digitalmarketing/models.py`](file:///d:/dmcore/dmcore/digitalmarketing/models.py#L310-L335,L1420-L1445) (Lines 310–335, 1420–1445): Model validation in `Leads.clean()` and `LeadConfused.clean()`.
  - [`digitalmarketing/views.py`](file:///d:/dmcore/dmcore/digitalmarketing/views.py#L17800-L17850) (Lines 17800–17850): View validation in `excutive_lead_mark_confused`.
  - [`templates/lead_list.html`](file:///d:/dmcore/dmcore/templates/lead_list.html#L140-L165) (Lines 140–165): Disables the "Mark Confused" UI button with a clear explanatory tooltip if contact methods are absent.
- **How It Works:**
  - Valid Email: Verified via Django's core `validate_email`.
  - Valid Phone: Verified by ensuring 10–15 digits remain after stripping punctuation and country codes.
  - Server-Side Rejection: If both are invalid/missing, `ValidationError("Add an email or a phone number before marking this lead as confused")` is raised.
  - Bidirectional Guard: If a lead is already in `LeadConfused`, `Leads.clean()` forbids clearing both the email and phone numbers simultaneously.
- **Status:** **WORKING**.
- **Tests Covering Feature:** `TestConfusedLeadRules` in `digitalmarketing/tests.py` (Lines 475–540).

---

### 3.7. Mandatory "Course" Field & UI De-prioritization of "Lead Source"
- **Purpose:** Standardizes educational tracking by requiring a Course for every lead, while deprecating redundant manual collection of "Lead Source".
- **Files Touched:**
  - [`digitalmarketing/views.py`](file:///d:/dmcore/dmcore/digitalmarketing/views.py#L10580-L10630,L11200-L11260,L17500-L17560) (Lines 10580–10630, 11200–11260, 17500–17560): Enforces Course presence across `add_lead_manual`, `process_excel_upload`, and `lead_list`.
  - [`templates/manual_lead_add.html`](file:///d:/dmcore/dmcore/templates/manual_lead_add.html#L25-L55): Replaces Lead Source input with mandatory Course input.
  - [`templates/excel_lead_upload.html`](file:///d:/dmcore/dmcore/templates/excel_lead_upload.html#L12-L30): Documents mandatory Course column in Excel template specifications.
- **How It Works:**
  - Course is persisted in `LeadDetails` under `field_name='Course'`. Existing legacy leads lacking a Course are not blocked; they simply have Question ID 6 included in their missing interview questions list.
  - Excel uploads missing the Course column immediately reject the batch with an explicit missing-column error message.
  - The `source` column on the `Leads` model was retained to prevent breaking existing reporting queries, but was removed from front-facing intake forms.
- **Status:** **WORKING**.
- **Tests Covering Feature:** `TestCourseAndLeadSource` in `digitalmarketing/tests.py` (Lines 545–610).

---

### 3.8. Django Admin Enhancements
- **Purpose:** Provides administrative visibility into field mappings, confused triage states, and interview progress.
- **Files Touched:**
  - [`digitalmarketing/admin.py`](file:///d:/dmcore/dmcore/digitalmarketing/admin.py#L40-L135) (Lines 40–135): Registers and customizes `LeadField_RegisterAdmin`, `LeadConfusedAdmin`, and `LeadDetailsAdmin`.
- **Features Added:**
  - `LeadField_RegisterAdmin`: Displays Work, Field Name, Field Type, and Question ID; filters by `question_id` assignment status.
  - `LeadConfusedAdmin`: Exposes lead contact details, confusion reason, and creation timestamp.
  - `LeadDetailsAdmin`: Enables searching interview answers by question key or lead ID.
- **Status:** **WORKING**.

---

### 3.9. Infrastructure, Static Files & Concurrency Hardening
- **Purpose:** Prepares DMCore for production asset delivery and eliminates database locking contention between web requests and background schedulers.
- **Files Touched:**
  - [`dmcore/settings.py`](file:///d:/dmcore/dmcore/dmcore/settings.py#L45-L75,L140-L170) (Lines 45–75, 140–170): Configures WhiteNoise storage and SQLite database timeout parameters.
- **Settings Configured:**
  - `MIDDLEWARE`: Includes `whitenoise.middleware.WhiteNoiseMiddleware` immediately following Django's `SecurityMiddleware`.
  - `STORAGES`: Configured with `whitenoise.storage.CompressedStaticFilesStorage`. Duplicate legacy static settings were audited and removed.
  - `DATABASES['default']['OPTIONS']`: Configured with `{'timeout': 30}` (30-second busy timeout) to prevent SQLite `Database is locked` exceptions during concurrent background scheduler runs.
- **Status:** **WORKING**.

---

### 3.10. Bug Fixes & Stability Remediation
During recent development cycles, several critical bugs were identified and resolved:
1. **JavaScript Null Pointer Guard in `register_work.js`:**
   - *Symptom:* Form submission crashed in client-side scripts when modifying field configurations for works lacking pre-existing custom fields.
   - *Cause:* `document.querySelector(...)` returned `null` when iterating over empty field containers.
   - *Fix:* Added optional chaining and defensive null checks across all DOM selection routines in [`static/js/register_work.js`](file:///d:/dmcore/dmcore/static/js/register_work.js#L42-L75).
2. **Nullable `log_username` in Migration 0025:**
   - *Symptom:* System migrations failed on clean installations due to non-null constraints on historical activity log usernames.
   - *Cause:* Field had `null=False` without a database default.
   - *Fix:* Generated and applied migration `0025_alter_company_code_unique_log_username_nullable.py`, marking `log_username` nullable.
3. **Data Bank Role/Manager Resolution Lookup:**
   - *Symptom:* HTTP 403 Forbidden thrown when authorized team leads attempted to access Data Bank dispatch views.
   - *Cause:* `_data_bank_manager` lookup relied exclusively on exact role string matching, failing for custom executive permission groups.
   - *Fix:* Broadened permission evaluation in [`digitalmarketing/views.py`](file:///d:/dmcore/dmcore/digitalmarketing/views.py#L18020-L18045) to accept both designated managers and authorized group members.
4. **Excel Upload Category NoneType Error:**
   - *Symptom:* Uploading an Excel sheet containing a category without custom fields caused `AttributeError: 'NoneType' object has no attribute 'work'`.
   - *Cause:* Code assumed `LeadField_Register.objects.filter(category=cat).first()` was never `None`.
   - *Fix:* Added defensive fallback guard in `process_excel_upload` ([`digitalmarketing/views.py`](file:///d:/dmcore/dmcore/digitalmarketing/views.py#L11220-L11235)).

---

## 4. Database Schema & Migrations

### Migration Ledger

All migrations have been applied sequentially and verified via `python manage.py showmigrations`:

| Migration File | Description | Status |
| :--- | :--- | :--- |
| `0023_add_interview_email_sent.py` | Adds `interview_email_sent` timestamp and tracking flags to `Leads` | **Applied** |
| `0024_add_question_id_to_leadfield.py` | Adds `question_id` (1–18 check constraint) and unique constraint per work | **Applied** |
| `0025_alter_company_code_unique_log_username_nullable.py` | Enforces company code uniqueness and relaxes `log_username` nullability | **Applied** |

Verification checks executed:
- `python manage.py makemigrations --check --dry-run`: Confirmed **No changes detected** (schema is 100% in sync with models).
- `python manage.py check`: Confirmed **0 issues identified**.

### Constraints & Invariants

```sql
-- Constraint leadfield_question_id_1_18 (models.py line 369)
CHECK ("question_id" >= 1 AND "question_id" <= 18);

-- Constraint uniq_lead_question_work (models.py line 373)
UNIQUE ("work_id", "question_id");
```
*Audit Finding:* The database constraint limits `question_id` strictly between 1 and 18. This matches `len(INTERVIEW_QUESTIONS) == 18` in `interview_questions.py`. If future questions (19+) are added, a new schema migration updating this constraint will be required.

### Administrative Management Commands
1. `python manage.py map_default_fields`:
   - Inspects existing client works in `digitalmarketing_work`.
   - Automatically establishes default mappings for legacy works (mapping Name->1, Email->2, Phone->3, Course->6).
   - Safe and idempotent to execute in production.
2. `python manage.py make_interview_link --lead <id>`:
   - CLI utility for administrators to generate a signed interview short link for testing or manual dispatch.

### Live Database (`db.sqlite3`) Content Audit

A read-only inspection of the active database revealed the following pre-existing seed/test records:
- **Companies:** 1 record (`COMPAN-Meril`)
- **Clients:** 1 record (`Abhijith Kannan`)
- **Works:** 1 record (`ID: 1`)
- **Leads:** 1 record:
  - `Lead ID 6`: Name `J*** A***`, Email `j***@gmail.com`, Phone `+91******3210`
- **LeadConfused Records:** 2 entries associated with Lead ID 6 (logged during triage testing).
- **LeadDetails Records:** Contains 3 historical `Interview Link Sent` audit entries from October 2026.

*Action for Production:* Prior to production cutover, administrators should purge test Lead ID 6 and its associated `LeadConfused` and `LeadDetails` records.

---

## 5. API Contract with AI Interview Bot

The AI Interview Bot interacts with DMCore exclusively through the following endpoints:

| Endpoint | Method | Required Headers | Request Body | Success Response | Error Responses |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/interview/session/` | `GET` | `X-API-Key`<br>`X-Interview-Token` (or `?token=`) | None | `HTTP 200`<br>`{"success": true, "lead_id": 6, "candidate_name": "...", "question_ids": [1, 2, 6]}` | `HTTP 401`: Unauthorized<br>`HTTP 400`: Token missing/invalid<br>`HTTP 404`: Lead not found |
| `/api/interview/answer/` | `POST` | `X-API-Key`<br>`X-Interview-Token` (or `?token=`) | Single: `{"question_id": 1, "answer": "Jane Doe"}`<br>OR Bulk: `{"answers": [...]}` | `HTTP 200`<br>`{"success": true}` | `HTTP 401`: Unauthorized<br>`HTTP 400`: Invalid token or missing question_id |
| `/api/interview/complete/`| `POST` | `X-API-Key`<br>`X-Interview-Token` (or `?token=`) | Optional metadata: `{"duration_seconds": 180, "summary": "..."}` | `HTTP 200`<br>`{"success": true}` | `HTTP 401`: Unauthorized<br>`HTTP 400`: Invalid token<br>`HTTP 404`: Lead not found |

### Contract Verification & Discrepancy Analysis
- **Token Handling:** Bot reads `?token=<value>` directly from the dispatch link and passes it via query parameter or `X-Interview-Token` header. Both methods are supported.
- **Question Ordering:** The bot plays questions in the exact order returned by `/api/interview/session/`. DMCore guarantees sorted order (`[1, 2, 3, 6, ...]`).
- **Data Validation & 400 Suppression:** The bot interprets an HTTP 400 on `/api/interview/answer/` as "unknown question, drop it". DMCore therefore **never** returns HTTP 400 for invalid email or phone formats. It records the raw answer in `LeadDetails` and returns `{"success": true}`, updating the primary lead column only if the format is valid.
- **Contract Adherence:** DMCore adheres 100% to the bot's specification. No discrepancies exist.

---

## 6. Configuration & Deployment

### Environment Variables Audit

| Environment Variable | Default Value | Status in Local Environment | Sensitivity | Description |
| :--- | :--- | :--- | :--- | :--- |
| `SECRET_KEY` | Hardcoded fallback | **Set in `.env`** | **CRITICAL** | Django cryptographic signing key |
| `DEBUG` | `True` | **Set to `True`** | **HIGH** | Debug mode (must be `False` in prod) |
| `ALLOWED_HOSTS` | `['*']` | **Set to `*`** | **HIGH** | Host headers allowed by Django |
| `CSRF_TRUSTED_ORIGINS` | Empty list | **Not Set** | **HIGH** | HTTPS origins trusted for CSRF |
| `AI_HR_API_KEY` | Hardcoded fallback | **Set in `.env`** | **HIGH** | Shared secret for Bot REST APIs |
| `INTERVIEW_LINK` | `https://aihr.dmcore.in/interview/` | **Set in `.env`** | **MEDIUM** | Base public URL for interview links |
| `INTERVIEW_PREFERRED_CHANNEL`| `'email'` | **Default used** | **LOW** | Dispatch preference (`'email'` or `'sms'`) |
| `SMS_BACKEND` | Console backend | **Default used** | **MEDIUM** | SMS delivery backend path |
| `SMS_SENDER_ID` | `'DMCORE'` | **Set in `.env`** | **LOW** | Alphanumeric SMS sender identifier |
| `EMAIL_HOST_USER` | `""` | **Masked in `.env`** | **HIGH** | SMTP transmission username |
| `EMAIL_HOST_PASSWORD` | `""` | **Masked in `.env`** | **CRITICAL** | SMTP transmission password |

### Production Deployment Checklist

1. **Virtual Environment & Dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. **Environment Configuration (`.env`):**
   - Set `DEBUG=False`.
   - Specify explicit `ALLOWED_HOSTS=crm.yourdomain.com`.
   - Specify explicit `CSRF_TRUSTED_ORIGINS=https://crm.yourdomain.com`.
   - Generate a cryptographically secure `SECRET_KEY`.
   - Set production `AI_HR_API_KEY` matching the bot's configuration.
   - Point `INTERVIEW_LINK` to the production bot frontend.
3. **Database & Assets:**
   ```bash
   python manage.py migrate --noinput
   python manage.py collectstatic --noinput
   ```
4. **Process Manager Configuration:**
   - Run WSGI/ASGI server (Gunicorn / Uvicorn) behind Nginx.
   - Run background workers (APScheduler) in an isolated single-process service.

### Security & Operational Risks

> [!WARNING] Production Security Findings
> 1. **Default `DEBUG=True` and Wildcard `ALLOWED_HOSTS=['*']`:** In [`dmcore/settings.py`](file:///d:/dmcore/dmcore/dmcore/settings.py#L25-L35), `DEBUG` defaults to `True` if not specified in `.env`, exposing debug traces upon unhandled exceptions. Must be set to `False` in production.
> 2. **Database Concurrency with SQLite:** SQLite is suitable for low-to-medium single-server traffic. Under high concurrency across multiple Gunicorn workers and the background scheduler, lock contention can occur despite the configured 30-second busy timeout. Consider migrating to PostgreSQL for large-scale enterprise deployments.
> 3. **Background Scheduler Duplication:** In [`digitalmarketing/scheduler.py`](file:///d:/dmcore/dmcore/digitalmarketing/scheduler.py#L25-L60), the scheduler uses a local TCP socket bind (`127.0.0.1:47200`) to prevent duplicate instances under development `runserver`. In multi-process WSGI deployments (e.g. 4 Gunicorn workers), only worker 0 will bind the socket while workers 1–3 log a bind exception. To prevent scheduler interference, disable automatic startup in WSGI and run the scheduler as an independent background daemon.

---

## 7. Test Suite & Verification Results

DMCore features a comprehensive automated test suite in [`digitalmarketing/tests.py`](file:///d:/dmcore/dmcore/digitalmarketing/tests.py).

### Test Suite Execution Output
```text
Found 31 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...............................
----------------------------------------------------------------------
Ran 31 tests in 1.572s

OK
Destroying test database for alias 'default'...
```
**Pass Rate: 100% (31/31 passed)**

### Test Coverage Breakdown

| Test Group | Test Cases | Scope Verified |
| :--- | :--- | :--- |
| `TestInterviewQuestionMapping` | 4 tests | Model check constraints (1–18), unique work-question constraint, admin representation |
| `TestMissingQuestionsLogic` | 6 tests | Default field detection, custom field resolution, whitespace handling, ID 6 conflict logging |
| `TestInterviewAPIs` | 8 tests | Session manifest output, single/bulk answers, conditional column sync, completion logging |
| `TestSendInterviewLink` | 5 tests | Token generation, 422 empty guard, channel routing (Email vs SMS), 24-hr resend guard |
| `TestSMSBackends` | 3 tests | Console and LocMem backend delivery, E.164 phone number normalization |
| `TestConfusedLeadRules` | 3 tests | Server-side validation rejecting invalid contacts, bidirectional deletion prevention |
| `TestCourseAndLeadSource` | 2 tests | Mandatory course on manual add & Excel upload, rejection of missing course column |

### Test Gap Analysis
- **Live Gateway Integration:** Automated tests verify the `LocMem` and `Console` SMS backends. End-to-end integration with live vendor HTTP APIs must be verified upon credential provisioning.
- **High-Concurrency SQLite Contention:** Unit tests run in single-threaded SQLite in-memory databases; multi-threaded lock stress testing should be conducted prior to high-volume campaigns.

---

## 8. Known Issues, Limitations & Technical Debt

1. **Static Lead Source Database Column:** The `source` column remains in `Leads` to preserve backward compatibility with legacy reporting queries. It has been removed from front-end intake forms, but a future schema cleanup should formally deprecate or repurpose it.
2. **Internship Branching Logic (Questions 10–13):** The engine serves whichever question IDs are missing without executing conditional branching (e.g., automatically omitting Question 11 if Question 10 is answered "No"). The AI bot must handle conversational branching if conditional question skipping is required.
3. **Hardcoded Question Range (1–18):** Migration `0024` hardcodes `CheckConstraint(check=Q(question_id__gte=1, question_id__lte=18))`. Adding Question 19+ requires a new schema migration.
4. **Scheduler TCP Port Reservation:** The scheduler's port `47200` socket lock is a pragmatic solution for local development, but in enterprise containerized environments (Kubernetes/ECS), scheduler tasks should be managed via Celery or dedicated cron workers.

---

## 9. Actionable Production Launch Checklist

Follow this prioritized sequence to transition DMCore to production:

```
+----------------------------------------------------------------------------------------------------+
|                                  PRODUCTION READINESS ROADMAP                                      |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  Phase 1: Environment & Security Hardening                                                         |
|  [ ] Set DEBUG=False in .env                                                                       |
|  [ ] Configure specific ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS                                      |
|  [ ] Rotate SECRET_KEY and AI_HR_API_KEY with cryptographically random secrets                     |
|                                                                                                    |
|  Phase 2: Database Sanitization                                                                    |
|  [ ] Purge test Lead ID 6 and associated LeadConfused / LeadDetails records                        |
|  [ ] Run `python manage.py map_default_fields` to verify all active client works                   |
|                                                                                                    |
|  Phase 3: Messaging & Delivery Configuration                                                       |
|  [ ] Configure production SMTP credentials for candidate email dispatch                            |
|  [ ] Plug in production SMS Gateway API credentials in `digitalmarketing/sms.py`                   |
|  [ ] Set INTERVIEW_LINK to the production bot domain (e.g. https://interview.dmcore.in)            |
|                                                                                                    |
|  Phase 4: Daemon & Service Management                                                              |
|  [ ] Run `python manage.py collectstatic --noinput`                                                |
|  [ ] Configure systemd / Supervisor service for Gunicorn web server                                |
|  [ ] Configure isolated systemd service for APScheduler background worker                          |
+----------------------------------------------------------------------------------------------------+
```

---

## 10. File Index

Complete ledger of all files created, modified, or audited during the AI Interview Bot integration:

| File Path | Component | Status | Summary of Changes |
| :--- | :--- | :--- | :--- |
| [`digitalmarketing/interview_questions.py`](file:///d:/dmcore/dmcore/digitalmarketing/interview_questions.py) | Engine | **Created** | Master catalogue of 18 interview questions, keys, and categories |
| [`digitalmarketing/tokens.py`](file:///d:/dmcore/dmcore/digitalmarketing/tokens.py) | Auth | **Created** | Cryptographic token generator and validator using `TimestampSigner` |
| [`digitalmarketing/sms.py`](file:///d:/dmcore/dmcore/digitalmarketing/sms.py) | Messaging | **Created** | Pluggable SMS backend architecture and phone normalization |
| [`digitalmarketing/validators.py`](file:///d:/dmcore/dmcore/digitalmarketing/validators.py) | Validation | **Created** | Shared email and phone validation helpers |
| [`digitalmarketing/management/commands/map_default_fields.py`](file:///d:/dmcore/dmcore/digitalmarketing/management/commands/map_default_fields.py) | CLI | **Created** | Management command to initialize default question mappings |
| [`digitalmarketing/management/commands/make_interview_link.py`](file:///d:/dmcore/dmcore/digitalmarketing/management/commands/make_interview_link.py) | CLI | **Created** | CLI utility to generate signed candidate interview links |
| [`digitalmarketing/tests.py`](file:///d:/dmcore/dmcore/digitalmarketing/tests.py) | Quality | **Updated** | Comprehensive test suite containing 31 automated tests |
| [`digitalmarketing/models.py`](file:///d:/dmcore/dmcore/digitalmarketing/models.py) | Data | **Updated** | Added `question_id`, constraints, and `clean()` integrity guards |
| [`digitalmarketing/utils.py`](file:///d:/dmcore/dmcore/digitalmarketing/utils.py) | Engine | **Updated** | Implemented `get_lead_missing_interview_questions()` engine |
| [`digitalmarketing/views.py`](file:///d:/dmcore/dmcore/digitalmarketing/views.py) | Controller | **Updated** | Added session/answer/complete endpoints, dispatch, and Course rules |
| [`digitalmarketing/urls.py`](file:///d:/dmcore/dmcore/digitalmarketing/urls.py) | Routing | **Updated** | Registered `/api/interview/*` REST routes |
| [`digitalmarketing/admin.py`](file:///d:/dmcore/dmcore/digitalmarketing/admin.py) | Admin | **Updated** | Registered `LeadField_Register`, `LeadConfused`, and `LeadDetails` |
| [`digitalmarketing/scheduler.py`](file:///d:/dmcore/dmcore/digitalmarketing/scheduler.py) | Ops | **Updated** | Socket lock guard to prevent duplicate scheduler runs |
| [`dmcore/settings.py`](file:///d:/dmcore/dmcore/dmcore/settings.py) | Config | **Updated** | Added WhiteNoise, SMS settings, and SQLite 30s timeout |
| [`digitalmarketing/migrations/0023_add_interview_email_sent.py`](file:///d:/dmcore/dmcore/digitalmarketing/migrations/0023_add_interview_email_sent.py) | Schema | **Created** | Schema migration for interview tracking columns |
| [`digitalmarketing/migrations/0024_add_question_id_to_leadfield.py`](file:///d:/dmcore/dmcore/digitalmarketing/migrations/0024_add_question_id_to_leadfield.py) | Schema | **Created** | Schema migration for question ID check and uniqueness constraints |
| [`digitalmarketing/migrations/0025_alter_company_code_unique_log_username_nullable.py`](file:///d:/dmcore/dmcore/digitalmarketing/migrations/0025_alter_company_code_unique_log_username_nullable.py) | Schema | **Created** | Schema migration for company code uniqueness and nullable log username |
| [`static/js/register_work.js`](file:///d:/dmcore/dmcore/static/js/register_work.js) | Frontend | **Updated** | Added null pointer guards for dynamic field generation |
| [`templates/data_bank.html`](file:///d:/dmcore/dmcore/templates/data_bank.html) | UI | **Updated** | Enhanced dispatch button, channel feedback, and resend safeguards |
| [`templates/lead_list.html`](file:///d:/dmcore/dmcore/templates/lead_list.html) | UI | **Updated** | Disabled confused button with tooltip if contact is missing |
| [`templates/manual_lead_add.html`](file:///d:/dmcore/dmcore/templates/manual_lead_add.html) | UI | **Updated** | Made Course mandatory and removed Lead Source |
| [`templates/excel_lead_upload.html`](file:///d:/dmcore/dmcore/templates/excel_lead_upload.html) | UI | **Updated** | Updated template guidelines to require Course column |
| [`templates/register_work.html`](file:///d:/dmcore/dmcore/templates/register_work.html) | UI | **Updated** | Work builder UI for assigning question IDs 1–18 |
