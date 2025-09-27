"""
Shared enums used across both resume and job parsing models.
These enums represent common concepts that apply to both domains.
"""

from enum import Enum


class VisaSupport(str, Enum):
    # if used by resume parser then means needed
    # if used by job parser then means available
    """Visa support status for resume candidates"""
    NONE = "none" 
    SPONSORSHIP = "sponsorship"
    TRANSFER_ONLY = "transfer_only"
    NOT_SPECIFIED = "not_specified"
    TRANSFER_AND_SPONSORSHIP = "transfer_and_sponsorship"
    OTHER = "other"



class ClearanceLevel(str, Enum):
    """Security clearance levels"""
    NONE = "none"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"
    OTHER = "other"
    NOT_SPECIFIED = "not_specified"


class SkillLevel(str, Enum):
    """Standardized skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    NATIVE = "native"  # For languages


class EducationLevel(str, Enum):
    """Standardized education levels"""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    PROFESSIONAL = "professional"  # JD, MD, etc.
    CERTIFICATE = "certificate"
    DIPLOMA = "diploma"


class EmploymentType(str, Enum):
    """Types of employment arrangements"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"
    VOLUNTEER = "volunteer"
    NOT_SPECIFIED = "not_specified"
    OTHER = "other"


class WorkLocationType(str, Enum):
    """Work location arrangements"""
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    NOT_SPECIFIED = "not_specified"
    OTHER = "other"


class SeniorityLevel(str, Enum):
    """Career seniority levels"""
    INTERN = "intern"
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    EXECUTIVE = "executive"
    OTHER = "other"
    NOT_SPECIFIED = "not_specified"


class Currency(str, Enum):
    """Currency codes for compensation"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    AED = "AED"
    SAR = "SAR"
    PKR = "PKR"
    OTHER = "other"


class PayPeriod(str, Enum):
    """Payment frequency periods"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    OTHER = "other"
    ONE_TIME = "one_time"
