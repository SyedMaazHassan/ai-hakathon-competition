from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Annotated
from .general import DateModel

from apps.hiring.choices.resume import *


# All enums are now imported from choices.resume


class ContactInfo(BaseModel):
    """Contact information with validation"""
    email: EmailStr | None = Field(default=None, description="Primary email address")
    phone: str | None = Field(default=None, description="Phone number in any format")
    linkedin: str | None = Field(default=None, description="LinkedIn profile URL")
    github: str | None = Field(default=None, description="GitHub profile URL")
    portfolio: str | None = Field(default=None, description="Portfolio/personal website URL")
    address: str | None = Field(default=None, description="Full address or city, state")
    city: str | None = Field(default=None, description="City of residence")
    state: str | None = Field(default=None, description="State/province of residence")
    country: str | None = Field(default=None, description="Country of residence")
    zip_code: str | None = Field(default=None, description="ZIP/postal code")


class Skill(BaseModel):
    """Individual skill with proficiency level"""
    name: str = Field(description="Skill name (e.g., Python, Project Management)")
    level: SkillLevel | None = Field(default=None, description="Proficiency level")
    years_experience: Annotated[int, Field(ge=0, le=50)] | None = Field(default=None, description="Years of experience with this skill")
    category: str | None = Field(default=None, description="Skill category (e.g., Programming, Design, Management)")


class Language(BaseModel):
    """Language proficiency"""
    language: str = Field(description="Language name")
    proficiency: SkillLevel | None = Field(default=None, description="Proficiency level")
    certification: str | None = Field(default=None, description="Language certification if any")


class Education(BaseModel):
    """Educational background"""
    institution: str = Field(description="School/university name")
    degree: str | None = Field(default=None, description="Degree title (e.g., Bachelor of Science)")
    field_of_study: str | None = Field(default=None, description="Major/field of study")
    level: EducationLevel | None = Field(default=None, description="Education level")
    start_date: DateModel | None = Field(default=None, description="Start date")
    end_date: DateModel | None = Field(default=None, description="End date or expected graduation")
    gpa: Annotated[float, Field(ge=0.0, le=4.0)] | None = Field(default=None, description="GPA on 4.0 scale")
    honors: List[str] = Field(default_factory=list, description="Academic honors, dean's list, etc.")
    relevant_coursework: List[str] = Field(default_factory=list, description="Relevant courses")
    location: str | None = Field(default=None, description="Institution location")
    is_current: bool = Field(False, description="Currently enrolled")


class WorkExperience(BaseModel):
    """Professional work experience"""
    company: str = Field(description="Company/organization name")
    position: str = Field(description="Job title/position")
    role_category: str | None = Field(default=None, description="One of: 'developer', 'designer', 'manager', 'qa', etc.")
    start_date: DateModel | None = Field(default=None, description="Employment start date")
    end_date: DateModel | None = Field(default=None, description="Employment end date")
    duration_months: int | None = Field(default=None, description="Duration in months, if start and end dates are computable")
    is_current: bool = Field(False, description="Currently employed at this position")
    location: str | None = Field(default=None, description="Work location")
    employment_type: EmploymentType | None = Field(default=None, description="Type of employment")
    industry: str | None = Field(default=None, description="Industry/sector")
    description: str | None = Field(default=None, description="Job description/summary")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    achievements: List[str] = Field(default_factory=list, description="Notable achievements")
    technologies_used: List[str] = Field(default_factory=list, description="Technologies/tools used")


class Project(BaseModel):
    """Personal or professional projects"""
    name: str = Field(description="Project name")
    description: str | None = Field(default=None, description="Project description")
    start_date: DateModel | None = Field(default=None, description="Project start date")
    end_date: DateModel | None = Field(default=None, description="Project completion date")
    is_ongoing: bool = Field(False, description="Project is ongoing")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    url: str | None = Field(default=None, description="Project URL/demo link")
    repository: str | None = Field(default=None, description="Source code repository")
    role: str | None = Field(default=None, description="Your role in the project")
    team_size: Annotated[int, Field(ge=1)] | None = Field(default=None, description="Team size if collaborative")
    achievements: List[str] = Field(default_factory=list, description="Key achievements/outcomes")


