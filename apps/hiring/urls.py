from django.urls import path

from .views import BulkResumeUploadView, JobFitAnalysisView, ApplicationsListView, ResumesListView, ResumeDetailView, JobFitReportsListView, JobFitReportDetailView

app_name = "hiring"

urlpatterns = [
    # for resumes
    path("resumes/", ResumesListView.as_view(), name="resumes_list"),
    path("resumes/create/", BulkResumeUploadView.as_view(), name="resumes_upload"),
    path("resumes/<int:pk>/", ResumeDetailView.as_view(), name="resume_detail"),

    # for job fit analysis
    path("reports/", JobFitReportsListView.as_view(), name="job_fit_reports"),
    path("analysis/", JobFitAnalysisView.as_view(), name="analysis"),
    path("reports/<int:pk>/", JobFitReportDetailView.as_view(), name="job_fit_report_detail"),
    path('applications/', ApplicationsListView.as_view(), name='applications'),
]


