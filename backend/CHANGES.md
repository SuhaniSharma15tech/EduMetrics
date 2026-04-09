# EduMetrics Backend — Changes Summary
## What was changed and why

### `analysis_engine/models.py` — Full rewrite
All model field names and table names now exactly match `analysis_db_schema.sql v2.1`.

**`weekly_metrics` table**
| Old field name (incorrect) | New field name (SQL schema) | Note |
|---|---|---|
| `library_visits_w` | `library_visits` | Matches SQL |
| `book_borrows_w` | `book_borrows` | Matches SQL |
| `assn_quality_avg` | `assn_quality_pct` | Matches SQL |
| `assn_plagiarism_max` | `assn_plagiarism_pct` | Matches SQL |
| `att_rate_recent` | `weekly_att_pct` | SQL stores as 0-100 pct |
| `quiz_submit_rate_recent` | `quiz_attempt_rate` | Matches SQL |
| `assn_submit_rate_recent` | `assn_submit_rate` | Matches SQL |
| `weight_m`, `weight_n`, `weight_p` | **removed** | Not in SQL schema |
| `risk_of_failing` (column) | **removed** | Moved to separate table |
| `recent_quiz_avg_pct`, `midterm_pct`, `endterm_pct`, `quiz_trend` | **removed** | Not in SQL schema |
| *(missing)* | `risk_of_detention` | Added — in SQL schema |
| *(missing)* | `overall_att_pct` | Added — in SQL schema |

**`risk_of_failing_prediction` model → renamed to `risk_of_failing`**
- Table name in SQL is `risk_of_failing`, not `risk_of_failing_prediction`
- Aliases `RiskOfFailing` and `RiskOfFailingPrediction` both point to new model

**`intervention_log` model**
- Added `flag` ForeignKey → `weekly_flags` (`flag_id` in SQL schema, nullable)
- Added `notes` as the canonical advisor text field (per SQL schema)
- Kept `trigger_diagnosis` and `advisor_notified` as nullable legacy fields

**`pre_sem_watchlist`**
- Made `att_rate_hist`, `assn_rate_hist`, `exam_avg_hist` nullable (engine may not always have data)

**All models now have explicit `db_table` Meta so Django doesn't prefix them.**

---

### `analysis_engine/migrations/0001_initial.py` — Full rewrite
Matches new models.py exactly. Key changes:
- `weekly_metrics`: all column names corrected per SQL schema
- `risk_of_failing_prediction` → `risk_of_failing`
- `intervention_log`: added `flag_id` FK, added `notes` column
- All models have correct `db_table` options

---

### `analysis_engine/weekly_metrics_calculator.py`
- `fields = dict(...)` block updated: all keys now use SQL schema column names
- `att_r` (0–1 ratio from `_compute_effort`) is multiplied by 100 before
  storing in `weekly_att_pct` (which is a 0–100 pct column in SQL)
- Removed `weight_m`, `weight_n`, `weight_p` from the fields dict

---

### `analysis_engine/pre_sem.py`
- WeeklyMetrics `.annotate()` query updated:
  - `Avg('att_rate_recent')` → `Avg('overall_att_pct')`
  - `Avg('assn_submit_rate_recent')` → `Avg('assn_submit_rate')`
  - `DMax('assn_plagiarism_max')` → `DMax('assn_plagiarism_pct')`

---

### `analysis_engine/flagging.py`
- `WeeklyFlag(...)` creation now passes `archetype=row.get('archetype')`
- `_save_memory()` now writes both `trigger_diagnosis` (legacy) and
  `notes` (canonical SQL field) from the same diagnosis string

---

### `analysis_engine/views.py`
All field name references updated to match new models:
- `att_rate_recent` → `overall_att_pct` (already 0-100, `*100` removed)
- `quiz_submit_rate_recent` → `quiz_attempt_rate`
- `assn_submit_rate_recent` → `assn_submit_rate`
- `library_visits_w` → `library_visits`
- `book_borrows_w` → `book_borrows`
- `assn_quality_avg` → `assn_quality_pct`
- `assn_plagiarism_max` → `assn_plagiarism_pct`
- `risk_of_failing_prediction` → `risk_of_failing` (model class name)
- `risk_of_failing` column removed from `weekly_metrics` queries;
  now fetched from `risk_of_failing` table with a `rof_map` lookup

---

### `analysis_engine/serializer.py`
- `risk_of_failing_prediction` → `risk_of_failing`
