from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Job
from .forms import JobForm
from .tasks import process_job_description_parsing

class JobCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a new job
    """
    model = Job
    form_class = JobForm
    template_name = "jobs/job_create.html"
    success_url = reverse_lazy("hiring:resumes_upload")

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        process_job_description_parsing.delay(self.object.id)
        return response

class JobsListView(LoginRequiredMixin, ListView):
    """
    View to list all jobs
    Filters:
      - title
      - location
      - company
      - employment_type
      - experience_level
      - department
      - location
    """
    model = Job
    template_name = "jobs/jobs_list.html"
    context_object_name = "jobs"

    def get_queryset(self):
        jobs = Job.objects.filter(user=self.request.user).order_by("-created_at")
        search_query = self.request.GET.get('search', '')
        if search_query:
            jobs = jobs.filter(
                Q(parsed_detailed__title__icontains=search_query) |
                Q(parsed_detailed__company__name__icontains=search_query) |
                Q(parsed_detailed__location_requirements__city__icontains=search_query) |
                Q(parsed_detailed__location_requirements__country__icontains=search_query)
            )

        employment_type = self.request.GET.get('employment_type', '')
        if employment_type:
            jobs = jobs.filter(parsed_detailed__employment_type=employment_type)

        experience_level = self.request.GET.get('experience_level', '')
        if experience_level:
            jobs = jobs.filter(parsed_detailed__seniority=experience_level)

        department = self.request.GET.get('department', '')
        if department:
            jobs = jobs.filter(parsed_detailed__department__icontains=department)

        location = self.request.GET.get('location', '')
        if location:
            jobs = jobs.filter(
                Q(parsed_detailed__location_requirements__city__icontains=location) |
                Q(parsed_detailed__location_requirements__country__icontains=location)
            )
        return jobs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



class JobDetailView(LoginRequiredMixin, DetailView):
    """
    Views for job details
    """
    model = Job
    template_name = "jobs/job_detail.html"
    context_object_name = "job"

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)


