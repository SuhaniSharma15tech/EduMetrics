"""
analysis_engine/risk_of_failing.py
====================================
Predicts probability of failing for each student from week 10 onwards,
using the trained fail_risk_model.json (converted from sklearn Pipeline pkl).

Logic
-----
Uses the student's weekly_metrics up to the current week to build features,
then predicts p_fail and assigns a risk_label (LOW / MEDIUM / HIGH).

Features fed to the model:
    - avg_academic_performance   (mean of all academic_performance rows so far)
    - avg_effort_score           (mean of all effort_score rows so far)
    - midterm_score_pct          (actual midterm score, or 0 if not yet available)
    - overall_att_pct            (latest cumulative attendance %)
    - assn_submit_rate           (latest assignment submission rate, 0-1)

Label thresholds:
    p_fail >= 0.60  → HIGH
    p_fail >= 0.35  → MEDIUM
    p_fail <  0.35  → LOW

Called by calibrate_analysis_db.py as  run_failing_risk()
from week 10 onwards every teaching week.

Model format
------------
The pipeline stored in fail_risk_model.json encodes three fitted steps:
  1. imputer  — SimpleImputer(strategy='mean')
  2. scaler   — StandardScaler
  3. lr       — LogisticRegression (binary, class 1 = fail)

The imputer accepts 33 input features; three feature columns were always
missing during training (indices stored in meta.always_missing_feature_indices)
and are dropped before the scaler, giving 30 features to the LR.

Inference is done in pure numpy — no sklearn required at runtime.
"""

import os
import json
import math
import numpy as np

from django.db.models import Avg
from django.db import transaction

from analysis_engine.models import WeeklyMetrics, RiskOfFailing

# ── Model path ────────────────────────────────────────────────────────────────
_HERE           = os.path.dirname(os.path.abspath(__file__))
FAIL_MODEL_PATH = os.path.join(_HERE, 'models', 'fail_risk_model.json')

# ── Label thresholds ──────────────────────────────────────────────────────────
HIGH_THRESHOLD   = 0.60
MEDIUM_THRESHOLD = 0.35


# ── Load model (lazy, cached at module level) ─────────────────────────────────
_fail_model = None

def _get_model():
    global _fail_model
    if _fail_model is None:
        if not os.path.exists(FAIL_MODEL_PATH):
            raise FileNotFoundError(
                f"fail_risk_model.json not found at: {FAIL_MODEL_PATH}\n"
                "Ensure the models/ directory is present in analysis_engine/."
            )
        with open(FAIL_MODEL_PATH, 'r') as f:
            _fail_model = json.load(f)
        print(f"[risk_of_failing] Model loaded from: {FAIL_MODEL_PATH}")
    return _fail_model


def _predict_proba(model_json, X_raw):
    """
    Pure-numpy replication of the sklearn Pipeline:
      SimpleImputer(strategy='mean')  →  drop always-missing cols  →
      StandardScaler  →  LogisticRegression (sigmoid)

    Parameters
    ----------
    model_json : dict   Loaded from fail_risk_model.json
    X_raw      : array-like, shape (1, n_imputer_features)

    Returns
    -------
    float  — probability of failing (class 1), in [0, 1]
    """
    imp     = model_json['imputer']
    scaler  = model_json['scaler']
    lr      = model_json['lr']
    always_missing = set(model_json['meta']['always_missing_feature_indices'])

    X = np.array(X_raw, dtype=float)

    # ── Step 1: Impute missing values with per-feature training means ─────────
    for j in range(X.shape[1]):
        stat = imp['statistics_'][j]
        if stat is None:
            continue   # always-missing column — will be dropped below
        nan_mask = np.isnan(X[:, j])
        X[nan_mask, j] = stat

    # ── Step 2: Drop columns that were always missing in training ─────────────
    keep_cols = [j for j in range(X.shape[1]) if j not in always_missing]
    X = X[:, keep_cols]

    # ── Step 3: StandardScale ─────────────────────────────────────────────────
    mean_  = np.array(scaler['mean_'])
    scale_ = np.array(scaler['scale_'])
    X = (X - mean_) / scale_

    # ── Step 4: Logistic Regression — sigmoid(Xw + b) ─────────────────────────
    coef      = np.array(lr['coef_'][0])
    intercept = float(lr['intercept_'][0])
    logit     = (X @ coef).item() + intercept     # .item() handles shape (1,) safely
    p_fail    = 1.0 / (1.0 + math.exp(-logit))   # numerically stable sigmoid

    return p_fail


def _label(p):
    if p >= HIGH_THRESHOLD:
        return 'HIGH'
    if p >= MEDIUM_THRESHOLD:
        return 'MEDIUM'
    return 'LOW'


