from django.core.management.base import BaseCommand
from analysis_engine.weekly_metrics_calculator import run as run_metrics
from analysis_engine.flagging import run as run_flagging
from analysis_engine.pre_mid_term import run as run_pre_mid
from analysis_engine.pre_end_term import run as run_pre_end
from analysis_engine.pre_sem import run as run_pre_sem


class Command(BaseCommand):
    help = 'Run weekly EduMetrics analysis pipeline (metrics → flagging → event scripts)'

    def handle(self, *args, **kwargs):
        self.stdout.write('=' * 60)
        self.stdout.write('Running weekly EduMetrics analysis pipeline...')
        self.stdout.write('=' * 60)

        self.stdout.write('\n[1/5] Weekly metrics calculator...')
        run_metrics()

        self.stdout.write('\n[2/5] Flagging engine...')
        run_flagging()

        self.stdout.write('\n[3/5] Pre-midterm prediction (fires at weeks 6 & 7)...')
        run_pre_mid()

        self.stdout.write('\n[4/5] Pre-endterm prediction (fires at week 17)...')
        run_pre_end()

        self.stdout.write('\n[5/5] Pre-semester watchlist (fires at semester boundary)...')
        run_pre_sem()

        self.stdout.write('\nDone.')
