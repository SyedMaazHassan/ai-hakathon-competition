from django.db import models
from django.utils.crypto import get_random_string
from django.core.validators import RegexValidator
import uuid
from .choices import *
from apps.core.models import BaseModel

# =============================================================================
# CORE GEOGRAPHIC MODELS
# =============================================================================

class City(BaseModel):
    PREFIX = "CITY"
    
    name = models.CharField(max_length=120)
    province = models.CharField(max_length=20, choices=Province.choices)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_major_city = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ("name", "province")
        indexes = [models.Index(fields=["name", "province"])]
        verbose_name_plural = "Cities"
    
    def __str__(self):
        return f"{self.name}, {self.get_province_display()}"

class Location(BaseModel):
    """Location model for incident locations"""
    PREFIX = "LOC"
    
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    area = models.CharField(max_length=160, blank=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="locations")
    raw_address = models.CharField(max_length=255, blank=True)
    
    # Google Maps integration
    place_id = models.CharField(max_length=200, blank=True)
    formatted_address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.area}, {self.city.name}" if self.area else str(self.city)

# =============================================================================
# DEPARTMENT & ENTITY MODELS
# =============================================================================

class Department(BaseModel):
    PREFIX = "DEPT"
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=32, choices=DepartmentCategory.choices)
    description = models.TextField(blank=True)
    
    # Contact Information
    main_phone = models.CharField(max_length=40, blank=True)
    main_email = models.EmailField(blank=True)
    emergency_number = models.CharField(max_length=20, blank=True)  # For critical emergencies
    
    # Visual & Branding
    logo = models.URLField(blank=True)
    
    # Operational Details
    is_24x7 = models.BooleanField(default=False)
    response_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # System Fields
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    class Meta:
        indexes = [models.Index(fields=["category", "is_active"])]



class DepartmentEntity(BaseModel):
    """Physical entities like hospitals, police stations, offices"""
    PREFIX = "ENT"
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=24, choices=EntityType.choices)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="entities")
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="entities")
    location = models.OneToOneField(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Contact & Services
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True, help_text="Primary contact email for this entity")
    services = models.JSONField(default=dict, blank=True)  # Available services, hours, etc.
    
    # Capacity & Details
    capacity = models.PositiveIntegerField(null=True, blank=True)  # beds, staff, etc.
    
    # System Fields
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["city", "type"]),
            models.Index(fields=["department", "is_active"])
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"



# =============================================================================
# REQUEST SYSTEM
# =============================================================================

def new_case_code():
    """Generate unique case code like C-AB12CD34"""
    return f"C-{get_random_string(8, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')}"

class CitizenRequest(BaseModel):
    """Main request model"""
    PREFIX = "REQ"
    
    # Identifiers
    case_code = models.CharField(max_length=12, default=new_case_code, editable=False, db_index=True, unique=True)
    
    # Request Details
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name="requests")
    request_text = models.TextField()
    
    # AI Analysis Results
    category = models.CharField(max_length=32, choices=DepartmentCategory.choices, blank=True)
    urgency_level = models.CharField(max_length=12, choices=UrgencyLevel.choices, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)  # AI confidence 0-1
    triage_source = models.CharField(max_length=8, choices=TriageSource.choices, default=TriageSource.LLM)
    ai_response = models.TextField(blank=True)  # AI reasoning/summary
    
    # Location (captured at request time)
    target_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Assignment
    assigned_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_entity = models.ForeignKey(DepartmentEntity, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status & Tracking
    status = models.CharField(max_length=16, choices=CaseStatus.choices, default=CaseStatus.SUBMITTED, db_index=True)
    
    # Timing
    resolved_at = models.DateTimeField(null=True, blank=True)
    expected_response_time = models.DateTimeField(null=True, blank=True)
    
    # Flags
    degraded_mode_used = models.BooleanField(default=False)  # If AI failed, used fallback
    is_emergency = models.BooleanField(default=False)  # For quick filtering
    
    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["urgency_level"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_emergency", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Auto-set emergency flag for critical cases
        if self.urgency_level == UrgencyLevel.CRITICAL:
            self.is_emergency = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.case_code} - {self.user.get_full_name()}"

# =============================================================================
# ASSIGNMENT & TRACKING
# =============================================================================

class CitizenRequestAssignment(BaseModel):
    """Track assignments to specific entities"""
    PREFIX = "ASG"
    
    citizen_request = models.ForeignKey(CitizenRequest, on_delete=models.CASCADE, related_name="assignments")
    department_entity = models.ForeignKey(DepartmentEntity, on_delete=models.PROTECT, related_name="assignments")
    status = models.CharField(max_length=16, choices=CaseStatus.choices, default=CaseStatus.ASSIGNED)
    
    # Notes & Details
    assignment_notes = models.TextField(blank=True)
    priority_override = models.CharField(max_length=12, choices=UrgencyLevel.choices, blank=True)
    
    # Timing
    assigned_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.citizen_request.case_code} → {self.department_entity.name}"

