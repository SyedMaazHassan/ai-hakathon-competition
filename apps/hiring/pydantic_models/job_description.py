from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Annotated
from enum import Enum
from .general import DateModel

# Import all job-related enums (includes general + job-specific)
from apps.hiring.choices.job import *


# All enums are now imported from choices.job

# ---------- Requirement atoms ----------

class SkillRequirement(BaseModel):
    name: str = Field(description="Verbatim skill/tool keyword")
    normalized: str | None = Field(default=None, description="Canonicalized value (e.g., 'postgres' => 'PostgreSQL')")
    level: SkillLevel | None = Field(default=None, description="Desired proficiency level")
    min_years: Annotated[float, Field(ge=0, le=60)] | None = Field(default=None, description="Minimum years of experience required")
    preferred_years: Annotated[float, Field(ge=0, le=60)] | None = Field(default=None, description="Preferred years of experience")
    priority: RequirementPriority | None = Field(default=None, description="Priority level for this requirement")
    notes: str | None = Field(default=None, description="Additional notes or context about this skill requirement")

class ExperienceRequirement(BaseModel):
    role_keywords: List[str] = Field(default_factory=list, description="Job titles/aliases to match. Pick from job title and description")
    min_years_total: Annotated[float, Field(ge=0, le=60)] | None = Field(default=None, description="Minimum total years of professional experience")
    preferred_years_total: Annotated[float, Field(ge=0, le=60)] | None = Field(default=None, description="Preferred total years of professional experience")
    min_years_in_role: Annotated[float, Field(ge=0, le=60)] | None = Field(default=None, description="Minimum years in similar role")
    equivalency_allowed: bool = Field(True, description="Allow strong skills/projects to offset years")
    industries: List[str] = Field(default_factory=list, description="Preferred industry experience")
    priority: RequirementPriority | None = Field(default=None, description="Priority level for this requirement")
    notes: str | None = Field(default=None, description="Additional notes about experience requirements")

class EducationRequirement(BaseModel):
    levels: List[EducationLevel] = Field(default_factory=list, description="Accepted degree levels")
    fields_of_study: List[str] = Field(default_factory=list, description="Preferred fields of study or majors")
    alternatives_allowed: bool = Field(True, description="Whether equivalent experience is acceptable")
    certifications_as_alternative: List[str] = Field(default_factory=list, description="Certifications that can substitute for degree")
    priority: RequirementPriority | None = Field(default=None, description="Priority level for this requirement")
    notes: str | None = Field(default=None, description="Additional notes about education requirements")

class CertificationRequirement(BaseModel):
    name: str = Field(description="Certification name")
    issuing_organizations: List[str] = Field(default_factory=list, description="Accepted certifying organizations")
    acceptable_equivalents: List[str] = Field(default_factory=list, description="Alternative certifications that are equivalent")
    priority: RequirementPriority | None = Field(default=None, description="Priority level for this requirement")
    notes: str | None = Field(default=None, description="Additional notes about certification requirements")

class LanguageRequirement(BaseModel):
    language: str = Field(description="Language name (e.g., English, Spanish)")
    proficiency: SkillLevel | None = Field(default=None, description="Required proficiency level")
    priority: RequirementPriority | None = Field(default=None, description="Priority level for this requirement")

class LocationRequirement(BaseModel):
    work_location_type: WorkLocationType | None = Field(default=None, description="Type of work location (remote, hybrid, onsite)")
    city: str | None = Field(default=None, description="Required city location")
    state: str | None = Field(default=None, description="Required state/province location")
    country: str | None = Field(default=None, description="Required country location")
    onsite_radius_km: Annotated[float, Field(ge=0, le=10000)] | None = Field(default=None, description="Maximum distance from office in kilometers")
    relocation: bool | None = Field(default=None, description="Whether relocation is required or supported")
    travel_percentage: Annotated[float, Field(ge=0, le=100)] | None = Field(default=None, description="Required travel percentage (0-100)")

class AuthorizationRequirement(BaseModel):
    work_authorization: str | None = Field(default=None, description="Required work authorization status (e.g., 'EU work permit', 'US Citizen')")
    visa_support: VisaSupport | None = Field(default=None, description="Visa sponsorship availability")
    security_clearance: ClearanceLevel | None = Field(default=None, description="Required security clearance level")

# ---------- Logical grouping for complex "AND/OR/min" conditions ----------

class RequirementGroup(BaseModel):
    logic: GroupLogic | None = Field(default=None, description="Logic type for this group")
    min_count: int | None = Field(default=None, description="Minimum count required when logic=MIN_COUNT")
    skills: List[SkillRequirement] = Field(default_factory=list, description="Skills in this requirement group")
    tools: List[SkillRequirement] = Field(default_factory=list, description="Tools in this requirement group")
    notes: str | None = Field(default=None, description="Additional notes about this requirement group")
    priority: RequirementPriority | None = Field(default=None, description="Priority level for this requirement group")

# ---------- Role definition & outcomes ----------

class RoleOutcome(BaseModel):
    description: str = Field(description="Outcome/KPI the role owns (e.g., 'Reduce infra cost by 20% in 6 months')")
    metric_key: str | None = Field(default=None, description="Canonical metric name")
    target_value: str | None = Field(default=None, description="Target value or range as string")
    timeframe: str | None = Field(default=None, description="Expected timeframe (e.g., '6 months')")
    priority: RequirementPriority | None = Field(default=None, description="Priority level for this outcome")

# ---------- Compensation & benefits ----------

