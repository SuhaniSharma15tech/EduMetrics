from django.urls import path
from .views import (
    # Existing
    get_flaggeddata,
    class_performance,
    student_performance,
    student_trajectory,
    # Pre-mid term (NEW)
    pre_mid_term_list,
    pre_mid_term_student,
    # Pre-end term (NEW)
    pre_end_term_list,
    pre_end_term_student,
    # Risk of failing table (NEW)
    risk_of_failing_list,
    risk_of_failing_student,
    # Pre-sem watchlist (NEW)
    pre_sem_watchlist_list,
    pre_sem_watchlist_student,
)

urlpatterns = [
    # ── Existing endpoints ─────────────────────────────────────
    path('get_flaggeddata/', get_flaggeddata, name='get_flaggeddata'),
    path('class_performance/', class_performance, name='class_performance'),
    path('student_performance/', student_performance, name='student_performance'),
    path('student_trajectory/', student_trajectory, name='student_trajectory'),

    # ── Pre-Mid Term predictions (NEW) ─────────────────────────
    # GET /analysis/pre_mid_term/?class_id=X&semester=Y[&sem_week=6|7]
    path('pre_mid_term/', pre_mid_term_list, name='pre_mid_term_list'),
    # GET /analysis/pre_mid_term/student/?student_id=X[&semester=Y]
    path('pre_mid_term/student/', pre_mid_term_student, name='pre_mid_term_student'),

    # ── Pre-End Term predictions (NEW) ─────────────────────────
    # GET /analysis/pre_end_term/?class_id=X&semester=Y
    path('pre_end_term/', pre_end_term_list, name='pre_end_term_list'),
    # GET /analysis/pre_end_term/student/?student_id=X[&semester=Y]
    path('pre_end_term/student/', pre_end_term_student, name='pre_end_term_student'),

    # ── Risk of Failing predictions (NEW) ──────────────────────
    # GET /analysis/risk_of_failing/?class_id=X&semester=Y[&sem_week=Z]
    path('risk_of_failing/', risk_of_failing_list, name='risk_of_failing_list'),
    # GET /analysis/risk_of_failing/student/?student_id=X[&semester=Y]
    path('risk_of_failing/student/', risk_of_failing_student, name='risk_of_failing_student'),

    # ── Pre-Sem Watchlist (NEW) ────────────────────────────────
    # GET /analysis/pre_sem_watchlist/?class_id=X&target_semester=Y
    path('pre_sem_watchlist/', pre_sem_watchlist_list, name='pre_sem_watchlist_list'),
    # GET /analysis/pre_sem_watchlist/student/?student_id=X[&target_semester=Y]
    path('pre_sem_watchlist/student/', pre_sem_watchlist_student, name='pre_sem_watchlist_student'),
]
