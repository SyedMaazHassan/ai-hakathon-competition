from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import timedelta

from .models import (
    City, Location, Department, DepartmentEntity, CitizenRequest,
    CitizenRequestAssignment, ActionLog, EmergencyCall, Appointment,
    SystemConfiguration, RequestFeedback, NotificationLog
)
from .choices import *


# =============================================================================
# CUSTOM FILTERS
# =============================================================================

class UrgencyFilter(SimpleListFilter):
    title = 'urgency level'
    parameter_name = 'urgency'

    def lookups(self, request, model_admin):
        return UrgencyLevel.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(urgency_level=self.value())
        return queryset


class EmergencyFilter(SimpleListFilter):
    title = 'emergency status'
    parameter_name = 'emergency'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Emergency Cases'),
            ('no', 'Non-Emergency Cases'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_emergency=True)
        elif self.value() == 'no':
            return queryset.filter(is_emergency=False)
        return queryset


class RecentFilter(SimpleListFilter):
    title = 'time period'
    parameter_name = 'time_period'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('week', 'Last 7 days'),
            ('month', 'Last 30 days'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        elif self.value() == 'week':
            return queryset.filter(created_at__gte=now - timedelta(days=7))
        elif self.value() == 'month':
            return queryset.filter(created_at__gte=now - timedelta(days=30))
        return queryset


# =============================================================================
# INLINE ADMIN CLASSES
# =============================================================================

class LocationInline(admin.TabularInline):
    model = Location
    extra = 0
    fields = ('area', 'lat', 'lng', 'formatted_address')
    readonly_fields = ('formatted_address',)


class DepartmentEntityInline(admin.TabularInline):
    model = DepartmentEntity
    extra = 0
    fields = ('name', 'type', 'city', 'phone', 'capacity', 'is_active')
    readonly_fields = ('name', 'type', 'city', 'phone', 'capacity', 'is_active')


class CitizenRequestAssignmentInline(admin.TabularInline):
    model = CitizenRequestAssignment
    extra = 0
    fields = ('department_entity', 'status', 'assignment_notes', 'assigned_at')
    readonly_fields = ('assigned_at',)


class ActionLogInline(admin.TabularInline):
    model = ActionLog
    extra = 0
    fields = ('action_type', 'description', 'success', 'created_at')
    readonly_fields = ('created_at',)


class EmergencyCallInline(admin.TabularInline):
    model = EmergencyCall
    extra = 0
    fields = ('department', 'phone_number', 'status', 'initiated_at', 'duration_seconds')
    readonly_fields = ('initiated_at',)


class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    fields = ('department', 'entity', 'scheduled_at', 'status', 'duration_minutes')
    readonly_fields = ('scheduled_at',)


class NotificationLogInline(admin.TabularInline):
    model = NotificationLog
    extra = 0
    fields = ('notification_type', 'recipient', 'sent_successfully', 'sent_at')
    readonly_fields = ('sent_at',)


# =============================================================================
# MAIN ADMIN CLASSES
# =============================================================================

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'is_major_city', 'location_count')
    list_filter = ('province', 'is_major_city')
    search_fields = ('name',)
    list_editable = ('is_major_city',)
    inlines = [LocationInline]

    def location_count(self, obj):
        return obj.locations.count()
    location_count.short_description = 'Locations'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            location_count=Count('locations')
        )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('area', 'city', 'formatted_address', 'has_coordinates')
    list_filter = ('city__province', 'city')
    search_fields = ('area', 'city__name', 'formatted_address')
    autocomplete_fields = ('city',)

    def has_coordinates(self, obj):
        return bool(obj.lat and obj.lng)
    has_coordinates.boolean = True
    has_coordinates.short_description = 'Has Coordinates'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_24x7', 'response_time_minutes', 'entity_count', 'is_active')
    list_filter = ('category', 'is_24x7', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    inlines = [DepartmentEntityInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Contact Information', {
            'fields': ('main_phone', 'main_email', 'emergency_number')
        }),
        ('Operational Details', {
            'fields': ('is_24x7', 'response_time_minutes', 'logo')
        }),
        ('System', {
            'fields': ('is_active',)
        }),
    )

    def entity_count(self, obj):
        return obj.entities.count()
    entity_count.short_description = 'Entities'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            entity_count=Count('entities')
        )


@admin.register(DepartmentEntity)
class DepartmentEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'department', 'city', 'capacity', 'is_active')
    list_filter = ('type', 'department__category', 'city__province', 'is_active')
    search_fields = ('name', 'department__name', 'city__name')
    autocomplete_fields = ('department', 'city', 'location')
    list_editable = ('is_active',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'department', 'city', 'location')
        }),
        ('Contact & Services', {
            'fields': ('phone', 'services')
        }),
        ('Capacity', {
            'fields': ('capacity',)
        }),
        ('System', {
            'fields': ('is_active',)
        }),
    )