# =============================================================================
# AI AGENT ACTIONS & COMMUNICATION
# =============================================================================

class ActionLog(BaseModel):
    """Track all actions taken by AI agents"""
    PREFIX = "ACT"
    
    citizen_request = models.ForeignKey(CitizenRequest, on_delete=models.CASCADE, related_name="actions")
    agent_type = models.CharField(max_length=20, choices=AgentType.choices, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    
    # Action Details
    description = models.TextField()
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)  # Store action-specific data
    
    # Timing
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["citizen_request", "created_at"]),
            models.Index(fields=["action_type", "success"]),
        ]
    
    def __str__(self):
        return f"{self.citizen_request.case_code} - {self.get_action_type_display()}"

class EmergencyCall(BaseModel):
    """Track emergency calls made via VAPI"""
    PREFIX = "CALL"
    
    citizen_request = models.ForeignKey(CitizenRequest, on_delete=models.CASCADE, related_name="emergency_calls")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    # VAPI Call Details
    call_id = models.CharField(max_length=100, blank=True)  # VAPI call ID
    phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=CallStatus.choices, default=CallStatus.INITIATED)
    
    # Call Content
    script_used = models.TextField(blank=True)
    message_sent = models.TextField(blank=True)
    response_received = models.TextField(blank=True)
    
    # Timing & Duration
    initiated_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)  # VAPI response data
    
    def __str__(self):
        return f"Call - {self.citizen_request.case_code} to {self.department.name}"

class Appointment(BaseModel):
    """Track appointments booked via Google Calendar"""
    PREFIX = "APT"
    
    citizen_request = models.ForeignKey(CitizenRequest, on_delete=models.CASCADE, related_name="appointments")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    entity = models.ForeignKey(DepartmentEntity, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Google Calendar Integration
    calendar_event_id = models.CharField(max_length=100, blank=True)
    calendar_link = models.URLField(blank=True)
    
    # Appointment Details
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    location_details = models.TextField(blank=True)
    
    # Status & Notes
    status = models.CharField(max_length=20, choices=AppointmentStatus.choices, default=AppointmentStatus.SCHEDULED)
    notes = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Appointment - {self.citizen_request.case_code} at {self.scheduled_at.strftime('%Y-%m-%d %H:%M')}"

# =============================================================================
# SYSTEM CONFIGURATION & FEEDBACK
# =============================================================================

class SystemConfiguration(BaseModel):
    """System-wide configuration settings"""
    PREFIX = "CONF"
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Categorization
    category = models.CharField(max_length=50, default='general')  # ai, communication, etc.
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

class RequestFeedback(BaseModel):
    """User feedback on request handling"""
    PREFIX = "FB"
    
    citizen_request = models.OneToOneField(CitizenRequest, on_delete=models.CASCADE, related_name="feedback")
    
    # Overall Rating
    overall_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    
    # Specific Ratings
    response_time_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    accuracy_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    communication_rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    # Comments
    comment = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    
    # Flags
    would_recommend = models.BooleanField(null=True, blank=True)
    
    def __str__(self):
        return f"Feedback for {self.citizen_request.case_code} - {self.overall_rating}★"

# =============================================================================
# NOTIFICATION & COMMUNICATION TRACKING
# =============================================================================

class NotificationLog(BaseModel):
    """Track all notifications sent"""
    PREFIX = "NOTIF"
    
    citizen_request = models.ForeignKey(CitizenRequest, on_delete=models.CASCADE, related_name="notifications")
    
    # Notification Details
    notification_type = models.CharField(max_length=20, choices=ActionType.choices)
    recipient = models.CharField(max_length=200)  # email, phone, etc.
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    
    # Status
    sent_successfully = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # External IDs
    external_id = models.CharField(max_length=100, blank=True)  # SMS ID, email ID, etc.
    
    # Timing
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_notification_type_display()} to {self.recipient}"