from django.contrib import admin
from apps.jobs.models import ParsedJob, Compensation, CompanyInfo, PostingMetadata, ApplicationProcess
# Register your models here.

admin.site.register(ParsedJob)
admin.site.register(CompanyInfo)
admin.site.register(PostingMetadata)
admin.site.register(ApplicationProcess)
admin.site.register(Compensation)