class Compensation(BaseModel):
    currency: Currency | None = Field(default=None, description="Currency for compensation amounts")
    min_amount: Annotated[float, Field(ge=0)] | None = Field(default=None, description="Minimum compensation amount")
    max_amount: Annotated[float, Field(ge=0)] | None = Field(default=None, description="Maximum compensation amount")
    period: PayPeriod | None = Field(default=None, description="Payment period (hourly, monthly, yearly, etc.)")
    equity: str | None = Field(default=None, description="Equity compensation details")
    bonus: str | None = Field(default=None, description="Bonus compensation details")
    benefits: List[str] = Field(default_factory=list, description="List of benefits offered")

# ---------- Company & posting metadata ----------

class CompanyInfo(BaseModel):
    name: str | None = Field(default=None, description="Company name")
    website: str | None = Field(default=None, description="Company website URL")
    industry: str | None = Field(default=None, description="Industry or sector")
    size: str | None = Field(default=None, description="Company size (e.g., '50-100 employees')")
    about: str | None = Field(default=None, description="Company description or about section")
    locations: List[str] = Field(default_factory=list, description="Company office locations")

class PostingMetadata(BaseModel):
    source: str | None = Field(default=None, description="Job posting source (e.g., LinkedIn, Greenhouse, Lever)")
    source_url: str | None = Field(default=None, description="URL to the original job posting")
    posted_at: DateModel | None = Field(default=None, description="Date when job was posted")
    updated_at: DateModel | None = Field(default=None, description="Date when job was last updated")
    application_deadline: DateModel | None = Field(default=None, description="Application deadline date")
    requisition_id: str | None = Field(default=None, description="Internal requisition ID")
    ats_board: str | None = Field(default=None, description="ATS board identifier (e.g., Greenhouse job board slug)")
    contact_email: EmailStr | None = Field(default=None, description="Contact email for applications")

class ApplicationProcess(BaseModel):
    apply_url: str | None = Field(default=None, description="URL to apply for the job")
    instructions: str | None = Field(default=None, description="Application instructions")
    screening_questions: List[str] = Field(default_factory=list, description="Pre-screening questions")
    interview_stages: List[str] = Field(default_factory=list, description="Interview process stages")

# ---------- Main ParsedJob ----------

class ParsedJob(BaseModel):
    # Core
    title: str = Field(description="Job title from the posting")
    alternative_titles: List[str] = Field(default_factory=list, description="Alternative job titles or role variants")
    seniority: SeniorityLevel | None = Field(default=None, description="Seniority level required for the role")
    employment_type: EmploymentType | None = Field(default=None, description="Type of employment (full-time, part-time, etc.)")
    work_location_type: WorkLocationType | None = Field(default=None, description="Work location type (remote, hybrid, onsite)")

    # Company & posting
    company: CompanyInfo | None = Field(default=None, description="Company information")
    posting: PostingMetadata | None = Field(default=None, description="Job posting metadata")
    application: ApplicationProcess | None = Field(default=None, description="Application process details")

    # Description blocks (verbatim)
    summary: str | None = Field(default=None, description="Job summary or overview")
    responsibilities: List[str] = Field(default_factory=list, description="Key job responsibilities")
    day_to_day: List[str] = Field(default_factory=list, description="Day-to-day activities")
    outcomes: List[RoleOutcome] = Field(default_factory=list, description="Expected role outcomes and KPIs")

    # Requirements (structured)
    experience: ExperienceRequirement | None = Field(default=None, description="Experience requirements")
    education: EducationRequirement | None = Field(default=None, description="Education requirements")
    authorizations: AuthorizationRequirement | None = Field(default=None, description="Authorization and clearance requirements")
    location_requirements: LocationRequirement | None = Field(default=None, description="Location and work arrangement requirements")

    # Atomized skills/tools & grouped logic
    required_skills: List[SkillRequirement] = Field(default_factory=list, description="Required skills for the position")
    preferred_skills: List[SkillRequirement] = Field(default_factory=list, description="Preferred/nice-to-have skills")
    required_tools: List[SkillRequirement] = Field(default_factory=list, description="Required tools and technologies")
    preferred_tools: List[SkillRequirement] = Field(default_factory=list, description="Preferred tools and technologies")
    requirement_groups: List[RequirementGroup] = Field(
        default_factory=list,
        description="Complex AND/OR/MIN skill/tool bundles"
    )

    # Normalized facets (for direct set intersection with resume)
    normalized_skills: List[str] = Field(default_factory=list, description="Deduped, canonical skills")
    normalized_tools: List[str] = Field(default_factory=list, description="Deduped, canonical tools")
    languages: List[LanguageRequirement] = Field(default_factory=list, description="Language requirements")
    certifications: List[CertificationRequirement] = Field(default_factory=list, description="Certification requirements")

    # Compensation & perks
    compensation: Compensation | None = Field(default=None, description="Compensation and salary information")
    perks: List[str] = Field(default_factory=list, description="Additional perks and benefits")

    # Taxonomy/keywords (optional but useful)
    keywords: List[str] = Field(default_factory=list, description="Relevant keywords extracted from job posting")
    role_taxonomy: Dict[str, str] = Field(
        default_factory=dict,
        description="Role taxonomy mappings (e.g., O*NET, ESCO codes)",
    )

    # Free-text policy notes
    diversity_statement: str | None = Field(default=None, description="Company diversity and inclusion statement")
    equal_opportunity_statement: str | None = Field(default=None, description="Equal opportunity employment statement")

    # Provenance & confidence
    # field_sources: Dict[str, str] = Field(default_factory=dict, description="Mapping of field paths to source phrases")
    parsing_confidence: Annotated[float, Field(ge=0.0, le=1.0)] | None = Field(default=None, description="Confidence score of parsing accuracy (0.0-1.0)")