class Certification(BaseModel):
    """Professional certifications"""
    name: str = Field(description="Certification name")
    issuing_organization: str | None = Field(default=None, description="Certifying body")
    issue_date: DateModel | None = Field(default=None, description="Date obtained")
    expiry_date: DateModel | None = Field(default=None, description="Expiration date")
    credential_id: str | None = Field(default=None, description="Credential/badge ID")
    credential_url: str | None = Field(default=None, description="Verification URL")
    is_active: bool = Field(True, description="Certification is currently valid")


class Award(BaseModel):
    """Awards and honors"""
    title: str = Field(description="Award title")
    organization: str | None = Field(default=None, description="Awarding organization")
    date_received: DateModel | None = Field(default=None, description="Date received")
    description: str | None = Field(default=None, description="Award description")
    category: str | None = Field(default=None, description="Award category")


class Publication(BaseModel):
    """Academic or professional publications"""
    title: str = Field(description="Publication title")
    authors: List[str] = Field(default_factory=list, description="Authors list")
    publication_venue: str | None = Field(default=None, description="Journal, conference, etc.")
    publication_date: DateModel | None = Field(default=None, description="Publication date")
    url: str | None = Field(default=None, description="Publication URL")
    doi: str | None = Field(default=None, description="DOI identifier")
    citation_count: Annotated[int, Field(ge=0)] | None = Field(default=None, description="Number of citations")


class VolunteerExperience(BaseModel):
    """Volunteer work and community service"""
    organization: str = Field(description="Organization name")
    role: str = Field(description="Volunteer role/position")
    start_date: DateModel | None = Field(default=None, description="Start date")
    end_date: DateModel | None = Field(default=None, description="End date")
    is_current: bool = Field(False, description="Currently volunteering")
    description: str | None = Field(default=None, description="Role description")
    achievements: List[str] = Field(default_factory=list, description="Notable contributions")
    hours_per_week: Annotated[float, Field(ge=0.0, le=168.0)] | None = Field(default=None, description="Average hours per week")


class Reference(BaseModel):
    """Professional references"""
    name: str = Field(description="Reference name")
    title: str | None = Field(default=None, description="Reference job title")
    company: str | None = Field(default=None, description="Reference company")
    relationship: str | None = Field(default=None, description="Professional relationship")
    email: EmailStr | None = Field(default=None, description="Reference email")
    phone: str | None = Field(default=None, description="Reference phone")


# NEW: Work preferences for location/flexibility matching
class WorkPreferences(BaseModel):
    """Work location and flexibility preferences"""
    preferred_work_location_type: WorkLocationType | None = Field(default=None, description="Preferred work arrangement")
    willing_to_relocate: bool | None = Field(default=None, description="Open to relocation")
    max_onsite_radius_km: Annotated[float, Field(ge=0, le=10000)] | None = Field(default=None, description="Maximum commute distance")
    travel_preference_pct: Annotated[float, Field(ge=0, le=100)] | None = Field(default=None, description="Acceptable travel percentage")
    time_zone: str | None = Field(default=None, description="Preferred time zone")
    availability_date: DateModel | None = Field(default=None, description="Available start date")


# NEW: Compensation expectations
class CompensationExpectation(BaseModel):
    """Salary and compensation expectations"""
    currency: Currency | None = Field(default=None, description="Preferred currency")
    desired_min: Annotated[float, Field(ge=0)] | None = Field(default=None, description="Minimum desired compensation")
    desired_max: Annotated[float, Field(ge=0)] | None = Field(default=None, description="Maximum desired compensation")
    period: PayPeriod | None = Field(default=None, description="Pay period preference")
    flexibility_note: str | None = Field(default=None, description="Notes on compensation flexibility")


