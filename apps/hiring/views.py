from urllib import request

from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse

from .models import Job, Resume, JobApplication
from .forms import JobForm, BulkResumeUploadForm
from .tasks import process_job_fit_scoring

class BulkResumeUploadView(LoginRequiredMixin, FormView):
    template_name = "hiring/resumes/bulk_upload.html"
    form_class = BulkResumeUploadForm
    success_url = reverse_lazy("hiring:analysis")

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        print("DEBUG FILES:", files)  # <- should now show files

        if not files:
            form = self.get_form()
            form.add_error(None, "Please upload at least one file.")
            return self.form_invalid(form)

        if len(files) > 10:
            form = self.get_form()
            form.add_error(None, "Please upload no more than 10 files.")
            return self.form_invalid(form)

        allowed_ext = {"pdf", "doc", "docx"}
        invalid = [f.name for f in files if f.name.rsplit(".", 1)[-1].lower() not in allowed_ext]
        if invalid:
            form = self.get_form()
            form.add_error(None, "Only PDF, DOC, and DOCX files are allowed.")
            return self.form_invalid(form)

        for f in files:
            Resume.objects.create(user=request.user, file=f)

        return super().form_valid(self.get_form())


class JobFitAnalysisView(LoginRequiredMixin, View):
    """
    Views for job fit analysis
    """
    template_name = "hiring/job_fit_report/wizard_analyze.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        jobs = Job.objects.filter(user=request.user).order_by("-created_at")
        resumes = Resume.objects.filter(user=request.user).order_by("-created_at")
        return render(request, self.template_name, {"jobs": jobs, "resumes": resumes})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        job_id = request.POST.get("job_id")
        resume_ids = request.POST.getlist("resume_ids")

        if not job_id:
            jobs = Job.objects.filter(user=request.user).order_by("-created_at")
            resumes = Resume.objects.filter(user=request.user).order_by("-created_at")
            return render(request, self.template_name, {"jobs": jobs, "resumes": resumes, "error": "Please select a job."})

        if not resume_ids:
            jobs = Job.objects.filter(user=request.user).order_by("-created_at")
            resumes = Resume.objects.filter(user=request.user).order_by("-created_at")
            return render(request, self.template_name, {"jobs": jobs, "resumes": resumes, "error": "Please select at least one resume."})

        job = Job.objects.filter(id=job_id, user=request.user).first()
        if not job:
            return redirect("hiring:analysis")

        for rid in resume_ids:
            resume = Resume.objects.filter(id=rid, user=request.user).first()
            if not resume:
                continue
            application, created = JobApplication.objects.get_or_create(
                job=job,
                resume=resume,
                user=request.user,
            )
            # Queue scoring
            try:
                process_job_fit_scoring.delay(application.id)
            except Exception:
                pass

        return redirect("hiring:job_fit_reports")


class ApplicationsListView(LoginRequiredMixin, ListView):
    """
    views for applications
    """
    model = JobApplication
    template_name = "hiring/resumes/applications_list.html"
    context_object_name = "applications"

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).select_related("job", "resume").order_by("-applied_at")


class ResumesListView(LoginRequiredMixin, ListView):
    """
    Views for candidate list view (formerly resume list)
    """
    model = Resume
    template_name = "hiring/candidates/candidates_list.html"
    context_object_name = "resumes"

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user).order_by("-created_at")



class ResumeDetailView(LoginRequiredMixin, DetailView):
    """
    Views for candidate detail page (formerly resume detail)
    """
    model = Resume
    template_name = "hiring/candidates/candidate_detail.html"
    context_object_name = "resume"

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


