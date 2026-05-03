from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis_engine', '0007_remove_intervention_log_escalation_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='weekly_metrics',
            name='risk_score',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='weekly_metrics',
            name='escalation_level',
            field=models.IntegerField(default=0),
        ),
    ]