class PersonalInfo(BaseModel):
    """Personal demographic information (use carefully for compliance)"""
    full_name: str = Field(description="Full name as it appears on resume")
    first_name: str | None = Field(default=None, description="First name")
    last_name: str | None = Field(default=None, description="Last name")
    professional_title: str | None = Field(default=None, description="Professional title/headline")
    summary: str | None = Field(default=None, description="Professional summary/objective")
    date_of_birth: DateModel | None = Field(default=None, description="Date of birth (if provided)")
    nationality: str | None = Field(default=None, description="Nationality (if provided)")
    work_authorization: str | None = Field(default=None, description="Work authorization status")
    # ENHANCED: Aligned authorization fields
    visa_support_needed: VisaSupport | None = Field(default=None, description="Visa sponsorship needs")
    security_clearance: ClearanceLevel | None = Field(default=None, description="Current security clearance")
    preferred_pronouns: str | None = Field(default=None, description="Preferred pronouns")


class SocialMedia(BaseModel):
    """Social media and online presence"""
    platform: str = Field(description="Platform name")
    username: str | None = Field(default=None, description="Username/handle")
    url: str = Field(description="Profile URL")
    follower_count: Annotated[int, Field(ge=0)] | None = Field(default=None, description="Number of followers")


class DerivedSkillStat(BaseModel):
    """Computed skill statistics for fast scoring lookups"""
    years: float | None = Field(default=None, description="Years of experience with this skill")
    level: SkillLevel | None = Field(default=None, description="Assessed proficiency level")
    category: str | None = Field(default=None, description="Skill category (e.g., 'programming', 'management')")


class ParsedResume(BaseModel):
    """Complete parsed resume structure"""

    # Core Information
    personal_info: PersonalInfo = Field()
    contact_info: ContactInfo = Field()

    # NEW: Work preferences
    work_preferences: WorkPreferences | None = Field(default=None, description="Work location and flexibility preferences")
    compensation_expectation: CompensationExpectation | None = Field(default=None, description="Salary expectations")

    # Professional Experience
    work_experience: List[WorkExperience] = Field(default_factory=list)

    # Education
    education: List[Education] = Field(default_factory=list)

    # Skills and Competencies
    technical_skills: List[Skill] = Field(default_factory=list)
    soft_skills: List[Skill] = Field(default_factory=list)
    normalized_skills: List[str] = Field(default_factory=list, description="Normalized skills")
    normalized_tools: List[str] = Field(default_factory=list, description="Normalized tools")
    languages: List[Language] = Field(default_factory=list)

    # NEW: Enhanced for scoring
    derived_skills_matrix: Dict[str, DerivedSkillStat] | None = Field(
        default_factory=dict,
        description="key=normalized_skill; value=DerivedSkillStat"
    )
    normalized_titles: List[str] = Field(default_factory=list, description="Normalized job titles from experience")
    primary_role_family: str | None = Field(default=None, description="Primary role category (e.g., 'software_engineer', 'data_scientist')")

    # Additional Sections
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    awards: List[Award] = Field(default_factory=list)
    publications: List[Publication] = Field(default_factory=list)
    volunteer_experience: List[VolunteerExperience] = Field(default_factory=list)
    professional_references: List[Reference] = Field(default_factory=list, description="Professional references")
    social_media: List[SocialMedia] = Field(default_factory=list)

    # Extra Information
    extra_information: Dict[str, str] | None = Field(default_factory=dict)

    # Metadata
    total_years_experience: Annotated[float, Field(ge=0.0, le=60.0)] | None = Field(default=None, description="Total years of professional experience")
    career_level: str | None = Field(default=None, description="Career level (entry, mid, senior, executive)")
    # NEW: Normalized career level
    career_level_enum: SeniorityLevel | None = Field(default=None, description="Normalized seniority level")
    primary_field: str | None = Field(default=None, description="Primary field/industry")
    parsing_confidence: Annotated[float, Field(ge=0.0, le=1.0)] | None = Field(default=None, description="Confidence score of parsing accuracy")

    # FIXED: Renamed field_sources to avoid collision
    # field_sources: Dict[str, str] = Field(default_factory=dict, description="Mapping of extracted fields to their original location in resume text")