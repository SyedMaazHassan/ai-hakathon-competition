"""
SIMPLE EMERGENCY SERVICES PIPELINE
Input: User request text
Output: Complete processed result with actions taken

This is the MAIN orchestrator - keeps it simple!
"""
import os
import sys
import django
from pathlib import Path
import time
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.depts.agents.schemas import (
    UserRequestInput, RouterInput, DepartmentAgentInput,
    PipelineResult, RouterOutput, ActionResult
)
from apps.depts.agents.router_agent.agent import ROUTER_AGENT
from apps.depts.agents.department_agent import get_department_agent
from apps.depts.models import CitizenRequest
from apps.integrations.twilio_sms.service import TwilioSMSService
from typing import Dict, Any, List

def generate_case_code() -> str:
    """Generate a simple case code"""
    import uuid
    return f"C-{str(uuid.uuid4())[:8].upper()}"

def execute_actions(action_plan, entity, case_code: str) -> List[ActionResult]:
    """Execute the actions in the action plan"""
    results = []

    try:
        # Primary action
        if action_plan.primary_action == "call":
            # Simulate call (in real implementation, use VAPI)
            results.append(ActionResult(
                action="call",
                success=True,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                details={"phone": entity.phone, "script": action_plan.call_script}
            ))

        elif action_plan.primary_action == "sms":
            # Real SMS via Twilio
            try:
                sms_service = TwilioSMSService()
                # For demo, we'll simulate SMS to avoid costs
                results.append(ActionResult(
                    action="sms",
                    success=True,
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    details={"phone": entity.phone, "message": action_plan.sms_body}
                ))
            except Exception as e:
                results.append(ActionResult(
                    action="sms",
                    success=False,
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    error_message=str(e)
                ))

        elif action_plan.primary_action == "email":
            # Simulate email
            results.append(ActionResult(
                action="email",
                success=True,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                details={"subject": action_plan.email_subject, "body": action_plan.email_body}
            ))

    except Exception as e:
        results.append(ActionResult(
            action=action_plan.primary_action,
            success=False,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            error_message=str(e)
        ))

    return results

def create_user_message(department_result, execution_results) -> Dict[str, str]:
    """Create simple user messages in English and Urdu"""

    entity = department_result.assigned_entity
    urgency = department_result.urgency

    if urgency == "critical":
        message_en = f"🚨 EMERGENCY PROCESSED: We have contacted {entity.name} immediately. Help is on the way. Keep your phone available."
        message_ur = f"🚨 ہنگامی صورتحال: ہم نے فوری طور پر {entity.name} سے رابطہ کیا ہے۔ مدد آ رہی ہے۔ اپنا فون ساتھ رکھیں۔"
    elif urgency == "high":
        message_en = f"⚡ HIGH PRIORITY: Your request has been sent to {entity.name}. They will contact you soon."
        message_ur = f"⚡ اعلیٰ ترجیح: آپ کی درخواست {entity.name} کو بھیج دی گئی ہے۔ وہ جلد آپ سے رابطہ کریں گے۔"
    else:
        message_en = f"✅ REQUEST SUBMITTED: Your request has been sent to {entity.name} in {entity.city}."
        message_ur = f"✅ درخواست جمع: آپ کی درخواست {entity.city} میں {entity.name} کو بھیج دی گئی ہے۔"

    return {
        "message_en": message_en,
        "message_ur": message_ur
    }

