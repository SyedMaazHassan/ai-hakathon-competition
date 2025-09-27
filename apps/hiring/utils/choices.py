# apps/hiring/utils/choices.py

PLATFORM_CHOICES = [
    ("linkedin", "LinkedIn"),
    ("indeed", "Indeed"),
    ("glassdoor", "Glassdoor"),
    ("other", "Other"),
]

JOB_TYPE_CHOICES = [
    ("full_time", "Full Time"),
    ("part_time", "Part Time"),
    ("contract", "Contract"),
    ("internship", "Internship"),
]

JOB_MODE_CHOICES = [
    ("remote", "Remote"),
    ("hybrid", "Hybrid"),
    ("onsite", "Onsite"),
]

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("completed", "Completed"),
    ("failed", "Failed"),
]


APPLICATION_STATUS_CHOICES = [
    ("submitted", "Submitted"),
    ("under_review", "Under Review"),
    ("interview", "Interview"),
    ("offered", "Offered"),
    ("rejected", "Rejected"),
]
