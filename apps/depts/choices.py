from django.db import models

class Province(models.TextChoices):
    PUNJAB = "punjab", "Punjab"
    SINDH = "sindh", "Sindh"
    KP = "kp", "Khyber Pakhtunkhwa"
    BALOCHISTAN = "balochistan", "Balochistan"
    ICT = "ict", "Islamabad Capital Territory"
    GB = "gb", "Gilgit-Baltistan"
    AJK = "ajk", "Azad Jammu & Kashmir"

class EntityType(models.TextChoices):
    HOSPITAL = "hospital", "Hospital"
    POLICE_STATION = "police_station", "Police Station"
    FIRE_STATION = "fire_station", "Fire Station"
    OFFICE = "office", "Office Building"
    SERVICE_CENTER = "service_center", "Service Center"
    CLINIC = "clinic", "Clinic"
    HEADQUARTERS = "headquarters", "Headquarters"

class DepartmentCategory(models.TextChoices):
    POLICE = "police", "Police"
    FIRE_BRIGADE = "fire_brigade", "Fire Brigade"
    AMBULANCE = "ambulance", "Ambulance/Medical Emergency"
    SEWERAGE = "sewerage", "Sewerage & Water"
    ELECTRICITY = "electricity", "Electricity"
    GAS = "gas", "Gas Company"
    BOMB_DISPOSAL = "bomb_disposal", "Bomb Disposal"
    NADRA = "nadra", "NADRA"
    HEALTH = "health", "Health Department"
    MUNICIPAL = "municipal", "Municipal Services"
    TRAFFIC_POLICE = "traffic_police", "Traffic Police"
    CYBERCRIME = "cybercrime", "Cybercrime"
    DISASTER_MGMT = "disaster_mgmt", "Disaster Management"

class UrgencyLevel(models.TextChoices):
    LOW = "low", "Low Priority"
    MEDIUM = "medium", "Medium Priority"
    HIGH = "high", "High Priority"
    CRITICAL = "critical", "Critical Emergency"

class CaseStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    ANALYZING = "analyzing", "AI Analysis in Progress"
    ROUTING = "routing", "Routing to Department"
    ASSIGNED = "assigned", "Assigned to Department"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"
    ESCALATED = "escalated", "Escalated"

class TriageSource(models.TextChoices):
    LLM = "llm", "AI/LLM Analysis"
    RULES = "rules", "Rule-based System"
    MANUAL = "manual", "Manual Assignment"
    FALLBACK = "fallback", "Fallback/Degraded Mode"

class ActionType(models.TextChoices):
    ANALYSIS = "analysis", "AI Analysis"
    CATEGORIZATION = "categorization", "Category Detection"
    LOCATION_MAPPING = "location_mapping", "Location Mapping"
    DEPARTMENT_ASSIGNMENT = "dept_assignment", "Department Assignment"
    EMAIL_SENT = "email", "Email Notification"
    SMS_SENT = "sms", "SMS Notification"
    EMERGENCY_CALL = "call", "Emergency Call"
    APPOINTMENT_BOOKED = "booking", "Appointment Booked"
    ESCALATION = "escalation", "Request Escalated"

class CallStatus(models.TextChoices):
    INITIATED = "initiated", "Call Initiated"
    RINGING = "ringing", "Ringing"
    ANSWERED = "answered", "Call Answered"
    COMPLETED = "completed", "Call Completed"
    FAILED = "failed", "Call Failed"
    BUSY = "busy", "Line Busy"
    NO_ANSWER = "no_answer", "No Answer"

class AppointmentStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"
    NO_SHOW = "no_show", "No Show"

class AgentType(models.TextChoices):
    REQUEST_ANALYSIS = "request_analysis", "Request Analysis Agent"
    LOCATION_MAPPING = "location_mapping", "Location Mapping Agent"
    TRIAGE_AGENT = "triage", "Triage Agent"
    ESCALATION_AGENT = "escalation", "Escalation Agent"
    COMMUNICATION_AGENT = "communication", "Communication Agent"