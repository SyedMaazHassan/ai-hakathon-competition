"""
Emergency Pipeline Service - Main Orchestrator
Combines all services into a complete emergency response flow

FLOW:
1. Router Agent → Classify request
2. Matcher Service → Find best entity
3. Department Orchestrator → Generate action plan
4. Trigger Orchestrator → Map to intelligent actions
5. Action Executor → Execute actions

Simple, efficient, demo-ready pipeline
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
import logging
import time
from datetime import datetime, timedelta
from django.utils import timezone

# Import all our services
from apps.depts.agents.router_agent.service import RouterAgentService
from apps.depts.services.matcher_service import MatcherService
from apps.depts.agents.department_orchestrator_agent.service import DepartmentOrchestratorService
from apps.depts.services.trigger_orchestrator_service import TriggerOrchestratorService, TriggerOrchestratorInput
from apps.depts.services.actions.action_executor import ActionExecutor
from apps.ai_agents.internal_agents.next_steps_agent import NextStepsAgentService, NextStepsInput

# Import database models
from apps.depts.models import (
    CitizenRequest, ActionLog, NotificationLog, EmergencyCall,
    Department, DepartmentEntity, City, Location, CitizenRequestAssignment
)
from apps.depts.choices import (
    CaseStatus, UrgencyLevel, ActionType, AgentType,
    DepartmentCategory, TriageSource, CallStatus, Province
)
from apps.authentication.models import CustomUser

logger = logging.getLogger(__name__)

# =============================================================================
# PIPELINE MODELS
# =============================================================================

class CitizenRequestInput(BaseModel):
    """Citizen's emergency request - Pipeline input"""
    request_text: str = Field(..., description="Citizen's emergency description")
    user_phone: Optional[str] = Field(None, description="Citizen's phone number")
    user_email: Optional[str] = Field(None, description="Citizen's email")
    user_city: Optional[str] = Field(None, description="Citizen's city")
    user_coordinates: Optional[Dict[str, float]] = Field(None, description="GPS coordinates {lat, lng}")
    priority_override: Optional[str] = Field(None, description="Manual priority override")
    # Add user identification
    user_id: Optional[int] = Field(None, description="User ID if authenticated")
    user_name: Optional[str] = Field("Anonymous", description="User's name")

class PipelineStep(BaseModel):
    """Individual pipeline step result"""
    step_name: str
    success: bool
    duration_ms: int
    output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class EmergencyPipelineOutput(BaseModel):
    """Complete pipeline execution result"""
    # Request info
    request_id: str
    citizen_request: CitizenRequestInput
    # Database record
    citizen_request_db_id: Optional[str] = None
    case_code: Optional[str] = None

    # Pipeline execution
    total_duration_ms: int
    pipeline_success: bool
    steps_executed: List[PipelineStep]

    # Results
    department_assigned: Optional[str] = None
    entity_matched: Optional[str] = None
    criticality_level: Optional[str] = None
    actions_triggered: Optional[int] = None
    actions_executed: Optional[int] = None

    # Outputs for user
    citizen_message: Optional[str] = None
    reference_number: Optional[str] = None

    # Error handling
    error_message: Optional[str] = None
    degraded_mode: bool = False

# =============================================================================
# EMERGENCY PIPELINE SERVICE
# =============================================================================

