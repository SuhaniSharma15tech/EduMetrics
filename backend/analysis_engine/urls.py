"""
EduMetrics — analysis_engine/urls.py
All routes under /api/analysis/ (configured in config/urls.py).
"""

from django.urls import path
from .views import (
    # New frontend-optimised endpoints
    dashboard_summary,
    flagged_students,
    all_students,
    student_detail,
    student_trajectory_view,
    class_analytics,
    last_week_comparison,
    # Prediction endpoints
    pre_mid_term_list,
    pre_mid_term_student,
    pre_end_term_list,
    pre_end_term_student,
    risk_of_failing_list,
    risk_of_failing_student,
    pre_sem_watchlist_list,
    pre_sem_watchlist_student,
    interventions_list,
    # Internal
    trigger_calibrate,
)

urlpatterns = [

    # ── DASHBOARD ──────────────────────────────────────────────────────────────
    # GET /api/analysis/dashboard/summary/?class_id=X&semester=Y&sem_week=Z
    path('dashboard/summary/', dashboard_summary, name='dashboard_summary'),

    # ── FLAGGED STUDENTS  (matches FLAGGED[] in app.js) ────────────────────────
    # GET /api/analysis/flagged/?class_id=X&semester=Y&sem_week=Z
    path('flagged/', flagged_students, name='flagged_students'),

    # ── ALL STUDENTS ROSTER  (matches ALL_STUDENTS[] in app.js) ───────────────
    # GET /api/analysis/students/?class_id=X&semester=Y&sem_week=Z
    path('students/', all_students, name='all_students'),

    # ── STUDENT DETAIL + TRAJECTORY ────────────────────────────────────────────
    # GET /api/analysis/student/<student_id>/detail/?semester=Y&sem_week=Z
    path('student/<str:student_id>/detail/',      student_detail,          name='student_detail'),
    # GET /api/analysis/student/<student_id>/trajectory/?semester=Y[&from_week=1]
    path('student/<str:student_id>/trajectory/', student_trajectory_view, name='student_trajectory'),

    # ── CLASS ANALYTICS ────────────────────────────────────────────────────────
    # GET /api/analysis/analytics/?class_id=X&semester=Y&sem_week=Z
    path('analytics/', class_analytics, name='class_analytics'),

    # ── LAST WEEK COMPARISON  (matches LAST_WEEK[] in app.js) ─────────────────
    # GET /api/analysis/last_week/?class_id=X&semester=Y&sem_week=Z
    path('last_week/', last_week_comparison, name='last_week_comparison'),

    # ── PRE-MID TERM PREDICTIONS ───────────────────────────────────────────────
    # GET /api/analysis/pre_mid_term/?class_id=X&semester=Y[&sem_week=6|7]
    path('pre_mid_term/',         pre_mid_term_list,    name='pre_mid_term_list'),
    # GET /api/analysis/pre_mid_term/student/?student_id=X[&semester=Y]
    path('pre_mid_term/student/', pre_mid_term_student, name='pre_mid_term_student'),

    # ── PRE-END TERM PREDICTIONS ───────────────────────────────────────────────
    # GET /api/analysis/pre_end_term/?class_id=X&semester=Y
    path('pre_end_term/',         pre_end_term_list,    name='pre_end_term_list'),
    # GET /api/analysis/pre_end_term/student/?student_id=X[&semester=Y]
    path('pre_end_term/student/', pre_end_term_student, name='pre_end_term_student'),

    # ── RISK OF FAILING ────────────────────────────────────────────────────────
    # GET /api/analysis/risk_of_failing/?class_id=X&semester=Y[&sem_week=Z]
    path('risk_of_failing/',         risk_of_failing_list,    name='risk_of_failing_list'),
    # GET /api/analysis/risk_of_failing/student/?student_id=X[&semester=Y]
    path('risk_of_failing/student/', risk_of_failing_student, name='risk_of_failing_student'),

    # ── PRE-SEM WATCHLIST ──────────────────────────────────────────────────────
    # GET /api/analysis/pre_sem_watchlist/?class_id=X&target_semester=Y
    path('pre_sem_watchlist/',         pre_sem_watchlist_list,    name='pre_sem_watchlist_list'),
    # GET /api/analysis/pre_sem_watchlist/student/?student_id=X[&target_semester=Y]
    path('pre_sem_watchlist/student/', pre_sem_watchlist_student, name='pre_sem_watchlist_student'),
    
    #GET /api/analysis/interventions/?class_id=CSE_Y1_A&semester=2&sem_week=9
    path('interventions/', interventions_list, name='interventions_list'),

    # ── INTERNAL ───────────────────────────────────────────────────────────────
    # POST /api/analysis/trigger_calibrate/
    path('trigger_calibrate/', trigger_calibrate, name='trigger_calibrate'),

]
