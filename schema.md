# Database Schema

This document describes all database tables used by the Fraud App Detection Using Sentiment Analysis application, including column names, data types, primary/foreign keys, and descriptions.

---

## Table: `auth_user`

Django’s built-in user model (from `django.contrib.auth`). Referenced by app models via foreign keys.

| Column           | Data Type        | PK | FK | Description                                      |
|-----------------|------------------|----|----|--------------------------------------------------|
| id              | INTEGER          | ✓  |    | Auto-increment primary key.                      |
| password        | VARCHAR(128)     |    |    | Hashed password.                                 |
| last_login      | DATETIME         |    |    | Time of last login (nullable).                   |
| is_superuser    | BOOLEAN          |    |    | Whether the user has all permissions.           |
| username        | VARCHAR(150)     |    |    | Unique username.                                 |
| first_name      | VARCHAR(150)     |    |    | User’s first name.                               |
| last_name       | VARCHAR(150)     |    |    | User’s last name.                                |
| email           | VARCHAR(254)     |    |    | User’s email address.                            |
| is_staff        | BOOLEAN          |    |    | Whether the user can access the admin site.     |
| is_active       | BOOLEAN          |    |    | Whether the account is active.                   |
| date_joined     | DATETIME         |    |    | When the account was created.                   |

---

## Table: `accounts_userprofile`

Optional profile for users; used for future metadata and extensibility.

| Column     | Data Type | PK | FK | Description                                      |
|------------|-----------|----|----|--------------------------------------------------|
| id         | BIGINT    | ✓  |    | Auto-increment primary key.                      |
| user_id    | INTEGER   |    | ✓  | References `auth_user.id`. One-to-one per user.  |
| created_at | DATETIME  |    |    | When the profile was created.                    |

**Foreign keys**

- `user_id` → `auth_user.id` (ON DELETE CASCADE)

---

## Table: `apps_store_mobileapp`

Mobile applications that can be evaluated for fraud risk using user reviews.

| Column              | Data Type   | PK | FK | Description                                      |
|---------------------|-------------|----|----|--------------------------------------------------|
| id                  | BIGINT      | ✓  |    | Auto-increment primary key.                      |
| name                | VARCHAR(255)|    |    | Display name of the app.                         |
| package_name        | VARCHAR(255)|    |    | Unique package identifier (e.g. Play Store).     |
| store_url           | VARCHAR(200)|    |    | URL to the app in the store (nullable).          |
| developer           | VARCHAR(255)|    |    | Developer name (nullable).                       |
| category            | VARCHAR(255)|    |    | App category (nullable).                         |
| privacy_policy_text | TEXT        |    |    | Privacy policy content (nullable).              |
| description         | TEXT        |    |    | App description (nullable).                      |
| created_by_id       | INTEGER     |    | ✓  | User who added the app; references `auth_user.id`. |
| created_at          | DATETIME    |    |    | When the app was added.                         |

**Foreign keys**

- `created_by_id` → `auth_user.id` (ON DELETE CASCADE)

**Indexes**

- `(created_by_id, created_at)`
- `(package_name)` (unique)

---

## Table: `apps_store_watchlist`

A user’s list of apps they are monitoring over time.

| Column    | Data Type | PK | FK | Description                                      |
|-----------|-----------|----|----|--------------------------------------------------|
| id        | BIGINT    | ✓  |    | Auto-increment primary key.                      |
| user_id   | INTEGER   |    | ✓  | References `auth_user.id`.                       |
| app_id    | BIGINT    |    | ✓  | References `apps_store_mobileapp.id`.            |
| added_at  | DATETIME  |    |    | When the app was added to the watchlist.         |

**Foreign keys**

- `user_id` → `auth_user.id` (ON DELETE CASCADE)
- `app_id` → `apps_store_mobileapp.id` (ON DELETE CASCADE)

**Unique constraint**

- `(user_id, app_id)` — one watchlist entry per user per app.

---

## Table: `apps_store_communityreport`

Community-submitted reports flagging apps as suspicious.

| Column     | Data Type   | PK | FK | Description                                      |
|------------|-------------|----|----|--------------------------------------------------|
| id         | BIGINT      | ✓  |    | Auto-increment primary key.                      |
| user_id    | INTEGER     |    | ✓  | User who submitted the report; references `auth_user.id`. |
| app_id     | BIGINT      |    | ✓  | App being reported; references `apps_store_mobileapp.id`.  |
| reason     | VARCHAR(32)|    |    | One of: FRAUD, PRIVACY, SCAM, MALWARE, MISLEADING, OTHER.  |
| description| TEXT        |    |    | Report details (max 2000 characters).            |
| created_at | DATETIME   |    |    | When the report was created.                     |

