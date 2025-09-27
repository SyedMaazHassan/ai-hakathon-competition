from django.db import models
from .models import CitizenRequest
from django.views.generic import ListView
from .models import EmergencyCall



class CitizenRequestListView(ListView):
    model = CitizenRequest
    template_name = "citizen_request_list.html"
    context_object_name = "requests"
    paginate_by = 25  # optional pagination

    # Optional: Order by most recent by default
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(case_code__icontains=search) |
                models.Q(user__first_name__icontains=search) |
                models.Q(user__last_name__icontains=search) |
                models.Q(category__icontains=search)
            )
        return queryset


class EmergencyCallListView(ListView):
    model = EmergencyCall
    template_name = "emergency_call_list.html"
    context_object_name = "calls"
    paginate_by = 25
    ordering = ['-initiated_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(citizen_request__case_code__icontains=search) |
                models.Q(department__name__icontains=search) |
                models.Q(status__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        # Add counts to context based on actual fields
        context['dispatched_count'] = queryset.filter(status='dispatched').count()
        context['in_progress_count'] = queryset.filter(status='in_progress').count()
        context['completed_count'] = queryset.filter(status='completed').count()
        context['answered_count'] = queryset.filter(status='answered').count()

        return context