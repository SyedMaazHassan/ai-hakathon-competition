from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
User = get_user_model()
from apps.hiring.choices.job import *  # all enums
from apps.hiring.pydantic_models.general import DateModel

class Job(models.Model):
    """
    Model to store data for job postings
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posted_jobs",
        verbose_name="Job Owner"
    )
    description = models.TextField(verbose_name="Job Description", default="")
    parsed_detailed = models.JSONField(default=dict, blank=True, verbose_name="Parsed Detailed")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Job"
        verbose_name_plural = "Jobs"
        ordering = ["-created_at"]



class CompanyInfo(models.Model):
    """Basic company profile details"""
    name = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    locations = models.JSONField(default=list, blank=True)  # list of strings


class PostingMetadata(models.Model):
    """Job posting source and metadata"""

    source = models.CharField(max_length=100, null=True, blank=True)
    source_url = models.URLField(null=True, blank=True)

    # 👇 Dual system: structured DateField + flexible JSONField
    posted_at = models.DateField(null=True, blank=True)              # full date (if available)
    posted_at_meta = models.JSONField(null=True, blank=True)         # AI partial date (via DateModel)

    application_deadline = models.DateField(null=True, blank=True)
    application_deadline_meta = models.JSONField(null=True, blank=True)

    requisition_id = models.CharField(max_length=100, null=True, blank=True)
    ats_board = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)

    def get_posted_at(self):
        return DateModel(**self.posted_at_meta) if self.posted_at_meta else None

    def set_posted_at(self, date_model):
        """Save both real date (if complete) and JSON fallback"""
        if date_model:
            self.posted_at_meta = date_model.dict()
            self.posted_at = date_model.as_date()
        else:
            self.posted_at_meta = None
            self.posted_at = None


class ApplicationProcess(models.Model):
    """How to apply and process steps"""
    apply_url = models.URLField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    screening_questions = models.JSONField(default=list, blank=True)  # list of strings
    interview_stages = models.JSONField(default=list, blank=True)    # list of strings


class Compensation(models.Model):
    """Salary, pay frequency, and benefits"""
    currency = models.CharField(max_length=10, choices=Currency.choices, null=True, blank=True)
    min_amount = models.FloatField(null=True, blank=True)
    max_amount = models.FloatField(null=True, blank=True)
    period = models.CharField(max_length=50, choices=PayPeriod.choices, null=True, blank=True)
    equity = models.TextField(null=True, blank=True)
    bonus = models.TextField(null=True, blank=True)
    benefits = models.JSONField(default=list, blank=True)


class ParsedJob(BaseModel):
    """Normalized job record with structured fields"""
    # Core
    title = models.CharField(max_length=255)
    alternative_titles = models.JSONField(default=list, blank=True)
    seniority = models.CharField(max_length=50, choices=SeniorityLevel.choices, null=True, blank=True)
    employment_type = models.CharField(max_length=50, choices=EmploymentType.choices, null=True, blank=True)
    work_location_type = models.CharField(max_length=50, choices=WorkLocationType.choices, null=True, blank=True)

    # Relations
    company = models.OneToOneField(CompanyInfo, on_delete=models.SET_NULL, null=True, blank=True)
    posting = models.OneToOneField(PostingMetadata, on_delete=models.SET_NULL, null=True, blank=True)
    application = models.OneToOneField(ApplicationProcess, on_delete=models.SET_NULL, null=True, blank=True)
    compensation = models.OneToOneField(Compensation, on_delete=models.SET_NULL, null=True, blank=True)

    # Description blocks
    summary = models.TextField(null=True, blank=True)
    responsibilities = models.JSONField(default=list, blank=True)
    day_to_day = models.JSONField(default=list, blank=True)
    outcomes = models.JSONField(default=list, blank=True)

    # Requirements
    experience = models.JSONField(null=True, blank=True)
    education = models.JSONField(null=True, blank=True)
    authorizations = models.JSONField(null=True, blank=True)
    location_requirements = models.JSONField(null=True, blank=True)

    required_skills = models.JSONField(default=list, blank=True)
    preferred_skills = models.JSONField(default=list, blank=True)
    required_tools = models.JSONField(default=list, blank=True)
    preferred_tools = models.JSONField(default=list, blank=True)
    requirement_groups = models.JSONField(default=list, blank=True)

    normalized_skills = models.JSONField(default=list, blank=True)  # list of str
    normalized_tools = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)          # list of dicts
    certifications = models.JSONField(default=list, blank=True)     # list of dicts

    # Perks
    perks = models.JSONField(default=list, blank=True)

    # Keywords & taxonomy
    keywords = models.JSONField(default=list, blank=True)
    role_taxonomy = models.JSONField(default=dict, blank=True)

    # Policy notes
    diversity_statement = models.TextField(null=True, blank=True)
    equal_opportunity_statement = models.TextField(null=True, blank=True)

    # Provenance & confidence
    parsing_confidence = models.FloatField(null=True, blank=True)
    job=models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
