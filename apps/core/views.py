from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.hiring.models import Job, Resume, JobApplication
from django.utils import timezone
from datetime import timedelta


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        active_jobs_count = Job.objects.filter(user=user).count()
        total_resumes_count = Resume.objects.filter(user=user).count()
        applications_count = JobApplication.objects.filter(user=user).count()

        previous_jobs_count = Job.objects.filter(
            user=user,
            created_at__lt=thirty_days_ago
        ).count()

        previous_resumes_count = Resume.objects.filter(
            user=user,
            created_at__lt=thirty_days_ago
        ).count()

        previous_applications_count = JobApplication.objects.filter(
            user=user,
            applied_at__lt=thirty_days_ago
        ).count()

        jobs_percentage_change = self.calculate_percentage_change(
            previous_jobs_count, active_jobs_count
        )

        resumes_percentage_change = self.calculate_percentage_change(
            previous_resumes_count, total_resumes_count
        )

        applications_percentage_change = self.calculate_percentage_change(
            previous_applications_count, applications_count
        )

        applications_with_scores = JobApplication.objects.filter(
            user=user,
            job_fit_report__isnull=False
        )

        total_score = 0
        count = 0
        for application in applications_with_scores:
            scoring = application.job_fit_report.get('scoring', {})
            overall_score = scoring.get('overall_fit_score')
            if overall_score is not None:
                total_score += overall_score
                count += 1

        match_rate = round(total_score / count) if count > 0 else 0

        previous_applications_with_scores = JobApplication.objects.filter(
            user=user,
            job_fit_report__isnull=False,
            applied_at__lt=thirty_days_ago
        )

        previous_total_score = 0
        previous_count = 0
        for application in previous_applications_with_scores:
            scoring = application.job_fit_report.get('scoring', {})
            overall_score = scoring.get('overall_fit_score')
            if overall_score is not None:
                previous_total_score += overall_score
                previous_count += 1

        previous_match_rate = round(previous_total_score / previous_count) if previous_count > 0 else 0
        match_rate_percentage_change = self.calculate_percentage_change(
            previous_match_rate, match_rate
        )

        recent_activity = []

        recent_jobs = Job.objects.filter(user=user).order_by('-created_at')[:3]
        for job in recent_jobs:
            job_title = job.parsed_detailed.get("job_title", "Job") if job.parsed_detailed else "Job"
            recent_activity.append({
                'type': 'job_created',
                'title': f'{job_title} position created',
                'time': job.created_at,
                'icon': 'fa-plus'
            })

        recent_resumes = Resume.objects.filter(user=user).order_by('-created_at')[:3]
        if recent_resumes:
            recent_activity.append({
                'type': 'resumes_uploaded',
                'title': f'{len(recent_resumes)} new resumes uploaded',
                'time': recent_resumes[0].created_at,
                'icon': 'fa-users'
            })

        recent_applications = JobApplication.objects.filter(
            user=user
        ).select_related('job').order_by('-applied_at')[:3]

        for application in recent_applications:
            job_title = application.job.parsed_detailed.get('job_title',
                                                            'Job') if application.job.parsed_detailed else 'Job'
            recent_activity.append({
                'type': 'application_processed',
                'title': f'Job fit analysis completed for {job_title}',
                'time': application.applied_at,
                'icon': 'fa-square-check'
            })

        in_progress_count = JobApplication.objects.filter(
            user=user,
            job_fit_report__isnull=True
        ).count()

        if in_progress_count > 0:
            recent_activity.append({
                'type': 'reports_in_progress',
                'title': f'{in_progress_count} job fit reports in progress',
                'time': None,
                'icon': 'fa-clock'
            })

        recent_activity.sort(key=lambda x: x['time'] if x['time'] else timezone.now(), reverse=True)
        recent_activity = recent_activity[:5]

        context.update({
            'active_jobs_count': active_jobs_count,
            'total_resumes_count': total_resumes_count,
            'applications_count': applications_count,
            'match_rate': match_rate,
            'recent_activity': recent_activity,
            'in_progress_count': in_progress_count,
            'jobs_percentage_change': jobs_percentage_change,
            'resumes_percentage_change': resumes_percentage_change,
            'applications_percentage_change': applications_percentage_change,
            'match_rate_percentage_change': match_rate_percentage_change,
        })

        return context

    def calculate_percentage_change(self, old_value, new_value):
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 100 if new_value > 0 else 0
        return round(((new_value - old_value) / old_value) * 100)


def health_check(request):
    """
    Simple health check endpoint to verify the server is running.
    """
    return JsonResponse({'status': 'ok'}, status=200)


def custom_404(request, exception=None):
    """Custom JSON 404 handler for API routes only."""
    if request.path.startswith("/api/"):  # Ensures only API routes return JSON
        # Use JsonResponse instead of DRF Response for 404 handlers
        return JsonResponse({
            "status": "error",
            "data": None,
            "message": "The requested API endpoint was not found."
        }, status=404)

    # For non-API routes, return a standard 404 page
    return render(request, '404.html', status=404)


def test_email_template(request):
    context = {
        'site_name': 'Agentsup',
        'code': '123456',
        'expiry_minutes': 10,
        'user': {
            'first_name': 'John',
            'last_name': 'Doe'
        }
    }
    return render(request, 'email/welcome_new_user.html', context, status=200)


class UpdateProfileView(LoginRequiredMixin, TemplateView):
    """
    View for Update The Profile
    """
    template_name = "core/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = PasswordChangeForm(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        if 'update_profile' in request.POST:
            return self.handle_profile_update(request)
        elif 'change_password' in request.POST:
            return self.handle_password_change(request)
        return super().get(request, *args, **kwargs)

    def handle_profile_update(self, request):
        user = request.user
        try:
            # Update basic fields
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')

            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']

            user.full_clean()
            user.save()
            messages.success(request, 'Profile updated successfully!')
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")

        return redirect('profile')

    def handle_password_change(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect('profile')



# make a view for rendering a all_request page
def all_request(request):
    return render(request, 'core/all_request.html')

def AppointmentsView(request):
    return render(request, 'core/appointments.html')

def AnalyticsView(request):
    return render(request, 'core/analytics.html')

def EmergencyCallsView(request):
    return render(request, 'core/emergency_calls.html')

def CitizenPageView(request):
    return render(request, 'core/citizen_page.html')