def process_emergency_request(request_text: str, user_city: str = None) -> PipelineResult:
    """
    MAIN PIPELINE FUNCTION
    This is where the magic happens!
    """
    start_time = time.time()
    case_code = generate_case_code()
    degraded_mode = False

    try:
        print(f"🚀 Processing request: {request_text[:50]}...")

        # STEP 1: Router Agent - Classify the request
        print("🤖 Step 1: Classifying request...")
        try:
            router_input = RouterInput(request_text=request_text, user_city=user_city)
            router_result = ROUTER_AGENT.run(router_input.model_dump())

            # Convert to our schema
            router_output = RouterOutput(
                category=router_result.get("department", "health"),
                confidence=router_result.get("confidence", 0.7),
                rationale=router_result.get("reason", "AI classification"),
                degraded_mode_used=router_result.get("degraded_mode_used", False)
            )

        except Exception as e:
            print(f"❌ Router failed: {e}")
            # DEGRADED MODE - Simple keyword matching
            degraded_mode = True
            if any(word in request_text.lower() for word in ['fire', 'آگ', 'burn']):
                category = "fire_brigade"
            elif any(word in request_text.lower() for word in ['police', 'theft', 'crime', 'پولیس']):
                category = "police"
            elif any(word in request_text.lower() for word in ['health', 'sick', 'pain', 'بیمار', 'درد']):
                category = "health"
            else:
                category = "health"  # Default fallback

            router_output = RouterOutput(
                category=category,
                confidence=0.5,
                rationale="Degraded mode - keyword matching",
                degraded_mode_used=True
            )

        print(f"✅ Classified as: {router_output.category} (confidence: {router_output.confidence:.2f})")

        # STEP 2: Department Agent - Plan actions
        print("🎯 Step 2: Planning actions...")
        department_agent = get_department_agent(router_output.category)

        dept_input = DepartmentAgentInput(
            category=router_output.category,
            request_text=request_text,
            user_location={"city": user_city} if user_city else None,
            confidence=router_output.confidence
        )

        department_result = department_agent(dept_input)
        print(f"✅ Plan created: {department_result.urgency} urgency → {department_result.action_plan.primary_action}")

        # STEP 3: Execute Actions
        print("⚡ Step 3: Executing actions...")
        execution_results = execute_actions(
            department_result.action_plan,
            department_result.assigned_entity,
            case_code
        )
        print(f"✅ Actions executed: {len(execution_results)} actions")

        # STEP 4: Create user message
        print("💬 Step 4: Creating user message...")
        user_message = create_user_message(department_result, execution_results)

        # STEP 5: Save to database
        print("💾 Step 5: Saving to database...")
        try:
            citizen_request = CitizenRequest.objects.create(
                request_text=request_text,
                category=router_output.category,
                urgency_level=department_result.urgency.upper(),
                confidence_score=router_output.confidence,
                ai_response=router_output.rationale,
                degraded_mode_used=degraded_mode
            )
            citizen_request.case_code = case_code
            citizen_request.save()
            print(f"✅ Saved as case: {case_code}")
        except Exception as e:
            print(f"⚠️ Database save failed: {e}")

        # Calculate processing time
        processing_time = time.time() - start_time

        # Return complete result
        result = PipelineResult(
            case_code=case_code,
            success=True,
            router_result=router_output,
            department_result=department_result,
            execution_results=execution_results,
            guidance_result={
                "message_en": user_message["message_en"],
                "message_ur": user_message["message_ur"],
                "next_steps": ["Keep your phone available", "Note down case number", "Contact us if no response"]
            },
            degraded_mode_used=degraded_mode,
            processing_time_seconds=round(processing_time, 2)
        )

        print(f"🎉 Pipeline completed in {processing_time:.2f}s")
        return result

    except Exception as e:
        print(f"💥 Pipeline failed: {e}")
        # Emergency fallback
        return PipelineResult(
            case_code=case_code,
            success=False,
            router_result=RouterOutput(
                category="health",
                confidence=0.0,
                rationale="Emergency fallback due to system error",
                degraded_mode_used=True
            ),
            error_message=str(e),
            degraded_mode_used=True,
            processing_time_seconds=time.time() - start_time
        )

# Quick test function
if __name__ == "__main__":
    # Test the pipeline
    test_request = "My father is having chest pain and difficulty breathing"

    print("🧪 TESTING EMERGENCY PIPELINE")
    print("=" * 50)

    result = process_emergency_request(test_request, "Karachi")

    print("\n📋 FINAL RESULT:")
    print(f"Case Code: {result.case_code}")
    print(f"Success: {result.success}")
    print(f"Category: {result.router_result.category}")
    print(f"Urgency: {result.department_result.urgency if result.department_result else 'N/A'}")
    print(f"Processing Time: {result.processing_time_seconds}s")
    print(f"Degraded Mode: {result.degraded_mode_used}")

    if result.guidance_result:
        print(f"Message (EN): {result.guidance_result['message_en']}")
        print(f"Message (UR): {result.guidance_result['message_ur']}")