**Foreign keys**

- `user_id` → `auth_user.id` (ON DELETE CASCADE)
- `app_id` → `apps_store_mobileapp.id` (ON DELETE CASCADE)

**Reason choices**

- `FRAUD` — Suspected Fraud  
- `PRIVACY` — Privacy Violation  
- `SCAM` — Financial Scam  
- `MALWARE` — Malware / Spyware  
- `MISLEADING` — Misleading Functionality  
- `OTHER` — Other  

---

## Table: `analysis_analysisrun`

A single LLM classification run for an app based on its reviews. Stores the raw LLM response for auditing.

| Column          | Data Type   | PK | FK | Description                                      |
|-----------------|-------------|----|----|--------------------------------------------------|
| id              | BIGINT      | ✓  |    | Auto-increment primary key.                      |
| app_id          | BIGINT      |    | ✓  | App analyzed; references `apps_store_mobileapp.id`. |
| created_by_id   | INTEGER     |    | ✓  | User who ran the analysis; references `auth_user.id`. |
| status          | VARCHAR(16)|    |    | Run status: SUCCESS or FAILED.                   |
| model_name      | VARCHAR(255)|   |    | Name of the LLM used.                            |
| prompt_version  | VARCHAR(64)|    |    | Version of the prompt (default: v1).             |
| llm_label       | VARCHAR(16)|    |    | Classification: LEGIT, SUSPICIOUS, FRAUD, UNKNOWN. |
| llm_confidence | FLOAT      |    |    | Confidence score from 0.0 to 1.0.                |
| llm_rationale   | TEXT       |    |    | LLM explanation for the label (nullable).       |
| safety_score    | INTEGER    |    |    | Safety score (default: 0).                        |
| sentiment_score | INTEGER    |    |    | Sentiment score (default: 0).                    |
| llm_json        | TEXT       |    |    | Parsed JSON output from LLM (nullable).         |
| raw_response    | TEXT       |    |    | Full raw LLM response (nullable).                |
| error_message   | TEXT       |    |    | Error message if status is FAILED (nullable).   |
| created_at      | DATETIME   |    |    | When the run was created.                        |

**Foreign keys**

- `app_id` → `apps_store_mobileapp.id` (ON DELETE CASCADE)
- `created_by_id` → `auth_user.id` (ON DELETE CASCADE)

**Indexes**

- `(app_id, created_at)`
- `(created_by_id, created_at)`
- `(llm_label)`

---

## Table: `reviews_review`

User comments/reviews for a mobile app.

| Column     | Data Type   | PK | FK | Description                                      |
|------------|-------------|----|----|--------------------------------------------------|
| id         | BIGINT      | ✓  |    | Auto-increment primary key.                      |
| app_id     | BIGINT      |    | ✓  | App this review belongs to; references `apps_store_mobileapp.id`. |
| text       | TEXT        |    |    | Review text.                                     |
| rating     | INTEGER     |    |    | Optional 1–5 star rating (nullable).              |
| author     | VARCHAR(255)|    |    | Display name of the reviewer (nullable).         |
| review_date| DATETIME    |    |    | Original date of the review, if known (nullable). |
| source     | VARCHAR(255)|    |    | Source of the review (e.g. Google Play) (nullable). |
| created_at | DATETIME    |    |    | When the review was stored in the system.        |

**Foreign keys**

- `app_id` → `apps_store_mobileapp.id` (ON DELETE CASCADE)

**Indexes**

- `(app_id, created_at)`
- `(app_id, review_date)`

---

## Entity relationship summary

```
auth_user
  ├── accounts_userprofile (1:1 via user_id)
  ├── apps_store_mobileapp (1:N via created_by_id)
  ├── apps_store_watchlist (1:N via user_id)
  ├── apps_store_communityreport (1:N via user_id)
  └── analysis_analysisrun (1:N via created_by_id)

apps_store_mobileapp
  ├── apps_store_watchlist (1:N via app_id)
  ├── apps_store_communityreport (1:N via app_id)
  ├── analysis_analysisrun (1:N via app_id)
  └── reviews_review (1:N via app_id)
```
