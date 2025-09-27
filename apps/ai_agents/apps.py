from django.apps import AppConfig


class AiAgentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_agents'

    def ready(self):
        import apps.ai_agents.signals