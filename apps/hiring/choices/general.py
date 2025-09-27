from django.db import models


class VisaSupport(models.TextChoices):
    """Visa support availability/requirement"""
    NONE = "none", "None"
    SPONSORSHIP = "sponsorship", "Sponsorship"
    TRANSFER_ONLY = "transfer_only", "Transfer Only"
    NOT_SPECIFIED = "not_specified", "Not Specified"
    TRANSFER_AND_SPONSORSHIP = "transfer_and_sponsorship", "Transfer and Sponsorship"
    OTHER = "other", "Other"


class ClearanceLevel(models.TextChoices):
    """Security clearance levels"""
    NONE = "none", "None"
    CONFIDENTIAL = "confidential", "Confidential"
    SECRET = "secret", "Secret"
    TOP_SECRET = "top_secret", "Top Secret"
    OTHER = "other", "Other"
    NOT_SPECIFIED = "not_specified", "Not Specified"


class SkillLevel(models.TextChoices):
    """Skill proficiency levels"""
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"
    EXPERT = "expert", "Expert"
    NATIVE = "native", "Native"


class EducationLevel(models.TextChoices):
    """Education attainment levels"""
    HIGH_SCHOOL = "high_school", "High School"
    ASSOCIATE = "associate", "Associate"
    BACHELOR = "bachelor", "Bachelor"
    MASTER = "master", "Master"
    DOCTORATE = "doctorate", "Doctorate"
    PROFESSIONAL = "professional", "Professional"
    CERTIFICATE = "certificate", "Certificate"
    DIPLOMA = "diploma", "Diploma"


class EmploymentType(models.TextChoices):
    """Types of employment arrangements"""
    FULL_TIME = "full_time", "Full Time"
    PART_TIME = "part_time", "Part Time"
    CONTRACT = "contract", "Contract"
    INTERNSHIP = "internship", "Internship"
    FREELANCE = "freelance", "Freelance"
    TEMPORARY = "temporary", "Temporary"
    VOLUNTEER = "volunteer", "Volunteer"
    NOT_SPECIFIED = "not_specified", "Not Specified"
    OTHER = "other", "Other"


class WorkLocationType(models.TextChoices):
    """Work location setup"""
    REMOTE = "remote", "Remote"
    HYBRID = "hybrid", "Hybrid"
    ONSITE = "onsite", "Onsite"
    NOT_SPECIFIED = "not_specified", "Not Specified"
    OTHER = "other", "Other"


class SeniorityLevel(models.TextChoices):
    """Career seniority levels"""
    INTERN = "intern", "Intern"
    ENTRY = "entry", "Entry"
    JUNIOR = "junior", "Junior"
    MID = "mid", "Mid"
    SENIOR = "senior", "Senior"
    LEAD = "lead", "Lead"
    MANAGER = "manager", "Manager"
    DIRECTOR = "director", "Director"
    VP = "vp", "VP"
    EXECUTIVE = "executive", "Executive"
    OTHER = "other", "Other"
    NOT_SPECIFIED = "not_specified", "Not Specified"


class Currency(models.TextChoices):
    """Currency codes for pay"""
    USD = "USD", "US Dollar"
    EUR = "EUR", "Euro"
    GBP = "GBP", "British Pound"
    AED = "AED", "UAE Dirham"
    SAR = "SAR", "Saudi Riyal"
    PKR = "PKR", "Pakistani Rupee"
    OTHER = "other", "Other"


class PayPeriod(models.TextChoices):
    """Compensation frequency"""
    HOURLY = "hourly", "Hourly"
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"
    OTHER = "other", "Other"
    ONE_TIME = "one_time", "One Time"
