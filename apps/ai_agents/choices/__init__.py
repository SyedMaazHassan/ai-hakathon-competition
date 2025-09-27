"""
Centralized enum choices for the agentos project.

This package organizes enums into logical modules:
- general.py: Shared enums used across resume and job domains
- resume.py: Resume-specific enums (imports general + adds resume-specific)  
- job.py: Job-specific enums (imports general + adds job-specific)

Usage:
    from choices import resume  # Gets all resume + general enums
    from choices import job     # Gets all job + general enums
    from choices import general # Gets only shared enums
"""

# Re-export modules for convenient access
from . import general
from . import resume
from . import job

__all__ = ['general', 'resume', 'job']
