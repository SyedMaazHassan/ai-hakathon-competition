import zipfile
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth import get_user_model
from apps.hiring.utils.choices import PLATFORM_CHOICES, JOB_TYPE_CHOICES, JOB_MODE_CHOICES, APPLICATION_STATUS_CHOICES
from apps.jobs.models import Job

User = get_user_model()


class BulkResumeUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bulk_uploads")
    files = models.FileField(upload_to="bulk_resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.files.name.endswith(".zip"):
            zip_file = zipfile.ZipFile(self.files)
            for filename in zip_file.namelist():
                if filename.endswith((".pdf", ".doc", ".docx")):
                    file_data = zip_file.read(filename)
                    file_obj = ContentFile(file_data, name=filename)

                    Resume.objects.create(
                        user=self.user,
                        file=file_obj
                    )
        else:
            # Single file upload
            Resume.objects.create(
                user=self.user,
                file=self.files
            )

class Skill(models.Model):
    """
    Model to store individual skills
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Skill Name")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ["name"]

    def __str__(self):
        return self.name



class JobSkill(models.Model):
    """
    Through model for Job ↔ Skill many-to-many relationship
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="job_skills")
    weight = models.PositiveIntegerField(default=1, verbose_name="Importance Weight")

    class Meta:
        verbose_name = "Job Skill"
        verbose_name_plural = "Job Skills"
        unique_together = ("job", "skill")

    def __str__(self):
        return f"{self.skill.name}"

class Resume(models.Model):
    """
    Model for saving resumes and extracted data
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="resumes",
    )
    file = models.FileField(upload_to="resumes/", verbose_name="Resume File")
    parsed_text = models.TextField(blank=True, null=True, verbose_name="Parsed Text")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadata")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded At")

    class Meta:
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Resume for {self.user} file name {self.file.name}"


class JobApplication(models.Model):
    """
    Model to represent an application of a Resume to a Job
    """
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Job"
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Resume"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_applications",
        verbose_name="Applicant"
    )
    cover_letter = models.TextField(
        blank=True,
        null=True,
        verbose_name="Cover Letter"
    )
    status = models.CharField(
        max_length=50,
        choices= APPLICATION_STATUS_CHOICES,
        default="submitted",
        verbose_name="Application Status"
    )
    applied_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Applied At"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    job_fit_report = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Job Fit Report"
    )

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        unique_together = ("job", "resume")
        ordering = ["-applied_at"]

    def __str__(self):
        return f"Application of {self.user}"



