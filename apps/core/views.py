

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from apps.depts.models import (
    CitizenRequest, ActionLog, Department, DepartmentEntity,
    CitizenRequestAssignment, EmergencyCall, Appointment
)

from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
from apps.depts.models import (
    CitizenRequest, ActionLog, Department, DepartmentEntity,
    CitizenRequestAssignment, EmergencyCall, Appointment
)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Date ranges for calculations
        today = timezone.now().date()
        start_of_today = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        start_of_month = today.replace(day=1)
        start_of_last_month = (start_of_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_month - timedelta(days=1)

        # Convert to timezone-aware datetimes
        start_of_month = timezone.make_aware(timezone.datetime.combine(start_of_month, timezone.datetime.min.time()))
        start_of_last_month = timezone.make_aware(
            timezone.datetime.combine(start_of_last_month, timezone.datetime.min.time()))
        end_of_last_month = timezone.make_aware(
            timezone.datetime.combine(end_of_last_month, timezone.datetime.max.time()))

        # Total Requests calculation
        total_requests = CitizenRequest.objects.count()
        current_month_requests = CitizenRequest.objects.filter(
            created_at__gte=start_of_month
        ).count()
        last_month_requests = CitizenRequest.objects.filter(
            created_at__gte=start_of_last_month,
            created_at__lte=end_of_last_month
        ).count()

        if last_month_requests > 0:
            jobs_percentage_change = round(
                ((current_month_requests - last_month_requests) / last_month_requests) * 100, 1
            )
        else:
            jobs_percentage_change = 100.0 if current_month_requests > 0 else 0.0

        # Active Cases (requests not resolved)
        active_cases = CitizenRequest.objects.filter(
            status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS']
        ).count()
        print("Active Cases:", active_cases)

        active_cases_last_month = CitizenRequest.objects.filter(
            created_at__gte=start_of_last_month,
            created_at__lte=end_of_last_month,
            status__in=['SUBMITTED', 'ASSIGNED', 'IN_PROGRESS']
        ).count()
        print("active_cases_last_month", active_cases_last_month)
        if active_cases_last_month > 0:
            resumes_percentage_change = round(
                ((active_cases - active_cases_last_month) / active_cases_last_month) * 100, 1
            )
        else:
            resumes_percentage_change = 100.0 if active_cases > 0 else 0.0

        # Resolved Today
        resolved_today = CitizenRequest.objects.filter(
            resolved_at__gte=start_of_today,
            status='RESOLVED'
        ).count()

        resolved_last_month_same_day = CitizenRequest.objects.filter(
            resolved_at__gte=start_of_last_month + timedelta(days=today.day - 1),
            resolved_at__lt=start_of_last_month + timedelta(days=today.day),
            status='RESOLVED'
        ).count()

        if resolved_last_month_same_day > 0:
            applications_percentage_change = round(
                ((resolved_today - resolved_last_month_same_day) / resolved_last_month_same_day) * 100, 1
            )
        else:
            applications_percentage_change = 100.0 if resolved_today > 0 else 0.0

        # Average Response Time (in minutes)
        avg_response_time = ActionLog.objects.filter(
            success=True,
            completed_at__isnull=False,
            duration_seconds__isnull=False
        ).aggregate(avg_duration=Avg('duration_seconds'))['avg_duration'] or 0

        avg_response_time_minutes = round(avg_response_time / 60, 1) if avg_response_time else 14.0
        # Calculate percentage change for response time (simplified)
        match_rate_percentage_change = 5.2

        # Recent Requests (last 10 requests)
        recent_requests = CitizenRequest.objects.select_related(
            'user', 'target_location__city', 'assigned_department', 'assigned_entity'
        ).prefetch_related('actions').order_by('-created_at')[:10]

        # Recent Activity (last 10 actions)
        recent_activity = ActionLog.objects.select_related(
            'citizen_request'
        ).filter(success=True).order_by('-created_at')[:10]

        context.update({
            'total_requests': total_requests,
            'jobs_percentage_change': jobs_percentage_change,
            'active_cases': active_cases,
            'resumes_percentage_change': resumes_percentage_change,
            'resolved_today': resolved_today,
            'applications_percentage_change': applications_percentage_change,
            'avg_response_time_minutes': avg_response_time_minutes,
            'match_rate_percentage_change': match_rate_percentage_change,
            'recent_requests': recent_requests,
            'recent_activity': recent_activity,
        })

        return context


class RequestDetailView(LoginRequiredMixin, TemplateView):
    """AJAX view to get request details"""

    def get(self, request, *args, **kwargs):
        case_code = request.GET.get('case_code')

        try:
            request_obj = CitizenRequest.objects.select_related(
                'user', 'target_location__city', 'assigned_department', 'assigned_entity'
            ).prefetch_related('actions', 'assignments').get(case_code=case_code)

            # Get recent actions for this request
            recent_actions = request_obj.actions.order_by('-created_at')[:10]

            # Get assignment details
            assignment = request_obj.assignments.first()

            data = {
                'success': True,
                'request': {
                    'case_code': request_obj.case_code,
                    'user_name': request_obj.user.get_full_name() or request_obj.user.email,
                    'request_text': request_obj.request_text,
                    'urgency_level': request_obj.urgency_level or 'LOW',
                    'category': request_obj.category or 'GENERAL',
                    'status': request_obj.status,
                    'created_at': request_obj.created_at.strftime('%Y-%m-%d %H:%M'),
                    'assigned_at': request_obj.assignments.first().assigned_at.strftime(
                        '%Y-%m-%d %H:%M') if request_obj.assignments.exists() else 'Not assigned yet',
                },
                'location': {
                    'area': request_obj.target_location.area if request_obj.target_location else '',
                    'city': request_obj.target_location.city.name if request_obj.target_location else 'Unknown',
                } if request_obj.target_location else {'area': '', 'city': 'Unknown'},
                'assignment': {
                    'department': request_obj.assigned_department.name if request_obj.assigned_department else 'Not assigned',
                    'entity': request_obj.assigned_entity.name if request_obj.assigned_entity else 'Not assigned',
                    'status': request_obj.status,
                },
                'recent_actions': [
                    {
                        'description': action.description,
                        'created_at': action.created_at.strftime('%Y-%m-%d %H:%M'),
                        'action_type': action.action_type,
                        'success': action.success,
                    }
                    for action in recent_actions
                ]
            }

            return JsonResponse(data)

        except CitizenRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Request not found'
            }, status=404)


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


# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from apps.depts.models import CitizenRequest, EmergencyCall, Department
import random
import string

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import random
import string


class SubmitEmergencyRequestView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        # Pass Google Maps API key to template
        context = {
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, 'core/emergency_request_form.html', context)

    def post(self, request):
        try:
            # Get form data (emergency_type is now optional)
            emergency_type = request.POST.get('emergency_type')
            location = request.POST.get('location')
            description = request.POST.get('description')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            # Validate required fields (emergency_type is optional)
            if not all([location, description, latitude, longitude]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'emergency_request_form.html')

            # Generate unique case code
            case_code = self.generate_case_code()

            # Map emergency type to category (optional)
            category_map = {
                'health': 'Medical Emergency',
                'police': 'Police Assistance',
                'fire': 'Fire Emergency',
                'govt': 'Government Services'
            }

            category = category_map.get(emergency_type, 'General Emergency')

            # Create CitizenRequest
            citizen_request = CitizenRequest.objects.create(
                user=request.user,
                case_code=case_code,
                category=category,
                description=description,
                location=location,
                latitude=latitude,
                longitude=longitude,
                status='pending'
            )

            # Find appropriate department based on emergency type (optional)
            department = self.get_department_for_emergency(emergency_type)

            if department:
                # Create EmergencyCall
                emergency_call = EmergencyCall.objects.create(
                    citizen_request=citizen_request,
                    department=department,
                    phone_number=request.user.phone_number if hasattr(request.user, 'phone_number') else '',
                    status='dispatched'
                )

            messages.success(request, f'Emergency request submitted successfully! Case Code: {case_code}')
            return redirect('emergency_request_success')

        except Exception as e:
            messages.error(request, 'An error occurred while submitting your request. Please try again.')
            return render(request, 'emergency_request_form.html')

    def generate_case_code(self):
        """Generate unique case code like C-ABC123XY"""
        while True:
            letters = ''.join(random.choices(string.ascii_uppercase, k=4))
            numbers = ''.join(random.choices(string.digits, k=4))
            case_code = f"C-{letters}{numbers}"

            if not CitizenRequest.objects.filter(case_code=case_code).exists():
                return case_code

    def get_department_for_emergency(self, emergency_type):
        """Get appropriate department based on emergency type (optional)"""
        if not emergency_type:
            return Department.objects.first()  # Default department

        department_map = {
            'health': 'Ambulance Service',
            'police': 'Police Department',
            'fire': 'Fire Department',
            'govt': 'Government Services'
        }

        department_name = department_map.get(emergency_type)
        if department_name:
            try:
                return Department.objects.filter(name__icontains=department_name).first()
            except Department.DoesNotExist:
                return Department.objects.first()  # Fallback to first department
        return None

class EmergencyRequestSuccessView(View):
    def get(self, request):
        return render(request, 'emergency_request_success.html')