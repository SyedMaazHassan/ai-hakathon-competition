from django.db import models

class Mode(models.TextChoices):
    UNDER_MAINTENANCE = "under_maintenance"
    COMING_SOON = "coming_soon"
    LIVE = "live"
