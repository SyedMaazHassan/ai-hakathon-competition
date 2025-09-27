# apps/hiring/apps.py
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class HiringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.hiring'

    def ready(self):
        logger.info("HiringConfig.ready() called")
        try:
            import apps.hiring.signals
            logger.info("Successfully imported apps.hiring.signals")
        except ImportError as e:
            logger.error(f"Failed to import signals: {e}")
        except Exception as e:
            logger.error(f"Error importing signals: {e}")