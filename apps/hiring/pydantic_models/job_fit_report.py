from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from apps.hiring.pydantic_models.job_description import SkillRequirement
from apps.hiring.pydantic_models.pdf_parser_pydantic import Skill

# ============================================================================
# ENUMS FOR JOB FIT REPORTING
# ============================================================================

class FitCategory(str, Enum):
    """Overall fit assessment categories"""
    EXCEPTIONAL_FIT = "exceptional_fit"    # 90-100: Perfect match
    STRONG_FIT = "strong_fit"             # 80-89: Very good match
    GOOD_FIT = "good_fit"                 # 70-79: Solid match
    MODERATE_FIT = "moderate_fit"         # 60-69: Acceptable match
    WEAK_FIT = "weak_fit"                 # 50-59: Poor match
    NO_FIT = "no_fit"                     # 0-49: Not suitable

class RecommendationType(str, Enum):
    """Hiring recommendation types"""
    HIGHLY_RECOMMEND = "highly_recommend"
    RECOMMEND = "recommend"
    CONSIDER = "consider"
    PROCEED_WITH_CAUTION = "proceed_with_caution"
    DO_NOT_RECOMMEND = "do_not_recommend"

class ConfidenceLevel(str, Enum):
    """Confidence in assessment accuracy"""
    HIGH = "high"           # 90-100% confident
    MEDIUM = "medium"       # 70-89% confident
    LOW = "low"             # 50-69% confident
    VERY_LOW = "very_low"   # <50% confident

class GateStatus(str, Enum):
    """Eligibility gate status"""
    PASSED = "passed"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"
    INSUFFICIENT_DATA = "insufficient_data"

# ============================================================================
# SCORING CONFIGURATION
# ============================================================================

class ScoringConfig(BaseModel):
    """Configuration for job fit scoring with user-defined priorities"""

    # Section Weights (must sum to 1.0)
    section_weights: Dict[str, float] = Field(
        default={
            "skills": 0.35,
            "tools": 0.15,
            "experience": 0.20,
            "projects": 0.15,
            "education": 0.10,
            "impact": 0.05
        },
        description="Priority weights for each scoring section"
    )

    # Eligibility Gates Configuration
    gates_config: Dict[str, bool] = Field(
        default={
            "work_authorization": True,
            "location": True,
            "min_experience": True,
            "education": False,
            "security_clearance": False,
            "industry_role_relevance": True
        },
        description="Which eligibility gates to enforce"
    )

    # Scoring Parameters
    recency_decay_factor: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Annual decay factor for skill recency (0.95 = 5% decay per year)"
    )

    # Priority weights within skills section
    skill_priority_weights: Dict[str, float] = Field(
        default={
            "must_have": 1.0,
            "strong_preference": 0.7,
            "nice_to_have": 0.3
        },
        description="Weights for different skill priority levels"
    )

    # Role and industry context
    role_family: Optional[str] = Field(
        default=None,
        description="Role family for contextualized scoring (e.g., 'engineering', 'sales')"
    )

    industry: Optional[str] = Field(
        default=None,
        description="Industry for contextualized scoring (e.g., 'automotive', 'tech')"
    )

    # Configuration metadata
    config_version: str = Field(default="1.0", description="Configuration version for reproducibility")
    created_by: Optional[str] = Field(default=None, description="User who created this configuration")
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('section_weights')
    def weights_must_sum_to_one(cls, v):
        total = sum(v.values())
        if abs(total - 1.0) > 0.001:  # Allow small floating point errors
            raise ValueError(f"Section weights must sum to 1.0, got {total}")
        return v

# ============================================================================
# DETAILED MATCHING RESULTS
# ============================================================================

