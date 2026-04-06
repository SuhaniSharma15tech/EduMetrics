# Generated migration — adds all analysis_engine tables including
# the new pre_mid_term, pre_end_term, risk_of_failing_prediction tables.

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        # ── analysis_state (singleton) ─────────────────────────
        migrations.CreateModel(
            name='analysis_state',
            fields=[
                ('id', models.IntegerField(default=1, primary_key=True, serialize=False)),
                ('current_sem_week', models.IntegerField(default=0)),
                ('current_global_week', models.IntegerField(default=0)),
                ('current_semester', models.IntegerField(default=1)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),

        # ── weekly_metrics ─────────────────────────────────────
        migrations.CreateModel(
            name='weekly_metrics',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('student_id', models.CharField(max_length=10)),
                ('class_id', models.CharField(max_length=20)),
                ('semester', models.IntegerField()),
                ('sem_week', models.IntegerField()),
                ('computed_at', models.DateTimeField(auto_now_add=True)),
                ('effort_score', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('library_visits_w', models.IntegerField(default=0)),
                ('book_borrows_w', models.IntegerField(default=0)),
                ('assn_quality_avg', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('assn_plagiarism_max', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('att_rate_recent', models.DecimalField(decimal_places=4, max_digits=5, null=True)),
                ('quiz_submit_rate_recent', models.DecimalField(decimal_places=4, max_digits=5, null=True)),
                ('quiz_avg_pct', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('assn_avg_pct', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('midterm_score_pct', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('weight_m', models.DecimalField(decimal_places=2, default=0.4, max_digits=4)),
                ('weight_n', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('weight_p', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('academic_performance', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('risk_of_failing', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('recent_quiz_avg_pct', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('midterm_pct', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('endterm_pct', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
                ('quiz_trend', models.DecimalField(decimal_places=3, max_digits=6, null=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name='weekly_metrics',
            constraint=models.UniqueConstraint(fields=['student_id', 'semester', 'sem_week'], name='uq_wm'),
        ),
        migrations.AddIndex(
            model_name='weekly_metrics',
            index=models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_wm_class_sem_week'),
        ),
        migrations.AddIndex(
            model_name='weekly_metrics',
            index=models.Index(fields=['student_id'], name='idx_wm_student'),
        ),

        # ── pre_mid_term (NEW) ─────────────────────────────────
        migrations.CreateModel(
            name='pre_mid_term',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('student_id', models.CharField(max_length=10)),
                ('class_id', models.CharField(max_length=20)),
                ('semester', models.IntegerField()),
                ('sem_week', models.IntegerField()),
                ('computed_at', models.DateTimeField(auto_now_add=True)),
                ('predicted_midterm_score', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='pre_mid_term',
            index=models.Index(fields=['student_id'], name='idx_pmt_student'),
        ),
        migrations.AddIndex(
            model_name='pre_mid_term',
            index=models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_pmt_class_sem_week'),
        ),

        # ── pre_end_term (NEW) ─────────────────────────────────
        migrations.CreateModel(
            name='pre_end_term',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('student_id', models.CharField(max_length=10)),
                ('class_id', models.CharField(max_length=20)),
                ('semester', models.IntegerField()),
                ('sem_week', models.IntegerField()),
                ('computed_at', models.DateTimeField(auto_now_add=True)),
                ('predicted_endterm_score', models.DecimalField(decimal_places=2, max_digits=5, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='pre_end_term',
            index=models.Index(fields=['student_id'], name='idx_pet_student'),
        ),
        migrations.AddIndex(
            model_name='pre_end_term',
            index=models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_pet_class_sem_week'),
        ),

        # ── risk_of_failing_prediction (NEW) ───────────────────
        migrations.CreateModel(
            name='risk_of_failing_prediction',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('student_id', models.CharField(max_length=10)),
                ('class_id', models.CharField(max_length=20)),
                ('semester', models.IntegerField()),
                ('sem_week', models.IntegerField()),
                ('computed_at', models.DateTimeField(auto_now_add=True)),
                ('p_fail', models.DecimalField(decimal_places=4, max_digits=5)),
                ('risk_label', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddConstraint(
            model_name='risk_of_failing_prediction',
            constraint=models.UniqueConstraint(fields=['student_id', 'semester', 'sem_week'], name='uq_rof'),
        ),
        migrations.AddIndex(
            model_name='risk_of_failing_prediction',
            index=models.Index(fields=['student_id'], name='idx_rof_student'),
        ),
        migrations.AddIndex(
            model_name='risk_of_failing_prediction',
            index=models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_rof_class_sem_week'),
        ),

        # ── weekly_flags ───────────────────────────────────────
        migrations.CreateModel(
            name='weekly_flags',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('student_id', models.CharField(max_length=10)),
                ('class_id', models.CharField(max_length=20)),
                ('semester', models.IntegerField()),
                ('sem_week', models.IntegerField()),
                ('computed_at', models.DateTimeField(auto_now_add=True)),
                ('risk_tier', models.CharField(max_length=40)),
                ('urgency_score', models.IntegerField()),
                ('escalation_level', models.IntegerField(default=0)),
                ('archetype', models.CharField(blank=True, max_length=50, null=True)),
                ('diagnosis', models.TextField()),
                ('helpful', models.BooleanField(default=None, null=True)),
                ('feedback_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name='weekly_flags',
            index=models.Index(fields=['class_id', 'semester', 'sem_week'], name='idx_wf_class_sem_week'),
        ),
        migrations.AddIndex(
            model_name='weekly_flags',
            index=models.Index(fields=['student_id'], name='idx_wf_student'),
        ),

        # ── pre_sem_watchlist ──────────────────────────────────
        migrations.CreateModel(
            name='pre_sem_watchlist',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('student_id', models.CharField(max_length=20)),
                ('class_id', models.CharField(max_length=20)),
                ('target_semester', models.IntegerField()),
                ('computed_at', models.DateTimeField(auto_now_add=True)),
                ('risk_probability_pct', models.DecimalField(decimal_places=2, max_digits=5)),
                ('escalation_level', models.IntegerField(default=0)),
                ('max_plagiarism', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('att_rate_hist', models.DecimalField(decimal_places=4, max_digits=5)),
                ('assn_rate_hist', models.DecimalField(decimal_places=4, max_digits=5)),
                ('exam_avg_hist', models.DecimalField(decimal_places=2, max_digits=5)),
                ('hard_subject_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddConstraint(
            model_name='pre_sem_watchlist',
            constraint=models.UniqueConstraint(fields=['student_id', 'target_semester'], name='uq_psw'),
        ),
        migrations.AddIndex(
            model_name='pre_sem_watchlist',
            index=models.Index(fields=['class_id', 'target_semester'], name='idx_psw_class'),
        ),

        # ── intervention_log ───────────────────────────────────
        migrations.CreateModel(
            name='intervention_log',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('student_id', models.CharField(max_length=10)),
                ('semester', models.IntegerField()),
                ('sem_week', models.IntegerField()),
                ('logged_at', models.DateTimeField(auto_now_add=True)),
                ('escalation_level', models.IntegerField(default=1)),
                ('trigger_diagnosis', models.TextField(blank=True, default='')),
                ('advisor_notified', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.AddIndex(
            model_name='intervention_log',
            index=models.Index(fields=['student_id'], name='idx_il_student'),
        ),
        migrations.AddIndex(
            model_name='intervention_log',
            index=models.Index(fields=['semester', 'sem_week'], name='idx_il_sem_week'),
        ),

        # ── subject_difficulty ─────────────────────────────────
        migrations.CreateModel(
            name='subject_difficulty',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('subject_id', models.CharField(max_length=20)),
                ('semester', models.IntegerField()),
                ('computed_at', models.DateTimeField(auto_now_add=True)),
                ('total_students', models.IntegerField()),
                ('students_passed', models.IntegerField()),
                ('pass_rate', models.DecimalField(decimal_places=4, max_digits=5)),
                ('difficulty_label', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddConstraint(
            model_name='subject_difficulty',
            constraint=models.UniqueConstraint(fields=['subject_id', 'semester'], name='uq_sd'),
        ),

        # ── event_log ──────────────────────────────────────────
        migrations.CreateModel(
            name='event_log',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('event_type', models.CharField(max_length=50)),
                ('triggered_at', models.DateTimeField(auto_now_add=True)),
                ('client_week', models.IntegerField(null=True)),
                ('analysis_week', models.IntegerField(null=True)),
                ('semester', models.IntegerField(null=True)),
                ('status', models.CharField(default='ok', max_length=10)),
                ('error_message', models.TextField(null=True)),
                ('duration_ms', models.IntegerField(null=True)),
            ],
        ),
    ]
