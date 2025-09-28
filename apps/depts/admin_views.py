from django.db import models
from django.shortcuts import render
from .models import Department, DepartmentEntity


def admin_dashboard(request):
    """Admin dashboard showing department models data"""

    # Get all departments with their statistics
    departments = Department.objects.filter(is_active=True).prefetch_related('entities')

    # Get department entities with their statistics
    entities = DepartmentEntity.objects.filter(is_active=True).select_related('department', 'city')

    # Calculate statistics
    total_departments = departments.count()
    total_entities = entities.count()
    active_departments = departments.filter(is_24x7=True).count()
    avg_response_time = departments.exclude(response_time_minutes__isnull=True).aggregate(
        avg_time=models.Avg('response_time_minutes')
    )['avg_time'] or 0

    # Group entities by department category
    entities_by_category = {}
    for entity in entities:
        category = entity.department.category
        if category not in entities_by_category:
            entities_by_category[category] = []
        entities_by_category[category].append(entity)

    context = {
        'departments': departments,
        'entities': entities,
        'total_departments': total_departments,
        'total_entities': total_entities,
        'active_departments': active_departments,
        'avg_response_time': round(avg_response_time, 1),
        'entities_by_category': entities_by_category,
    }

    return render(request, 'depts/admin_dashboard.html', context)