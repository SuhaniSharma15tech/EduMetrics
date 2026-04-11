from django.apps import AppConfig

class AnalysisEngineConfig(AppConfig):
    name = 'analysis_engine'

    def ready(self):
        from .calibrate_analysis_db import calibrate
        calibrate()  # Calibrate on startup (can be removed later if not needed)
        # from .scheduler import start,run_weekly
        # run_weekly()
        # start()