"""
analysis_engine/risk_of_detention.py
=====================================
Calculates attendance-based detention risk for every active student
and writes risk_of_detention + overall_att_pct into weekly_metrics.

Detention rule (standard Indian universities):
    A student needs >= 75% attendance to sit for an exam.

Formula
-------
    H  = lectures held so far this semester
    A  = lectures attended so far
    R  = lectures remaining before the exam
         = (exam_sem_week - current_sem_week - 1) * lectures_per_week * n_subjects

    pressure = (0.75*(H+R) - A) / R
        > 1.0  → certain detention
        0.75–1.0 → critical
        < 0.75  → some slack

risk_of_detention stored as 0–100:
    certain (pressure>1.0)  → 100
    critical (>=0.90)       →  90
    high_risk (>=0.75)      →  70
    moderate (>=0.50)       →  50
    safe                    →  max(0, pressure*100)

Called by calibrate_analysis_db.py every teaching week as
    run_detention_risk()
"""

import os
import pickle

from django.db.models import Sum, Max
from django.db import transaction

from analysis_engine.client_models import (
    ClientSimState,
    ClientClass,
    ClientAttendance,
    ClientClassSubject,
    ClientSubject,
)
from analysis_engine.models import WeeklyMetrics

# ── Constants ────────────────────────────────────────────────────────────────
MIDTERM_SEM_WEEK  = 8
ENDTERM_SEM_WEEK  = 18
LECTURES_PER_WEEK = 3    # per subject per teaching week
EXAM_WEEKS        = {MIDTERM_SEM_WEEK, ENDTERM_SEM_WEEK}
DETENTION_THRESHOLD = 0.75


# ── Helpers ───────────────────────────────────────────────────────────────────
def _calc_pressure(attended, held, remaining):
    """
    Fraction of remaining lectures the student MUST attend to reach 75%.
    Returns 0.0 if already safe, >1.0 if impossible, None if exam passed.
    """
    if remaining <= 0:
        return None
    needed = DETENTION_THRESHOLD * (held + remaining) - attended
    if needed <= 0:
        return 0.0
    return needed / remaining


def _pressure_to_risk_score(pressure):
    """Convert pressure ratio to a 0-100 risk score for the portal."""
    if pressure is None:
        return 0.0     # exam already passed, no current risk
    if pressure > 1.0:
        return 100.0   # certain detention
    if pressure >= 0.90:
        return 90.0
    if pressure >= 0.75:
        return 70.0
    if pressure >= 0.50:
        return 50.0
    return round(max(0.0, pressure * 100), 2)


def _teaching_weeks_remaining(from_week, to_exam_week):
    """Count teaching weeks strictly between from_week and to_exam_week."""
    return sum(
        1 for w in range(from_week + 1, to_exam_week)
        if w not in EXAM_WEEKS
    )


# ── Main function ─────────────────────────────────────────────────────────────
def run_detention_risk():
    """
    Read attendance from client DB, compute detention risk, write
    risk_of_detention and overall_att_pct into analysis_db.weekly_metrics.
    Called by calibrate_analysis_db.py every teaching week.
    """

    # ── 1. Current week from sim_state ───────────────────────────────────────
    state = ClientSimState.objects.using('client_db').filter(id=1).first()
    if not state:
        print("[detention_risk] ERROR — sim_state row not found.")
        return

    global_week = state.current_week
    if global_week <= 18:
        sem_week = global_week
        slot = 'odd'
    else:
        sem_week = global_week - 18
        slot = 'even'

    if sem_week in EXAM_WEEKS:
        print(f"[detention_risk] Exam week {sem_week} — skipping.")
        return

    # ── 2. Active classes ────────────────────────────────────────────────────
    classes = list(ClientClass.objects.using('client_db').values(
        'class_id', 'odd_sem', 'even_sem'
    ))

    to_create = []
    to_update = []

    for cls in classes:
        cid      = cls['class_id']
        semester = cls['odd_sem'] if slot == 'odd' else cls['even_sem']

        # Count subjects active this semester for this class
        n_subjects = ClientClassSubject.objects.using('client_db').filter(
            class_id=cid,
        ).count() or 5   # fallback to 5 if table unavailable

        # Remaining teaching weeks to each exam
        weeks_left_mid = _teaching_weeks_remaining(sem_week, MIDTERM_SEM_WEEK)
        weeks_left_end = _teaching_weeks_remaining(sem_week, ENDTERM_SEM_WEEK)
        remaining_mid  = weeks_left_mid * n_subjects * LECTURES_PER_WEEK
        remaining_end  = weeks_left_end * n_subjects * LECTURES_PER_WEEK

        # Per-student cumulative attendance totals up to this sem_week
        att_qs = (
            ClientAttendance.objects.using('client_db')
            .filter(class_id=cid, week__lte=sem_week)
            .values('student_id')
            .annotate(
                total_present=Sum('present'),
                total_held=Sum('lectures_held'),
            )
        )

        # Pre-fetch existing weekly_metrics rows for this class/week to bulk-update
        existing = {
            wm.student_id: wm
            for wm in WeeklyMetrics.objects.filter(
                class_id=cid, semester=semester, sem_week=sem_week
            )
        }

        for row in att_qs:
            sid           = row['student_id']
            total_present = int(row['total_present'] or 0)
            total_held    = int(row['total_held'] or 0)

            # Overall attendance pct so far (0-100)
            overall_att = round(
                (total_present / total_held * 100) if total_held > 0 else 0.0,
                2
            )

            # Use endterm pressure as the primary risk signal
            pressure = _calc_pressure(total_present, total_held, remaining_end)
            risk_score = _pressure_to_risk_score(pressure)

            if sid in existing:
                obj = existing[sid]
                obj.risk_of_detention = risk_score
                obj.overall_att_pct   = overall_att
                to_update.append(obj)
            else:
                to_create.append(WeeklyMetrics(
                    student_id        = sid,
                    class_id          = cid,
                    semester          = semester,
                    sem_week          = sem_week,
                    risk_of_detention = risk_score,
                    overall_att_pct   = overall_att,
                ))

    with transaction.atomic():
        if to_create:
            WeeklyMetrics.objects.bulk_create(
                to_create,
                update_conflicts=True,
                update_fields=['risk_of_detention', 'overall_att_pct'],
                unique_fields=['student_id', 'semester', 'sem_week'],
            )
        if to_update:
            WeeklyMetrics.objects.bulk_update(
                to_update, ['risk_of_detention', 'overall_att_pct']
            )

    total = len(to_create) + len(to_update)
    print(
        f"[detention_risk] Week {sem_week}: wrote {total} rows "
        f"({len(to_create)} new, {len(to_update)} updated)."
    )


if __name__ == '__main__':
    import django, os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    run_detention_risk()