class SkillMatchDetail(BaseModel):
    """Detailed information about a single skill match"""

    skill_name: str = Field(description="Name of the skill being evaluated")
    job_requirement: SkillRequirement = Field(description="Job's skill requirement")
    resume_skill: Optional[Skill] = Field(default=None, description="Best matching skill from resume")

    # Scoring details
    match_score: float = Field(ge=0.0, le=1.0, description="Base match score (0.0-1.0)")
    proficiency_score: float = Field(ge=0.0, le=1.0, description="Proficiency level match score")
    years_score: float = Field(ge=0.0, le=1.2, description="Years experience score (can exceed 1.0)")
    recency_score: float = Field(ge=0.0, le=1.0, description="Recency factor score")
    final_score: float = Field(ge=0.0, le=1.0, description="Final weighted skill score")

    # Evidence and explanation
    match_confidence: ConfidenceLevel = Field(description="Confidence in this match")
    evidence_sources: List[str] = Field(default_factory=list, description="Where skill was found in resume")
    gap_reason: Optional[str] = Field(default=None, description="Why this skill didn't match well")

    # Context
    is_required: bool = Field(description="Whether this skill is required vs preferred")
    priority_weight: float = Field(description="Priority weight applied to this skill")

class SectionScore(BaseModel):
    """Score and analysis for a major scoring section"""

    section_name: str = Field(description="Name of the scoring section")
    raw_score: float = Field(ge=0.0, le=100.0, description="Raw section score (0-100)")
    weight: float = Field(ge=0.0, le=1.0, description="Weight assigned to this section")
    weighted_score: float = Field(ge=0.0, le=100.0, description="Score * weight")

    # Detailed breakdown
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed scoring breakdown")
    strengths: List[str] = Field(default_factory=list, description="Top strengths in this section")
    gaps: List[str] = Field(default_factory=list, description="Key gaps identified")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")

    # Quality indicators
    confidence: ConfidenceLevel = Field(description="Confidence in this section's assessment")
    data_completeness: float = Field(ge=0.0, le=1.0, description="How complete was the data for scoring")

# ============================================================================
# ELIGIBILITY ASSESSMENT
# ============================================================================

class GateResult(BaseModel):
    """Result of a single eligibility gate"""

    gate_name: str = Field(description="Name of the eligibility gate")
    status: GateStatus = Field(description="Pass/fail status")
    required: bool = Field(description="Whether this gate is required vs optional")

    # Details
    job_requirement: Optional[str] = Field(default=None, description="What the job requires")
    candidate_status: Optional[str] = Field(default=None, description="Candidate's status")
    evaluation_notes: Optional[str] = Field(default=None, description="Additional evaluation notes")

    # Evidence
    evidence_sources: List[str] = Field(default_factory=list, description="Supporting evidence")
    confidence: ConfidenceLevel = Field(description="Confidence in this gate assessment")

class EligibilityResult(BaseModel):
    """Overall eligibility assessment results"""

    overall_eligible: bool = Field(description="Whether candidate passes all required gates")
    gates_evaluated: int = Field(description="Total number of gates evaluated")
    gates_passed: int = Field(description="Number of gates passed")
    gates_failed: int = Field(description="Number of gates failed")

    # Detailed results
    gate_results: Dict[str, GateResult] = Field(description="Results for each gate")
    critical_failures: List[str] = Field(default_factory=list, description="Failed gates that are deal-breakers")
    minor_concerns: List[str] = Field(default_factory=list, description="Failed optional gates")

    # Summary
    eligibility_summary: str = Field(description="Human-readable eligibility summary")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on gate results")

# ============================================================================
# COMPREHENSIVE JOB FIT REPORT
# ============================================================================