class EmergencyPipelineService:
    """
    Main pipeline orchestrator - combines all emergency response services
    """

    def __init__(self):
        self.router_service = RouterAgentService()
        self.matcher_service = MatcherService()
        self.dept_service = DepartmentOrchestratorService()
        self.trigger_service = TriggerOrchestratorService()
        self.action_executor = ActionExecutor()
        self.next_steps_service = NextStepsAgentService()

    def process_emergency_request(self, citizen_request: CitizenRequestInput) -> EmergencyPipelineOutput:
        """
        Main pipeline execution - processes complete emergency request

        Args:
            citizen_request: CitizenRequest with emergency details

        Returns:
            EmergencyPipelineOutput with complete results
        """
        request_id = f"EMR-{int(time.time())}"
        start_time = time.time()
        pipeline_steps = []

        logger.info(f"🚨 Starting emergency pipeline: {request_id}")
        logger.info(f"Request: {citizen_request.request_text[:100]}...")

        # Create initial database record
        try:
            citizen_request_db = self._create_citizen_request_record(citizen_request, request_id)
            logger.info(f"📝 Created database record: {citizen_request_db.case_code}")
        except Exception as e:
            logger.error(f"Failed to create database record: {e}")
            return self._create_error_response(request_id, citizen_request, [], f"Database error: {str(e)}")

        try:
            # Step 1: Router Agent
            router_result, step = self._execute_router_step(citizen_request)
            pipeline_steps.append(step)
            if not step.success:
                # Only log critical failures
                self._log_pipeline_step(
                    citizen_request_db,
                    step.step_name,
                    AgentType.REQUEST_ANALYSIS,
                    ActionType.CATEGORIZATION,
                    step.success,
                    {'error_message': step.error_message},
                    step.error_message
                )
                return self._create_error_response(request_id, citizen_request, pipeline_steps, step.error_message)

            # Step 2: Matcher Service
            matcher_result, step = self._execute_matcher_step(citizen_request, router_result)
            pipeline_steps.append(step)
            if not step.success:
                self._log_pipeline_step(
                    citizen_request_db,
                    step.step_name,
                    AgentType.LOCATION_MAPPING,
                    ActionType.LOCATION_MAPPING,
                    step.success,
                    {'error_message': step.error_message},
                    step.error_message
                )
                return self._create_error_response(request_id, citizen_request, pipeline_steps, step.error_message)

            # Step 3: Department Orchestrator
            dept_result, step = self._execute_department_step(citizen_request, router_result)
            pipeline_steps.append(step)
            if not step.success:
                self._log_pipeline_step(
                    citizen_request_db,
                    step.step_name,
                    AgentType.TRIAGE_AGENT,
                    ActionType.ANALYSIS,
                    step.success,
                    {'error_message': step.error_message},
                    step.error_message
                )
                return self._create_error_response(request_id, citizen_request, pipeline_steps, step.error_message)


            # Assignment will be created in finalization step


            # Step 4: Trigger Orchestrator
            trigger_result, step = self._execute_trigger_step(citizen_request, dept_result, matcher_result, router_result)
            pipeline_steps.append(step)
            if not step.success:
                self._log_pipeline_step(
                    citizen_request_db,
                    step.step_name,
                    AgentType.ESCALATION_AGENT,
                    ActionType.ESCALATION,
                    step.success,
                    {'error_message': step.error_message},
                    step.error_message
                )
                return self._create_error_response(request_id, citizen_request, pipeline_steps, step.error_message)

            # Step 5: Action Executor
            execution_result, step = self._execute_actions_step(trigger_result)
            pipeline_steps.append(step)
            # Actions can fail without stopping pipeline - only log if completely failed
            if not step.success:
                self._log_pipeline_step(
                    citizen_request_db,
                    step.step_name,
                    AgentType.COMMUNICATION_AGENT,
                    ActionType.SMS_SENT,
                    step.success,
                    {'error_message': step.error_message},
                    step.error_message
                )

            # Step 6: Generate Next Steps for Citizen
            next_steps_result = self._execute_next_steps(
                citizen_request, dept_result, matcher_result,
                execution_result.get("successful_actions", 0),
                citizen_request_db.case_code
            )

            # Update database record with final results
            self._finalize_citizen_request_record(
                citizen_request_db, router_result, matcher_result,
                dept_result, trigger_result, execution_result
            )

            # Create success response
            return self._create_success_response(
                request_id, citizen_request, pipeline_steps, start_time,
                router_result, matcher_result, dept_result, trigger_result, execution_result,
                citizen_request_db
            )

        except Exception as e:
            return self._create_error_response(request_id, citizen_request, pipeline_steps, str(e))

    def _execute_router_step(self, citizen_request: CitizenRequest):
        """Execute Router Agent step"""
        step_start = time.time()
        logger.info("📍 Step 1: Classifying request with Router Agent...")

        try:
            router_result = self.router_service.route_request(
                request_text=citizen_request.request_text,
                user_city=citizen_request.user_city,
                user_location=citizen_request.user_coordinates
            )

            step_duration = int((time.time() - step_start) * 1000)

            if router_result:
                step = PipelineStep(
                    step_name="Router Agent",
                    success=True,
                    duration_ms=step_duration,
                    output={
                        "department": router_result.department,
                        "confidence": router_result.confidence,
                        "reason": router_result.reason
                    }
                )
                logger.info(f"✅ Department: {router_result.department}")
                return router_result, step
            else:
                raise Exception("Router failed - no result returned")

        except Exception as e:
            step = PipelineStep(
                step_name="Router Agent",
                success=False,
                duration_ms=int((time.time() - step_start) * 1000),
                error_message=str(e)
            )
            return None, step

    def _execute_matcher_step(self, citizen_request: CitizenRequest, router_result):
        """Execute Matcher Service step"""
        step_start = time.time()
        logger.info("🎯 Step 2: Finding best department entity...")

        try:
            from apps.depts.services.matcher_service import MatcherInput

            matcher_input = MatcherInput(
                department_category=router_result.department,
                user_city=citizen_request.user_city,
                user_location=citizen_request.user_coordinates
            )

            matcher_result = self.matcher_service.find_best_entity(matcher_input)

            step_duration = int((time.time() - step_start) * 1000)

            if matcher_result.success and matcher_result.matched_entity:
                step = PipelineStep(
                    step_name="Matcher Service",
                    success=True,
                    duration_ms=step_duration,
                    output={
                        "entity_name": matcher_result.matched_entity.name,
                        "entity_phone": matcher_result.matched_entity.phone,
                        "distance_km": matcher_result.matched_entity.distance_km,
                        "match_reason": matcher_result.matched_entity.match_reason
                    }
                )
                logger.info(f"✅ Matched: {matcher_result.matched_entity.name}")

                return matcher_result, step
            else:
                raise Exception(f"Matcher failed: {matcher_result.error_message}")

        except Exception as e:
            step = PipelineStep(
                step_name="Matcher Service",
                success=False,
                duration_ms=int((time.time() - step_start) * 1000),
                error_message=str(e)
            )
            return None, step

    def _execute_department_step(self, citizen_request: CitizenRequest, router_result):
        """Execute Department Orchestrator step"""
        step_start = time.time()
        logger.info("🏛️ Step 3: Generating department action plan...")

        try:
            from apps.depts.agents.department_orchestrator_agent.pydantic_models import DepartmentOrchestratorInput

            dept_input = DepartmentOrchestratorInput(
                original_request=citizen_request.request_text,
                router_decision=router_result,
                user_city=citizen_request.user_city,
                user_location=citizen_request.user_coordinates
            )

            dept_result = self.dept_service.process_request(dept_input)

            step_duration = int((time.time() - step_start) * 1000)

            if dept_result.success:
                step = PipelineStep(
                    step_name="Department Orchestrator",
                    success=True,
                    duration_ms=step_duration,
                    output={
                        "criticality": dept_result.criticality,
                        "communication_method": dept_result.communication_method,
                        "immediate_actions": len(dept_result.action_plan.immediate_actions),
                        "follow_up_actions": len(dept_result.action_plan.follow_up_actions)
                    }
                )
                logger.info(f"✅ Criticality: {dept_result.criticality}")
                return dept_result, step
            else:
                raise Exception(f"Department orchestrator failed: {dept_result.error_message}")

        except Exception as e:
            step = PipelineStep(
                step_name="Department Orchestrator",
                success=False,
                duration_ms=int((time.time() - step_start) * 1000),
                error_message=str(e)
            )
            return None, step

    def _execute_trigger_step(self, citizen_request: CitizenRequest, dept_result, matcher_result, router_result):
        """Execute Trigger Orchestrator step"""
        step_start = time.time()
        logger.info("⚡ Step 4: Mapping to intelligent actions...")

        try:
            trigger_input = TriggerOrchestratorInput(
                department_output=dept_result,
                entity_info=matcher_result.matched_entity,
                router_decision=router_result,
                user_phone=citizen_request.user_phone,
                user_email=citizen_request.user_email,
                user_coordinates=citizen_request.user_coordinates
            )

            trigger_result = self.trigger_service.orchestrate_triggers(trigger_input)

            step_duration = int((time.time() - step_start) * 1000)

            if trigger_result.success:
                step = PipelineStep(
                    step_name="Trigger Orchestrator",
                    success=True,
                    duration_ms=step_duration,
                    output={
                        "actions_triggered": len(trigger_result.triggered_actions),
                        "execution_plan": trigger_result.execution_plan,
                        "estimated_time": trigger_result.total_estimated_time
                    }
                )
                logger.info(f"✅ Actions: {len(trigger_result.triggered_actions)}")
                return trigger_result, step
            else:
                raise Exception(f"Trigger orchestrator failed: {trigger_result.error_message}")

        except Exception as e:
            step = PipelineStep(
                step_name="Trigger Orchestrator",
                success=False,
                duration_ms=int((time.time() - step_start) * 1000),
                error_message=str(e)
            )
            return None, step

    def _execute_actions_step(self, trigger_result):
        """Execute Actions step"""
        step_start = time.time()
        logger.info("🚀 Step 5: Executing emergency actions...")

        try:
            # For V1: Execute synchronously (V2 will be background tasks)
            execution_result = self.action_executor.execute_multiple_actions(
                trigger_result.triggered_actions,
                parallel=True
            )

            step_duration = int((time.time() - step_start) * 1000)

            step = PipelineStep(
                step_name="Action Executor",
                success=True,
                duration_ms=step_duration,
                output={
                    "total_actions": execution_result["total_actions"],
                    "successful_actions": execution_result["successful_actions"],
                    "failed_actions": execution_result["failed_actions"],
                    "execution_mode": execution_result["execution_mode"]
                }
            )
            logger.info(f"✅ Executed: {execution_result['successful_actions']}/{execution_result['total_actions']}")
            return execution_result, step

        except Exception as e:
            step = PipelineStep(
                step_name="Action Executor",
                success=False,
                duration_ms=int((time.time() - step_start) * 1000),
                error_message=str(e)
            )
            logger.warning(f"⚠️ Action execution failed: {e}")
            return {"successful_actions": 0, "total_actions": 0}, step

    def _create_success_response(self, request_id, citizen_request, pipeline_steps, start_time,
                               router_result, matcher_result, dept_result, trigger_result, execution_result,
                               citizen_request_db):
        """Create successful pipeline response"""
        total_duration = int((time.time() - start_time) * 1000)

        logger.info(f"🎉 Pipeline completed successfully in {total_duration}ms")

        return EmergencyPipelineOutput(
            request_id=request_id,
            citizen_request=citizen_request,
            citizen_request_db_id=citizen_request_db.id,  # UUID string from BaseModel
            case_code=citizen_request_db.case_code,
            total_duration_ms=total_duration,
            pipeline_success=True,
            steps_executed=pipeline_steps,
            department_assigned=router_result.department,
            entity_matched=matcher_result.matched_entity.name,
            criticality_level=dept_result.criticality,
            actions_triggered=len(trigger_result.triggered_actions),
            actions_executed=execution_result.get("successful_actions", 0),
            reference_number=next_steps_result.reference_number,
            citizen_message=next_steps_result.citizen_message
        )

    def _create_citizen_request_record(self, citizen_request: CitizenRequestInput, request_id: str):
        """Create initial CitizenRequest database record"""

        # Get or create user
        user = None
        if citizen_request.user_id:
            try:
                user = CustomUser.objects.get(id=citizen_request.user_id)
            except CustomUser.DoesNotExist:
                pass

        if not user:
            # Create anonymous user for demo
            user, created = CustomUser.objects.get_or_create(
                email=citizen_request.user_email or f"anonymous_{request_id}@demo.com",
                defaults={
                    'first_name': citizen_request.user_name or "Anonymous",
                    'last_name': "User",
                    'phone': citizen_request.user_phone or "",
                    'is_active': True
                }
            )

        # Get or create city if provided
        target_location = None
        if citizen_request.user_city:
            city, created = City.objects.get_or_create(
                name=citizen_request.user_city,
                province=Province.PUNJAB,  # Default for demo
                defaults={'is_major_city': True}
            )

            if citizen_request.user_coordinates:
                location, created = Location.objects.get_or_create(
                    lat=citizen_request.user_coordinates.get('lat'),
                    lng=citizen_request.user_coordinates.get('lng'),
                    city=city,
                    defaults={'area': f"Area near {citizen_request.user_city}"}
                )
                target_location = location

        # Create CitizenRequest
        citizen_request_db = CitizenRequest.objects.create(
            user=user,
            request_text=citizen_request.request_text,
            target_location=target_location,
            status=CaseStatus.ANALYZING,
            triage_source=TriageSource.LLM
        )

        # Log initial action
        ActionLog.objects.create(
            citizen_request=citizen_request_db,
            agent_type=AgentType.REQUEST_ANALYSIS,
            action_type=ActionType.ANALYSIS,
            description=f"Emergency request received: {citizen_request.request_text[:100]}...",
            success=True,
            details={
                'request_id': request_id,
                'has_phone': bool(citizen_request.user_phone),
                'has_email': bool(citizen_request.user_email),
                'user_city': citizen_request.user_city,
                'has_coordinates': bool(citizen_request.user_coordinates)
            }
        )

        return citizen_request_db

    def _log_pipeline_step(self, citizen_request_db, step_name: str, agent_type: str, action_type: str,
                          success: bool, details: dict, error_message: str = None):
        """Log pipeline step to ActionLog"""
        ActionLog.objects.create(
            citizen_request=citizen_request_db,
            agent_type=agent_type,
            action_type=action_type,
            description=f"{step_name}: {details.get('description', 'Processing step')}",
            success=success,
            error_message=error_message or "",  # Provide empty string instead of None
            details=details,
            completed_at=timezone.now()
        )

    def _finalize_citizen_request_record(self, citizen_request_db, router_result, matcher_result,
                                       dept_result, trigger_result, execution_result):
        """Update CitizenRequest with final pipeline results"""

        try:
            # Map urgency level
            urgency_mapping = {
                'critical': UrgencyLevel.CRITICAL,
                'high': UrgencyLevel.HIGH,
                'medium': UrgencyLevel.MEDIUM,
                'low': UrgencyLevel.LOW
            }

            # Get assigned department and entity
            assigned_dept = None
            assigned_entity = None

            if hasattr(router_result, 'department'):
                try:
                    assigned_dept = Department.objects.filter(
                        category=router_result.department,
                        is_active=True
                    ).first()
                except:
                    pass

            if matcher_result.matched_entity:
                try:
                    assigned_entity = DepartmentEntity.objects.filter(
                        name=matcher_result.matched_entity.name,
                        is_active=True
                    ).first()
                except:
                    pass

            # Update the record
            citizen_request_db.category = router_result.department if hasattr(router_result, 'department') else None
            citizen_request_db.urgency_level = urgency_mapping.get(dept_result.criticality, UrgencyLevel.MEDIUM)
            citizen_request_db.confidence_score = getattr(router_result, 'confidence', 0.8)
            citizen_request_db.ai_response = dept_result.rationale
            citizen_request_db.assigned_department = assigned_dept
            citizen_request_db.assigned_entity = assigned_entity
            citizen_request_db.status = CaseStatus.ASSIGNED if execution_result.get("successful_actions", 0) > 0 else CaseStatus.IN_PROGRESS
            citizen_request_db.is_emergency = (dept_result.criticality in ['critical', 'high'])
            citizen_request_db.expected_response_time = timezone.now() + timedelta(minutes=30)  # Default 30 min response

            citizen_request_db.save()

            # Create assignment record
            if assigned_entity:
                CitizenRequestAssignment.objects.create(
                    citizen_request=citizen_request_db,
                    department_entity=assigned_entity,
                    priority_override=dept_result.criticality
                )

            # Log completion
            self._log_pipeline_step(
                citizen_request_db,
                "Pipeline Completion",
                AgentType.REQUEST_ANALYSIS,
                ActionType.DEPARTMENT_ASSIGNMENT,
                True,
                {
                    'description': 'Emergency pipeline processing completed successfully',
                    'total_actions': execution_result.get("total_actions", 0),
                    'successful_actions': execution_result.get("successful_actions", 0),
                    'criticality': dept_result.criticality,
                    'assigned_department': router_result.department if hasattr(router_result, 'department') else None,
                    'assigned_entity': matcher_result.matched_entity.name if matcher_result.matched_entity else None
                }
            )

        except Exception as e:
            logger.error(f"Failed to finalize database record: {e}")

    def _execute_next_steps(self, citizen_request, dept_result, matcher_result, actions_taken, case_code):
        """Execute Next Steps Agent to generate citizen communication"""
        try:
            next_steps_input = NextStepsInput(
                request_summary=citizen_request.request_text[:100],  # First 100 chars
                department_name=dept_result.department_assignment if hasattr(dept_result, 'department_assignment') else "Emergency Services",
                entity_name=matcher_result.matched_entity.name,
                criticality_level=dept_result.criticality,
                actions_taken=actions_taken,
                case_code=case_code
            )

            next_steps = self.next_steps_service.generate_next_steps(next_steps_input)
            next_steps_dict = next_steps.model_dump()
            citizen_request.output_json = next_steps_dict
            print(next_steps_dict)
            logger.info(f"Next Steps Generated: {next_steps_dict}")
            citizen_request.save(update_fields=["output_json"])
            return next_steps

        except Exception as e:
            logger.error(f"Next Steps Agent failed: {str(e)}")
            # Return fallback response
            from apps.ai_agents.internal_agents.next_steps_agent import NextStepsOutput
            return NextStepsOutput(
                citizen_message="Your emergency request has been processed. You will be contacted soon.",
                reference_number=case_code,
                next_steps=["Keep your phone available", "Check messages regularly"],
                expected_timeline="Within 24 hours",
                contact_info="Contact your local emergency services for updates",
                success=False,
                error_message=str(e)
            )

    def _create_error_response(self, request_id: str, citizen_request: CitizenRequestInput,
                             pipeline_steps: List[PipelineStep], error_message: str) -> EmergencyPipelineOutput:
        """Create error response for failed pipeline"""
        logger.error(f"❌ Pipeline failed: {error_message}")

        return EmergencyPipelineOutput(
            request_id=request_id,
            citizen_request=citizen_request,
            total_duration_ms=sum(step.duration_ms for step in pipeline_steps),
            pipeline_success=False,
            steps_executed=pipeline_steps,
            error_message=error_message,
            degraded_mode=True,
            citizen_message=f"Emergency request received but system error occurred. Please call emergency services directly: 15 (Police) / 1122 (Rescue). Reference: {request_id}"
        )

# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def process_citizen_emergency(
    request_text: str,
    user_phone: str = None,
    user_email: str = None,
    user_city: str = None,
    user_coordinates: Dict[str, float] = None,
    user_id: int = None,
    user_name: str = "Anonymous"
) -> EmergencyPipelineOutput:
    """
    Convenience function to process emergency request with database persistence

    Args:
        request_text: Citizen's emergency description
        user_phone: Phone number
        user_email: Email address
        user_city: City name
        user_coordinates: GPS coordinates
        user_id: User ID if authenticated
        user_name: User's name

    Returns:
        EmergencyPipelineOutput with complete results and database record
    """

    citizen_request = CitizenRequestInput(
        request_text=request_text,
        user_phone=user_phone,
        user_email=user_email,
        user_city=user_city,
        user_coordinates=user_coordinates,
        user_id=user_id,
        user_name=user_name
    )

    pipeline = EmergencyPipelineService()
    return pipeline.process_emergency_request(citizen_request)

# Global instance for easy access
EMERGENCY_PIPELINE = EmergencyPipelineService()