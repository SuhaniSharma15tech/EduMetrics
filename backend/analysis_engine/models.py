from django.db import models
from django.utils import timezone


class analysis_state(models.Model):
    id = models.IntegerField(primary_key=True, default=1)
    current_sem_week = models.IntegerField(default=0)
    current_global_week = models.IntegerField(default=0)
    current_semester = models.IntegerField(default=1)
    last_updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.id = 1  # Ensure singleton
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Analysis at sem_week={self.current_sem_week}, semester={self.current_semester}"


class weekly_metrics(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.CharField(max_length=10)
    class_id = models.CharField(max_length=20)
    semester = models.IntegerField()
    sem_week = models.IntegerField()
    computed_at = models.DateTimeField(auto_now_add=True)

    # Effort score (E_t, 0-100)
    effort_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    library_visits_w = models.IntegerField(default=0)
    book_borrows_w = models.IntegerField(default=0)
    assn_quality_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    assn_plagiarism_max = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    att_rate_recent = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    quiz_submit_rate_recent = models.DecimalField(max_digits=5, decimal_places=4, null=True)
    quiz_avg_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    assn_avg_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    midterm_score_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    # Academic performance (A_t, 0-100)
    weight_m = models.DecimalField(max_digits=4, decimal_places=2, default=0.4)
    weight_n = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    weight_p = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    academic_performance = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    # Risk / trajectory columns
    risk_of_failing = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    recent_quiz_avg_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    midterm_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    endterm_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    quiz_trend = models.DecimalField(max_digits=6, decimal_places=3, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student_id', 'semester', 'sem_week'], name='uq_wm')
        ]
        indexes = [
            models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_wm_class_sem_week'),
            models.Index(fields=['student_id'], name='idx_wm_student'),
        ]

    def __str__(self):
        return f"Metrics for student {self.student_id} in class {self.class_id} at sem {self.semester} week {self.sem_week}"


# Alias so old imports (WeeklyMetrics) continue to work
WeeklyMetrics = weekly_metrics


# ============================================================
#  TABLE: PRE_MID_TERM
#  Predicted midterm score written at sem_week 6 and 7.
#  Matches SQL schema table `pre_mid_term`.
# ============================================================
class pre_mid_term(models.Model):
    id = models.BigAutoField(primary_key=True)
    student_id = models.CharField(max_length=10)
    class_id = models.CharField(max_length=20)
    semester = models.IntegerField()
    sem_week = models.IntegerField()          # 6 or 7
    computed_at = models.DateTimeField(auto_now_add=True)

    predicted_midterm_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['student_id'], name='idx_pmt_student'),
            models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_pmt_class_sem_week'),
        ]

    def __str__(self):
        return (
            f"PreMidTerm for {self.student_id} | sem={self.semester} "
            f"week={self.sem_week} | predicted={self.predicted_midterm_score}"
        )


PreMidTerm = pre_mid_term


# ============================================================
#  TABLE: PRE_END_TERM
#  Predicted endterm score written once at sem_week 17.
#  Matches SQL schema table `pre_end_term`.
# ============================================================
class pre_end_term(models.Model):
    id = models.BigAutoField(primary_key=True)
    student_id = models.CharField(max_length=10)
    class_id = models.CharField(max_length=20)
    semester = models.IntegerField()
    sem_week = models.IntegerField()          # always 17
    computed_at = models.DateTimeField(auto_now_add=True)

    predicted_endterm_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['student_id'], name='idx_pet_student'),
            models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_pet_class_sem_week'),
        ]

    def __str__(self):
        return (
            f"PreEndTerm for {self.student_id} | sem={self.semester} "
            f"week={self.sem_week} | predicted={self.predicted_endterm_score}"
        )


PreEndTerm = pre_end_term


# ============================================================
#  TABLE: RISK_OF_FAILING (dedicated table)
#  Binary risk label from logistic model, week 10 onwards.
#  Separate from weekly_metrics.risk_of_failing column.
# ============================================================
class risk_of_failing_prediction(models.Model):
    id = models.BigAutoField(primary_key=True)
    student_id = models.CharField(max_length=10)
    class_id = models.CharField(max_length=20)
    semester = models.IntegerField()
    sem_week = models.IntegerField()          # 10-17
    computed_at = models.DateTimeField(auto_now_add=True)

    p_fail = models.DecimalField(max_digits=5, decimal_places=4)    # raw probability 0-1
    risk_label = models.CharField(max_length=10)                    # LOW | MEDIUM | HIGH

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student_id', 'semester', 'sem_week'], name='uq_rof')
        ]
        indexes = [
            models.Index(fields=['student_id'], name='idx_rof_student'),
            models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_rof_class_sem_week'),
        ]

    def __str__(self):
        return (
            f"RiskOfFailing for {self.student_id} | sem={self.semester} "
            f"week={self.sem_week} | {self.risk_label} ({self.p_fail})"
        )