# ── Main function ─────────────────────────────────────────────────────────────
def run_failing_risk(sem_week=None, semester=None):
    """
    Reads weekly_metrics up to the current sem_week, builds features per student,
    runs the fail_risk_model, and writes to the risk_of_failing table.

    Called by calibrate_analysis_db.py every teaching week from week 10 onward.
    """

    if sem_week < 10:
        print(f"[risk_of_failing] Week {sem_week} < 10 — skipping (model runs week 10+).")
        return

    # ── 2. Load model ─────────────────────────────────────────────────────────
    model = _get_model()

    # ── 3. Aggregate per-student features from weekly_metrics ─────────────────
    # Find all semesters that have data up to this week
    sem_qs = (
        WeeklyMetrics.objects
        .filter(semester=semester, sem_week__lte=sem_week)
        .values('student_id', 'class_id', 'semester')
        .distinct()
    )
    combos = list(sem_qs)

    if not combos:
        print("[risk_of_failing] No weekly_metrics data found — skipping.")
        return

    # Get aggregated features per (student, semester)
    agg_qs = (
        WeeklyMetrics.objects
        .filter(semester=semester, sem_week__lte=sem_week)
        .values('student_id', 'class_id', 'semester')
        .annotate(
            avg_ap     = Avg('academic_performance'),
            avg_effort = Avg('effort_score'),
        )
    )
    agg_map = {
        (r['student_id'], r['semester']): r
        for r in agg_qs
    }

    # Get latest row per (student, semester) for point-in-time fields
    latest_map = {}
    for wm in (WeeklyMetrics.objects
               .filter(semester=semester, sem_week__lte=sem_week)
               .order_by('student_id', 'semester', '-sem_week')):
        key = (wm.student_id, wm.semester)
        if key not in latest_map:
            latest_map[key] = wm

    # ── 4. Build predictions ──────────────────────────────────────────────────
    to_create = []
    to_update = []

    n_features = model['meta']['n_features_imputer']  # 33

    seen_keys = set()
    for combo in combos:
        sid      = combo['student_id']
        cid      = combo['class_id']
        semester = combo['semester']
        key      = (sid, semester)

        if key in seen_keys:
            continue
        seen_keys.add(key)

        agg  = agg_map.get(key)
        last = latest_map.get(key)

        if not agg or not last:
            continue

        # ── Build feature vector (5 active features, rest padded with nan) ────
        # The model was trained on 33 features; the 5 features this script
        # provides are placed at the positions the training code used.
        # Remaining 28 positions stay nan and are imputed from training means.
        avg_ap      = float(agg['avg_ap']     or 0.0)
        avg_effort  = float(agg['avg_effort'] or 0.0)
        midterm_pct = float(last.midterm_score_pct or 0.0)
        overall_att = float(last.overall_att_pct   or 0.0)
        assn_sub    = float(last.assn_submit_rate   or 0.0)

        X = np.full((1, n_features), np.nan)
        X[0, 0] = avg_ap
        X[0, 1] = avg_effort
        X[0, 2] = midterm_pct
        X[0, 3] = overall_att
        X[0, 4] = assn_sub

        try:
            p_fail = _predict_proba(model, X)
        except Exception as e:
            print(f"[risk_of_failing] Prediction error for {sid}: {e}")
            continue

        p_fail = round(min(max(p_fail, 0.0), 1.0), 4)
        label  = _label(p_fail)

        # Upsert into risk_of_failing table
        existing = RiskOfFailing.objects.filter(
            student_id=sid, semester=semester, sem_week=sem_week
        ).first()

        if existing:
            existing.p_fail     = p_fail
            existing.risk_label = label
            to_update.append(existing)
        else:
            to_create.append(RiskOfFailing(
                student_id = sid,
                class_id   = cid,
                semester   = semester,
                sem_week   = sem_week,
                p_fail     = p_fail,
                risk_label = label,
            ))

    with transaction.atomic():
        if to_create:
            RiskOfFailing.objects.bulk_create(
                to_create,
                update_conflicts=True,
                update_fields=['p_fail', 'risk_label'],
                unique_fields=['student_id', 'semester', 'sem_week'],
            )
        if to_update:
            RiskOfFailing.objects.bulk_update(to_update, ['p_fail', 'risk_label'])

    total = len(to_create) + len(to_update)
    high  = sum(1 for r in to_create + to_update if r.risk_label == 'HIGH')
    med   = sum(1 for r in to_create + to_update if r.risk_label == 'MEDIUM')
    print(
        f"[risk_of_failing] Week {sem_week}: {total} predictions written "
        f"— HIGH: {high}, MEDIUM: {med}, LOW: {total - high - med}"
    )


if __name__ == '__main__':
    import django, os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    run_failing_risk()