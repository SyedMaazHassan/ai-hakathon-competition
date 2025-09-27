from django.db import models
from django.conf import settings


# Create your models here.
User = settings.AUTH_USER_MODEL


class SalesforceCredential(models.Model):
    """
    Model for Store The Data for Salesforce for the user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    signature = models.CharField(max_length=255)
    scope = models.CharField(max_length=255)
    instance_url = models.URLField(max_length=255)
    salesforce_id = models.CharField(max_length=255)
    token_type = models.CharField(max_length=50)
    issued_at = models.BigIntegerField()

    def __str__(self):
        return f"SalesForce Auth for {self.user.username}"



class GoogleDriveCredential(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.URLField()
    scopes = models.TextField()
    expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Google Drive Auth for {self.user.email}"


class ZoomCredential(models.Model):
    """
    Model  for Saving the Zoom credentials in this model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="zoom_token")
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_in = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class GoogleCalendarCredential(models.Model):
    """
    Model for storing Google Calendar OAuth credentials
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.URLField()
    scopes = models.TextField()
    expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Google Calendar Auth for {self.user.email}"