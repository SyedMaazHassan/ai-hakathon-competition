from django.urls import path

from .views import JobCreateView, JobsListView, JobDetailView

app_name = "jobs"

urlpatterns = [
    # for jobs
    path("jobs/", JobsListView.as_view(), name="jobs_list"),
    path("jobs/new/", JobCreateView.as_view(), name="job_create"),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job_detail"),
]