@admin.register(CitizenRequest)
class CitizenRequestAdmin(admin.ModelAdmin):
    list_display = (
        'case_code', 'user_link', 'category', 'urgency_badge', 'status_badge',
        'is_emergency', 'assigned_department', 'created_at', 'confidence_score'
    )
    list_filter = (
        'status', 'category', UrgencyFilter, EmergencyFilter, RecentFilter,
        'assigned_department', 'triage_source', 'created_at'
    )
    search_fields = ('case_code', 'user__first_name', 'user__last_name', 'request_text')
    autocomplete_fields = ('user', 'assigned_department', 'assigned_entity', 'target_location')
    readonly_fields = ('case_code', 'created_at', 'updated_at', 'confidence_score')
    date_hierarchy = 'created_at'
    inlines = [
        CitizenRequestAssignmentInline, ActionLogInline, EmergencyCallInline,
        AppointmentInline, NotificationLogInline
    ]

    fieldsets = (
        ('Request Information', {
            'fields': ('case_code', 'user', 'request_text', 'target_location')
        }),
        ('AI Analysis', {
            'fields': ('category', 'urgency_level', 'confidence_score', 'triage_source', 'ai_response')
        }),
        ('Assignment', {
            'fields': ('assigned_department', 'assigned_entity')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'is_emergency', 'degraded_mode_used')
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'expected_response_time')
        }),
    )

    def user_link(self, obj):
        url = reverse('admin:authentication_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'User'

    def urgency_badge(self, obj):
        if not obj.urgency_level:
            return '-'
        colors = {
            UrgencyLevel.LOW: 'green',
            UrgencyLevel.MEDIUM: 'orange',
            UrgencyLevel.HIGH: 'red',
            UrgencyLevel.CRITICAL: 'darkred'
        }
        color = colors.get(obj.urgency_level, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_urgency_level_display()
        )
    urgency_badge.short_description = 'Urgency'

    def status_badge(self, obj):
        colors = {
            CaseStatus.SUBMITTED: 'blue',
            CaseStatus.ANALYZING: 'orange',
            CaseStatus.ROUTING: 'purple',
            CaseStatus.ASSIGNED: 'green',
            CaseStatus.IN_PROGRESS: 'darkgreen',
            CaseStatus.RESOLVED: 'gray',
            CaseStatus.CLOSED: 'black',
            CaseStatus.ESCALATED: 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'assigned_department', 'assigned_entity', 'target_location__city'
        )

    actions = ['mark_as_resolved', 'escalate_requests', 'assign_emergency_priority']

    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status=CaseStatus.RESOLVED, resolved_at=timezone.now())
        self.message_user(request, f'{updated} requests marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected requests as resolved'

    def escalate_requests(self, request, queryset):
        updated = queryset.update(status=CaseStatus.ESCALATED)
        self.message_user(request, f'{updated} requests escalated.')
    escalate_requests.short_description = 'Escalate selected requests'

    def assign_emergency_priority(self, request, queryset):
        updated = queryset.update(urgency_level=UrgencyLevel.CRITICAL, is_emergency=True)
        self.message_user(request, f'{updated} requests assigned emergency priority.')
    assign_emergency_priority.short_description = 'Assign emergency priority'


@admin.register(CitizenRequestAssignment)
class CitizenRequestAssignmentAdmin(admin.ModelAdmin):
    list_display = ('citizen_request', 'department_entity', 'status', 'assigned_at', 'resolved_at')
    list_filter = ('status', 'assigned_at', 'department_entity__type')
    search_fields = ('citizen_request__case_code', 'department_entity__name')
    autocomplete_fields = ('citizen_request', 'department_entity')
    readonly_fields = ('assigned_at',)


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('citizen_request', 'action_type', 'agent_type', 'success', 'created_at', 'duration_seconds')
    list_filter = ('action_type', 'agent_type', 'success', 'created_at')
    search_fields = ('citizen_request__case_code', 'description')
    autocomplete_fields = ('citizen_request',)
    readonly_fields = ('created_at', 'completed_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('citizen_request')


@admin.register(EmergencyCall)
class EmergencyCallAdmin(admin.ModelAdmin):
    list_display = ('citizen_request', 'department', 'phone_number', 'status', 'initiated_at', 'duration_seconds')
    list_filter = ('status', 'department', 'initiated_at')
    search_fields = ('citizen_request__case_code', 'phone_number', 'call_id')
    autocomplete_fields = ('citizen_request', 'department')
    readonly_fields = ('initiated_at', 'answered_at', 'completed_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('citizen_request', 'department')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('citizen_request', 'department', 'entity', 'scheduled_at', 'status', 'duration_minutes')
    list_filter = ('status', 'department', 'scheduled_at')
    search_fields = ('citizen_request__case_code', 'department__name')
    autocomplete_fields = ('citizen_request', 'department', 'entity')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('citizen_request', 'department', 'entity')


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_preview', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('key', 'description')
    list_editable = ('is_active',)

    def value_preview(self, obj):
        return obj.value[:50] + '...' if len(obj.value) > 50 else obj.value
    value_preview.short_description = 'Value Preview'


@admin.register(RequestFeedback)
class RequestFeedbackAdmin(admin.ModelAdmin):
    list_display = ('citizen_request', 'overall_rating', 'response_time_rating', 'accuracy_rating', 'would_recommend', 'created_at')
    list_filter = ('overall_rating', 'would_recommend', 'created_at')
    search_fields = ('citizen_request__case_code', 'comment')
    autocomplete_fields = ('citizen_request',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('citizen_request')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('citizen_request', 'notification_type', 'recipient', 'sent_successfully', 'sent_at', 'delivered_at')
    list_filter = ('notification_type', 'sent_successfully', 'sent_at')
    search_fields = ('citizen_request__case_code', 'recipient', 'subject')
    autocomplete_fields = ('citizen_request',)
    readonly_fields = ('sent_at', 'delivered_at', 'read_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('citizen_request')


# =============================================================================
# ADMIN SITE CUSTOMIZATION
# =============================================================================

admin.site.site_header = "AI Hackathon - Department Management System"
admin.site.site_title = "Dept Admin"
admin.site.index_title = "Department Management Administration"
