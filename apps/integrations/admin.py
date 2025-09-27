from django.contrib import admin

from apps.integrations.models import ZoomCredential
from apps.integrations.models import SalesforceCredential, GoogleDriveCredential, GoogleCalendarCredential


# Register your models here.
@admin.register(SalesforceCredential)
class SalesForceModelAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'salesforce_id',
        'instance_url',
        'token_type',
        'issued_at',
    )
    search_fields = ('user__username', 'salesforce_id', 'instance_url')
    list_filter = ('token_type',)
    readonly_fields = (
        'signature',
        'issued_at',
    )

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        return [f for f in fields if f not in ("access_token", "refresh_token")]

@admin.register(ZoomCredential)
class ZoomCredentialAdmin(admin.ModelAdmin):
    list_display = ("user", )

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        return [f for f in fields if f not in ("access_token", "refresh_token")]


@admin.register(GoogleDriveCredential)
class GoogleDriveCredentialAdmin(admin.ModelAdmin):
    list_display = ("user", )
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        return [f for f in fields if f not in ("access_token", "refresh_token")]


@admin.register(GoogleCalendarCredential)
class GoogleCalendarCredentialAdmin(admin.ModelAdmin):
    list_display = ("user", )
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        return [f for f in fields if f not in ("access_token", "refresh_token")]