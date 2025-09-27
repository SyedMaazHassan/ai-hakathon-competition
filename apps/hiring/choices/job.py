"""
Job-specific enums for job posting parsing and requirements.
This module imports all general enums and adds job-specific ones.
When you import from this module, you get both general and job-specific enums.
"""

from enum import Enum

# Import all general/shared enums directly into this namespace
from .general import (
    SkillLevel,
    EducationLevel,
    EmploymentType,
    WorkLocationType,
    SeniorityLevel,
    Currency,
    PayPeriod,
    VisaSupport,
    ClearanceLevel
)

# Job-specific enums
class RequirementPriority(str, Enum):
    """Priority levels for job requirements"""
    MUST_HAVE = "must_have"
    STRONG_PREFERENCE = "strong_preference"
    NICE_TO_HAVE = "nice_to_have"
    OTHER = "other"


class GroupLogic(str, Enum):
    """Logical operations for requirement grouping"""
    ALL_OF = "all_of"
    ANY_OF = "any_of"
    MIN_COUNT = "min_count"
    OTHER = "other"




# Export all enums (general + job-specific)
__all__ = [
    # General enums
    'SkillLevel',
    'EducationLevel',
    'EmploymentType',
    'WorkLocationType',
    'SeniorityLevel',
    'Currency',
    'PayPeriod',
    # Job-specific enums
    'RequirementPriority',
    'GroupLogic',
    'VisaSupport',
    'ClearanceLevel',
]
