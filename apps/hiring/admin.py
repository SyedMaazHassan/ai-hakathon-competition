from django.contrib import admin
from .models import Skill, Job, JobSkill, Resume, JobApplication, BulkResumeUpload


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Custom admin for Skill
    """
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 1
    autocomplete_fields = ["skill"]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    Custom admin for Job
    """
    list_display = ("id", "user", "description", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("description",)
    autocomplete_fields = ["user"]
    ordering = ("-created_at",)


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    """
    Custom admin for Resume
    """
    list_display = ("user", "file", "created_at")
    search_fields = ("user__username", "file")
    list_filter = ("created_at",)
    autocomplete_fields = ["user"]
    ordering = ("-created_at",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """
    Custom admin for JobApplication
    """
    list_display = ("job", "user", "status", "applied_at", "updated_at")
    list_filter = ("status", "applied_at", "updated_at")
    search_fields = ("job__title", "user__username", "resume__file")
    autocomplete_fields = ["job", "resume", "user"]
    ordering = ("-applied_at",)
admin.site.register(BulkResumeUpload)