class JobFitReportsListView(LoginRequiredMixin, ListView):
    """
    Views for Job Fit Reports
    Filters:
    - title
    - status
    - resume name
    - job title
    """
    model = JobApplication
    template_name = "hiring/job_fit_report/job_fit_reports_list.html"
    context_object_name = "applications"

    def get_queryset(self):
        queryset = (
            JobApplication.objects
            .filter(user=self.request.user)
            .select_related("job", "resume")
            .order_by("-applied_at")
        )

        # Handle search query
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(job__parsed_detailed__title__icontains=search_query) |
                Q(resume__metadata__personal_info__full_name__icontains=search_query) |
                Q(job_fit_report__experience_alignment__highlights__icontains=search_query) |
                Q(job_fit_report__experience_alignment__gaps__icontains=search_query)
            )

        # Handle status filter
        status_filter = self.request.GET.get('status')
        if status_filter == 'completed':
            queryset = queryset.filter(job_fit_report__isnull=False)
        elif status_filter == 'processing':
            queryset = queryset.filter(job_fit_report__isnull=True).exclude(status__iexact='failed')
        elif status_filter == 'failed':
            queryset = queryset.filter(status__iexact='failed')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apps = context["applications"]

        total = JobApplication.objects.filter(user=self.request.user).count()
        completed = JobApplication.objects.filter(user=self.request.user, job_fit_report__isnull=False).count()
        failed = JobApplication.objects.filter(user=self.request.user, status__iexact='failed').count()
        processing = max(total - completed - failed, 0)

        context.update({
            "total_reports": total,
            "completed_reports": completed,
            "processing_reports": processing,
            "failed_reports": failed,
        })
        return context


class JobFitReportDetailView(LoginRequiredMixin, DetailView):
    """
    View for Job Fit Report Detail
    """
    model = JobApplication
    template_name = "hiring/job_fit_report/job_fit_report_detail.html"
    context_object_name = "application"

    def get_queryset(self):
        return (
            JobApplication.objects
            .filter(user=self.request.user)
            .select_related("job", "resume")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = context['application']

        # Process job_fit_report data to multiply decimal values by 10 for display
        if application.job_fit_report:
            report_data = application.job_fit_report.copy()

            # Multiply data quality assessment values by 10
            if 'data_quality_assessment' in report_data:
                for key, value in report_data['data_quality_assessment'].items():
                    if isinstance(value, (int, float)) and value <= 1.0:
                        report_data['data_quality_assessment'][key] = value * 10

            # Multiply section scores and details by 10
            if 'section_scores' in report_data:
                for section in report_data['section_scores']:
                    if 'raw_score' in section and isinstance(section['raw_score'], (int, float)) and section[
                        'raw_score'] <= 1.0:
                        section['raw_score'] = section['raw_score'] * 10
                    if 'weighted_score' in section and isinstance(section['weighted_score'], (int, float)) and section[
                        'weighted_score'] <= 1.0:
                        section['weighted_score'] = section['weighted_score'] * 10

                    # Process details within each section
                    if 'details' in section:
                        for detail_key, detail_value in section['details'].items():
                            if isinstance(detail_value, (int, float)) and detail_value <= 1.0:
                                section['details'][detail_key] = detail_value * 10

            # Multiply skills_score values by 10
            if 'skills_score' in report_data:
                skills_score = report_data['skills_score']
                if 'raw_score' in skills_score and isinstance(skills_score['raw_score'], (int, float)) and skills_score[
                    'raw_score'] <= 1.0:
                    skills_score['raw_score'] = skills_score['raw_score'] * 10
                if 'weighted_score' in skills_score and isinstance(skills_score['weighted_score'], (int, float)) and \
                        skills_score['weighted_score'] <= 1.0:
                    skills_score['weighted_score'] = skills_score['weighted_score'] * 10

                # Process skills_score details
                if 'details' in skills_score:
                    for detail_key, detail_value in skills_score['details'].items():
                        if isinstance(detail_value, dict):
                            for sub_key, sub_value in detail_value.items():
                                if isinstance(sub_value, (int, float)) and sub_value <= 1.0:
                                    skills_score['details'][detail_key][sub_key] = sub_value * 10
                        elif isinstance(detail_value, (int, float)) and detail_value <= 1.0:
                            skills_score['details'][detail_key] = detail_value * 10

            # Multiply skill_matches final_score by 10
            if 'skill_matches' in report_data:
                for skill_match in report_data['skill_matches']:
                    if 'final_score' in skill_match and isinstance(skill_match['final_score'], (int, float)) and \
                            skill_match['final_score'] <= 1.0:
                        skill_match['final_score'] = skill_match['final_score'] * 10

            context['processed_report'] = report_data

        return context