"""
Simplified Emergency Pipeline Service
Clean, maintainable version that preserves all functionality
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from typing import Optional, Dict, List, Any
import logging
import time
from pydantic import BaseModel, Field

# Import services
from apps.depts.agents.router_agent.service import RouterAgentService
from apps.depts.services.matcher_service import MatcherService, MatcherInput
from apps.depts.agents.department_orchestrator_agent.service import DepartmentOrchestratorService
from apps.depts.agents.department_orchestrator_agent.pydantic_models import DepartmentOrchestratorInput
from apps.depts.services.trigger_orchestrator_service import TriggerOrchestratorService, TriggerOrchestratorInput
from apps.depts.services.actions.action_executor import ActionExecutor
from apps.ai_agents.internal_agents.next_steps_agent import NextStepsAgentService, NextStepsInput
from apps.depts.services.database_service import EmergencyDatabaseService
from apps.depts.services.actions.vapi_call_agent import EmergencyCallAgent

# Import models
from apps.depts.models import CitizenRequest

logger = logging.getLogger(__name__)

class EmergencyRequest(BaseModel):
    """Simplified request model - uses Django models directly"""
    request_text: str = Field(..., description="Emergency description")
    user_phone: Optional[str] = Field(None, description="Phone number")
    user_email: Optional[str] = Field(None, description="Email address")
    user_city: Optional[str] = Field(None, description="City name")
    user_coordinates: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")
    user_id: Optional[int] = Field(None, description="User ID if authenticated")
    user_name: Optional[str] = Field("Anonymous", description="User's name")

class PipelineResult(BaseModel):
    """Simplified result model"""
    success: bool
    request_id: str
    case_code: Optional[str] = None
    citizen_request_id: Optional[str] = None
    
    # Results
    department_assigned: Optional[str] = None
    entity_matched: Optional[str] = None
    criticality_level: Optional[str] = None
    actions_executed: Optional[int] = None
    
    # User response
    citizen_message: Optional[str] = None
    reference_number: Optional[str] = None
    
    # Error handling
    error_message: Optional[str] = None
    total_duration_ms: int = 0

class SimplifiedEmergencyPipeline:
    """
    Simplified emergency pipeline - clean and maintainable
    Preserves all original functionality
    """
    
    def __init__(self):
        self.router_service = RouterAgentService()
        self.matcher_service = MatcherService()
        self.dept_service = DepartmentOrchestratorService()
        self.trigger_service = TriggerOrchestratorService()
        self.action_executor = ActionExecutor()
        self.next_steps_service = NextStepsAgentService()
        self.db_service = EmergencyDatabaseService()

    def process_emergency_request(self, request: EmergencyRequest) -> PipelineResult:
        """
        Main pipeline execution - simplified but complete
        
        Args:
            request: EmergencyRequest with all necessary data
            
        Returns:
            PipelineResult with complete results
        """
        request_id = f"EMR-{int(time.time())}"
        start_time = time.time()
        
        logger.info(f"🚨 Processing emergency request: {request_id}")
        logger.info(f"Request: {request.request_text[:100]}...")

        # Convert to dict for database service
        request_data = request.dict()

        try:
            # 1. Create database record
            citizen_request = self.db_service.create_citizen_request(request_data, request_id)
            logger.info(f"📝 Created database record: {citizen_request.case_code}")

            # 2. Process through pipeline steps
            router_result = self._process_router_step(request)
            matcher_result = self._process_matcher_step(request, router_result)
            dept_result = self._process_department_step(request, router_result)
            trigger_result = self._process_trigger_step(request, router_result, matcher_result, dept_result)
            execution_result = self._process_actions_step(trigger_result)
            
            # 3. Generate citizen response
            next_steps_result = self._process_next_steps(request, dept_result, matcher_result, execution_result, citizen_request.case_code)
            
            # 4. Update database with results
            self.db_service.update_request_with_results(
                citizen_request, router_result, matcher_result, dept_result, execution_result
            )

            # 5. Create success response
            total_duration = int((time.time() - start_time) * 1000)
            logger.info(f"🎉 Pipeline completed successfully in {total_duration}ms")

            return PipelineResult(
                success=True,
                request_id=request_id,
                case_code=citizen_request.case_code,
                citizen_request_id=str(citizen_request.id),
                department_assigned=router_result.department,
                entity_matched=matcher_result.matched_entity.name if matcher_result.matched_entity else None,
                criticality_level=dept_result.criticality,
                actions_executed=execution_result.get("successful_actions", 0),
                citizen_message=next_steps_result.citizen_message,
                reference_number=next_steps_result.reference_number,
                total_duration_ms=total_duration
            )

        except Exception as e:
            # Handle errors gracefully
            logger.error(f"❌ Pipeline failed: {str(e)}")
            total_duration = int((time.time() - start_time) * 1000)
            
            # Log error to database if we have a citizen_request
            try:
                if 'citizen_request' in locals():
                    self.db_service.log_error(citizen_request, "Pipeline Execution", str(e))
            except:
                pass  # Don't let logging errors break the response

            return PipelineResult(
                success=False,
                request_id=request_id,
                error_message=str(e),
                total_duration_ms=total_duration,
                citizen_message=f"Emergency request received but system error occurred. Please call emergency services directly: 15 (Police) / 1122 (Rescue). Reference: {request_id}"
            )

    def _process_router_step(self, request: EmergencyRequest):
        """Process router step"""
        logger.info("📍 Step 1: Classifying request...")
        
        router_result = self.router_service.route_request(
            request_text=request.request_text,
            user_city=request.user_city,
            user_location=request.user_coordinates
        )
        
        if not router_result:
            raise Exception("Router failed - no result returned")
            
        logger.info(f"✅ Department: {router_result.department}")
        return router_result

    def _process_matcher_step(self, request: EmergencyRequest, router_result):
        """Process matcher step"""
        logger.info("🎯 Step 2: Finding best department entity...")
        
        matcher_input = MatcherInput(
            department_category=router_result.department,
            user_city=request.user_city,
            user_location=request.user_coordinates
        )
        
        matcher_result = self.matcher_service.find_best_entity(matcher_input)
        
        if not matcher_result.success or not matcher_result.matched_entity:
            raise Exception(f"Matcher failed: {matcher_result.error_message}")
            
        logger.info(f"✅ Matched: {matcher_result.matched_entity.name}")
        return matcher_result

    def _process_department_step(self, request: EmergencyRequest, router_result):
        """Process department orchestrator step"""
        logger.info("🏛️ Step 3: Generating department action plan...")
        
        dept_input = DepartmentOrchestratorInput(
            original_request=request.request_text,
            router_decision=router_result,
            user_city=request.user_city,
            user_location=request.user_coordinates
        )
        
        dept_result = self.dept_service.process_request(dept_input)
        
        if not dept_result.success:
            raise Exception(f"Department orchestrator failed: {dept_result.error_message}")
            
        logger.info(f"✅ Criticality: {dept_result.criticality}")
        return dept_result

    def _process_trigger_step(self, request: EmergencyRequest, router_result, matcher_result, dept_result):
        """Process trigger orchestrator step"""
        logger.info("⚡ Step 4: Mapping to intelligent actions...")


        # Make an emergency call
        call_agent = EmergencyCallAgent()
        call_result = call_agent.make_emergency_call(
            # phone_number=matcher_result.matched_entity.phone,
            phone_number="+923472533106",
            call_reason=dept_result.request_plan.incident_summary,
            additional_context={
                "longi"
                "user_city": request.user_city,
                "user_coordinates": request.user_coordinates,
                "request_plan": dept_result.request_plan.model_dump_json(),
                "emergency_type": dept_result.request_plan.incident_summary,
                "location": dept_result.request_plan.location_details,
                "reported_by": request.user_name,
                "urgency_level": dept_result.criticality,
                "additional_notes": dept_result.request_plan.additional_context
            }
        )
        
        trigger_input = TriggerOrchestratorInput(
            department_output=dept_result,
            entity_info=matcher_result.matched_entity,
            router_decision=router_result,
            user_phone=request.user_phone,
            user_email=request.user_email,
            user_coordinates=request.user_coordinates
        )
        
        trigger_result = self.trigger_service.orchestrate_triggers(trigger_input)
        
        if not trigger_result.success:
            raise Exception(f"Trigger orchestrator failed: {trigger_result.error_message}")
            
        logger.info(f"✅ Actions: {len(trigger_result.triggered_actions)}")
        return trigger_result

    def _process_actions_step(self, trigger_result):
        """Process action execution step"""
        logger.info("🚀 Step 5: Executing emergency actions...")
        
        execution_result = self.action_executor.execute_multiple_actions(
            trigger_result.triggered_actions,
            parallel=True
        )
        
        logger.info(f"✅ Executed: {execution_result['successful_actions']}/{execution_result['total_actions']}")
        return execution_result

    def _process_next_steps(self, request: EmergencyRequest, dept_result, matcher_result, execution_result, case_code):
        """Process next steps generation"""
        logger.info("📋 Step 6: Generating citizen response...")
        
        try:
            # Create properly formatted input with all required fields
            next_steps_input = NextStepsInput(
                user_request=request.request_text,
                department_response_plan=dept_result.rationale,
                required_user_actions=dept_result.request_plan.required_response,
                criticality_level=dept_result.criticality,
                entity_name=matcher_result.matched_entity.name if matcher_result.matched_entity else 'Emergency Services',
                case_code=case_code,
                incident_summary=dept_result.request_plan.incident_summary,
                location_details=dept_result.request_plan.location_details
            )
            
            return self.next_steps_service.generate_next_steps(next_steps_input)
            
        except Exception as e:
            logger.error(f"Next Steps Agent failed: {str(e)}")
            # Return fallback response with all required fields
            from apps.ai_agents.internal_agents.next_steps_agent import NextStepsOutput
            return NextStepsOutput(
                citizen_message="Your emergency request has been processed. You will be contacted soon.",
                actionable_steps=["Keep your phone available", "Check messages regularly", "Stay at a safe location"],
                reference_number=case_code,
                urgency_indicator="Help is being dispatched to your location",
                help_arriving_info="Emergency services have been notified and are responding",
                success=False,
                error_message=str(e)
            )

# Convenience function
def process_citizen_emergency(
    request_text: str,
    user_phone: str = None,
    user_email: str = None,
    user_city: str = None,
    user_coordinates: Dict[str, float] = None,
    user_id: int = None,
    user_name: str = "Anonymous"
) -> PipelineResult:
    """
    Convenience function to process emergency request
    
    Args:
        request_text: Citizen's emergency description
        user_phone: Phone number
        user_email: Email address
        user_city: City name
        user_coordinates: GPS coordinates
        user_id: User ID if authenticated
        user_name: User's name
        
    Returns:
        PipelineResult with complete results
    """
    
    request = EmergencyRequest(
        request_text=request_text,
        user_phone=user_phone,
        user_email=user_email,
        user_city=user_city,
        user_coordinates=user_coordinates,
        user_id=user_id,
        user_name=user_name
    )
    
    pipeline = SimplifiedEmergencyPipeline()
    return pipeline.process_emergency_request(request)

# Global instance for easy access
SIMPLIFIED_EMERGENCY_PIPELINE = SimplifiedEmergencyPipeline()
