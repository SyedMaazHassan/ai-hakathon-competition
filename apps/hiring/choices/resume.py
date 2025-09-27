"""
Resume-specific enums for resume parsing.
This module imports all general enums and adds resume-specific ones.
When you import from this module, you get both general and resume-specific enums.
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




# Export all enums (general + resume-specific)
__all__ = [
    # General enums
    'SkillLevel',
    'EducationLevel',
    'EmploymentType',
    'WorkLocationType',
    'SeniorityLevel',
    'Currency',
    'PayPeriod',
    # Resume-specific enums
    'VisaSupport',
    'ClearanceLevel'
]