class JobFitReport(BaseModel):
    """Comprehensive job fit analysis report"""

    # ============ META INFORMATION ============
    report_id: str = Field(description="Unique identifier for this report")
    job_id: str = Field(description="Job posting identifier")
    candidate_id: str = Field(description="Candidate/resume identifier")
    candidate_name: str = Field(description="Candidate's full name")

    # Generation metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    config_version: str = Field(description="Scoring configuration version used")
    engine_version: str = Field(default="1.0", description="Job fit engine version")

    # ============ EXECUTIVE SUMMARY ============
    overall_fit_score: float = Field(ge=0.0, le=100.0, description="Overall fit score (0-100)")
    fit_category: FitCategory = Field(description="Categorical fit assessment")
    hiring_recommendation: RecommendationType = Field(description="Hiring recommendation")
    confidence_level: ConfidenceLevel = Field(description="Overall confidence in assessment")

    # ============ ELIGIBILITY GATES ============
    eligibility_assessment: EligibilityResult = Field(description="Eligibility gate results")

    # ============ SECTION SCORES ============
    section_scores: List[SectionScore] = Field(description="Detailed section-by-section scoring")

    # Quick access to major sections
    skills_score: Optional[SectionScore] = Field(default=None, description="Skills section score")
    experience_score: Optional[SectionScore] = Field(default=None, description="Experience section score")
    projects_score: Optional[SectionScore] = Field(default=None, description="Projects section score")
    education_score: Optional[SectionScore] = Field(default=None, description="Education section score")

    # ============ KEY INSIGHTS ============
    top_strengths: List[str] = Field(default_factory=list, description="Top 3-5 candidate strengths")
    critical_gaps: List[str] = Field(default_factory=list, description="Most important gaps or concerns")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    risk_factors: List[str] = Field(default_factory=list, description="Potential hiring risks")

    # ============ DETAILED EVIDENCE ============
    skill_matches: List[SkillMatchDetail] = Field(default_factory=list, description="Detailed skill matching analysis")

    # ============ COMPARATIVE CONTEXT ============
    percentile_ranking: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Percentile ranking among all candidates (when available)"
    )

    similar_candidates_count: Optional[int] = Field(
        default=None,
        description="Number of candidates with similar profiles in comparison pool"
    )

    # ============ AUDIT TRAIL ============
    evidence_trail: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Complete evidence trail for all conclusions"
    )

    data_quality_assessment: Dict[str, float] = Field(
        default_factory=dict,
        description="Assessment of data quality for each section (0-1)"
    )

    processing_notes: List[str] = Field(
        default_factory=list,
        description="Notes about processing issues or limitations"
    )

    # ============ CONFIGURATION USED ============
    scoring_config: ScoringConfig = Field(description="Configuration used for this assessment")

    def get_section_score(self, section_name: str) -> Optional[SectionScore]:
        """Helper method to get a specific section score"""
        for section in self.section_scores:
            if section.section_name == section_name:
                return section
        return None

    def get_weighted_total(self) -> float:
        """Calculate total weighted score from all sections"""
        return sum(section.weighted_score for section in self.section_scores)

    def is_hire_recommended(self) -> bool:
        """Helper to check if hiring is recommended"""
        return self.hiring_recommendation in [
            RecommendationType.HIGHLY_RECOMMEND,
            RecommendationType.RECOMMEND
        ]

# ============================================================================
# BATCH REPORTING (for multiple candidates)
# ============================================================================

class BatchJobFitReport(BaseModel):
    """Report comparing multiple candidates for a single job"""

    job_id: str = Field(description="Job posting identifier")
    job_title: str = Field(description="Job title for reference")
    generated_at: datetime = Field(default_factory=datetime.now)

    # Individual reports
    candidate_reports: List[JobFitReport] = Field(description="Individual candidate reports")

    # Aggregate insights
    total_candidates: int = Field(description="Total candidates evaluated")
    recommended_candidates: int = Field(description="Number of candidates recommended for hire")
    avg_fit_score: float = Field(description="Average fit score across all candidates")

    # Rankings
    top_candidates: List[str] = Field(description="Top candidate IDs in rank order")
    score_distribution: Dict[str, int] = Field(
        description="Distribution of candidates across fit categories"
    )

    # Gap analysis
    common_strengths: List[str] = Field(description="Skills/areas where most candidates excel")
    common_gaps: List[str] = Field(description="Skills/areas where most candidates are weak")

    # Recommendations
    hiring_pool_quality: str = Field(description="Overall assessment of candidate pool quality")
    sourcing_recommendations: List[str] = Field(description="Suggestions for improving candidate pipeline")