RiskOfFailingPrediction = risk_of_failing_prediction


class weekly_flags(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.CharField(max_length=10)
    class_id = models.CharField(max_length=20)
    semester = models.IntegerField()
    sem_week = models.IntegerField()
    computed_at = models.DateTimeField(auto_now_add=True)
    risk_tier = models.CharField(max_length=40)
    urgency_score = models.IntegerField()
    escalation_level = models.IntegerField(default=0)
    archetype = models.CharField(max_length=50, null=True, blank=True)
    diagnosis = models.TextField()
    helpful = models.BooleanField(null=True, default=None)
    feedback_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_wf_class_sem_week'),
            models.Index(fields=['student_id'], name='idx_wf_student'),
        ]

    def __str__(self):
        return f"Flags for student {self.student_id} in class {self.class_id} at sem {self.semester} week {self.sem_week}"


class pre_sem_watchlist(models.Model):
    id = models.BigAutoField(primary_key=True)
    student_id = models.CharField(max_length=20)
    class_id = models.CharField(max_length=20)
    target_semester = models.IntegerField()
    computed_at = models.DateTimeField(auto_now_add=True)
    risk_probability_pct = models.DecimalField(max_digits=5, decimal_places=2)
    escalation_level = models.IntegerField(default=0)
    max_plagiarism = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    att_rate_hist = models.DecimalField(max_digits=5, decimal_places=4)
    assn_rate_hist = models.DecimalField(max_digits=5, decimal_places=4)
    exam_avg_hist = models.DecimalField(max_digits=5, decimal_places=2)
    hard_subject_count = models.IntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student_id', 'target_semester'], name='uq_psw')]
        indexes = [models.Index(fields=['class_id', 'target_semester'], name='idx_psw_class')]

    def __str__(self):
        return f"Pre-sem watchlist for student {self.student_id} in class {self.class_id} for semester {self.target_semester}"


PreSemWatchlist = pre_sem_watchlist


class intervention_log(models.Model):
    id = models.BigAutoField(primary_key=True)
    student_id = models.CharField(max_length=10)
    semester = models.IntegerField()
    sem_week = models.IntegerField()
    logged_at = models.DateTimeField(auto_now_add=True)
    escalation_level = models.IntegerField(default=1)
    trigger_diagnosis = models.TextField(blank=True, default='')
    advisor_notified = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['student_id'], name='idx_il_student'),
            models.Index(fields=['semester', 'sem_week'], name='idx_il_sem_week'),
        ]

    def __str__(self):
        return f"Intervention log for student {self.student_id} at sem {self.semester} week {self.sem_week}"


InterventionLog = intervention_log


class subject_difficulty(models.Model):
    subject_id = models.CharField(max_length=20)
    semester = models.IntegerField()
    computed_at = models.DateTimeField(auto_now_add=True)
    total_students = models.IntegerField()
    students_passed = models.IntegerField()
    pass_rate = models.DecimalField(max_digits=5, decimal_places=4)
    difficulty_label = models.CharField(max_length=20)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['subject_id', 'semester'], name='uq_sd')]

    def __str__(self):
        return f"Difficulty for subject {self.subject_id} in semester {self.semester}: {self.difficulty_label}"


SubjectDifficulty = subject_difficulty


class event_log(models.Model):
    id = models.BigAutoField(primary_key=True)
    event_type = models.CharField(max_length=50)
    triggered_at = models.DateTimeField(auto_now_add=True)
    client_week = models.IntegerField(null=True)
    analysis_week = models.IntegerField(null=True)
    semester = models.IntegerField(null=True)
    status = models.CharField(max_length=10, default='ok')
    error_message = models.TextField(null=True)
    duration_ms = models.IntegerField(null=True)

    def __str__(self):
        return f"Event {self.event_type} triggered at {self.triggered_at} with status {self.status}"
