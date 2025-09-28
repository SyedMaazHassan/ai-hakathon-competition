"""
Database Service - Handles all database operations for emergency pipeline
Keeps the main pipeline service focused on orchestration
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from typing import Optional, Dict, Any
from datetime import timedelta
from django.utils import timezone
from django.utils.crypto import get_random_string

from apps.depts.models import (
    CitizenRequest, ActionLog, CitizenRequestAssignment,
    Department, DepartmentEntity, City, Location
)
from apps.depts.choices import (
    CaseStatus, UrgencyLevel, ActionType, AgentType,
    DepartmentCategory, TriageSource, Province,
    UrgencyLevel
)
from apps.authentication.models import CustomUser

class EmergencyDatabaseService:
    """Handles all database operations for emergency pipeline"""
    
    @staticmethod
    def create_citizen_request(request_data: Dict[str, Any], request_id: str) -> CitizenRequest:
        """Create initial CitizenRequest record"""
        
        # Get or create user
        user = None
        if request_data.get('user_id'):
            try:
                user = CustomUser.objects.get(id=request_data['user_id'])
            except CustomUser.DoesNotExist:
                pass

        if not user:
            # Create anonymous user for demo
            user, created = CustomUser.objects.get_or_create(
                email=request_data.get('user_email') or f"anonymous_{request_id}@demo.com",
                defaults={
                    'first_name': request_data.get('user_name', 'Anonymous'),
                    'last_name': "User",
                    'is_active': True
                }
            )

        # Get or create location
        target_location = EmergencyDatabaseService._get_or_create_location(request_data)

        # Create CitizenRequest
        citizen_request = CitizenRequest.objects.create(
            user=user,
            request_text=request_data['request_text'],
            target_location=target_location,
            status=CaseStatus.ANALYZING,
            triage_source=TriageSource.LLM
        )

        # Log initial action
        ActionLog.objects.create(
            citizen_request=citizen_request,
            agent_type=AgentType.REQUEST_ANALYSIS,
            action_type=ActionType.ANALYSIS,
            description=f"Emergency request received: {request_data['request_text'][:100]}...",
            success=True,
            details={
                'request_id': request_id,
                'has_phone': bool(request_data.get('user_phone')),
                'has_email': bool(request_data.get('user_email')),
                'user_city': request_data.get('user_city'),
                'has_coordinates': bool(request_data.get('user_coordinates'))
            }
        )

        return citizen_request

    @staticmethod
    def _get_or_create_location(request_data: Dict[str, Any]) -> Optional[Location]:
        """Get or create location from request data"""
        if not request_data.get('user_city'):
            return None

        city, created = City.objects.get_or_create(
            name=request_data['user_city'],
            province=Province.PUNJAB,  # Default for demo
            defaults={'is_major_city': True}
        )

        if request_data.get('user_coordinates'):
            location, created = Location.objects.get_or_create(
                lat=request_data['user_coordinates'].get('lat'),
                lng=request_data['user_coordinates'].get('lng'),
                city=city,
                defaults={'area': f"Area near {request_data['user_city']}"}
            )
            return location

        return None

    @staticmethod
    def update_request_with_results(
        citizen_request: CitizenRequest,
        router_result,
        matcher_result,
        dept_result,
        execution_result: Dict[str, Any]
    ) -> None:
        """Update CitizenRequest with final pipeline results"""
        
        # Map urgency level - dept_result.criticality comes as string, need to map to enum
        urgency_mapping = {
            'critical': UrgencyLevel.CRITICAL,
            'high': UrgencyLevel.HIGH,
            'medium': UrgencyLevel.MEDIUM,
            'low': UrgencyLevel.LOW
        }

        # Get assigned department and entity
        assigned_dept = EmergencyDatabaseService._get_department(router_result)
        assigned_entity = EmergencyDatabaseService._get_entity(matcher_result)

        # Update the record
        citizen_request.category = getattr(router_result, 'department', None)
        citizen_request.urgency_level = urgency_mapping.get(dept_result.criticality, UrgencyLevel.MEDIUM)
        citizen_request.confidence_score = getattr(router_result, 'confidence', 0.8)
        citizen_request.ai_response = getattr(dept_result, 'rationale', '')
        citizen_request.assigned_department = assigned_dept
        citizen_request.assigned_entity = assigned_entity
        citizen_request.status = CaseStatus.ASSIGNED if execution_result.get("successful_actions", 0) > 0 else CaseStatus.IN_PROGRESS
        citizen_request.is_emergency = (dept_result.criticality in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH])
        citizen_request.expected_response_time = timezone.now() + timedelta(minutes=30)

        citizen_request.save()

        # Create assignment record with detailed notes from request_plan
        if assigned_entity:
            # Create comprehensive assignment notes from request_plan
            assignment_notes = f"""INCIDENT SUMMARY: {dept_result.request_plan.incident_summary}

LOCATION DETAILS: {dept_result.request_plan.location_details}

ADDITIONAL CONTEXT: {dept_result.request_plan.additional_context}

REQUIRED RESPONSE: {dept_result.request_plan.required_response}

DEPARTMENT RATIONALE: {dept_result.rationale}"""

            CitizenRequestAssignment.objects.create(
                citizen_request=citizen_request,
                department_entity=assigned_entity,
                priority_override=dept_result.criticality,
                assignment_notes=assignment_notes
            )

        # Log completion
        ActionLog.objects.create(
            citizen_request=citizen_request,
            agent_type=AgentType.REQUEST_ANALYSIS,
            action_type=ActionType.DEPARTMENT_ASSIGNMENT,
            description='Emergency pipeline processing completed successfully',
            success=True,
            details={
                'total_actions': execution_result.get("total_actions", 0),
                'successful_actions': execution_result.get("successful_actions", 0),
                'criticality': dept_result.criticality,
                'assigned_department': getattr(router_result, 'department', None),
                'assigned_entity': matcher_result.matched_entity.name if matcher_result.matched_entity else None
            }
        )

    @staticmethod
    def _get_department(router_result):
        """Get department from router result"""
        return Department.objects.filter(
            category=getattr(router_result, 'department', None),
            is_active=True
        ).first()

    @staticmethod
    def _get_entity(matcher_result):
        """Get entity from matcher result"""
        if not matcher_result.matched_entity:
            return None
            
        return DepartmentEntity.objects.filter(
            name=matcher_result.matched_entity.name,
            is_active=True
        ).first()

    @staticmethod
    def log_error(citizen_request: CitizenRequest, step_name: str, error_message: str, agent_type: str = None, action_type: str = None):
        """Log error to ActionLog"""
        ActionLog.objects.create(
            citizen_request=citizen_request,
            agent_type=agent_type or AgentType.REQUEST_ANALYSIS,
            action_type=action_type or ActionType.ANALYSIS,
            description=f"{step_name} failed",
            success=False,
            error_message=error_message,
            details={'error': error_message}
        )
