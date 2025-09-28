import os
import requests
from vapi import Vapi
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

class EmergencyCallAgent:
    def __init__(self, api_key: str = None, phone_number_id: str = None):
        self.api_key = api_key or os.getenv("VAPI_API_KEY")
        self.phone_number_id = phone_number_id or os.getenv("VAPI_PHONE_NUMBER_ID")
        self.vapi = Vapi(token=self.api_key)
        self.assistant_id = None
        self.structured_output_id = None

    def make_emergency_call(self, phone_number: str, call_reason: str, additional_context: dict = None):
        """
        Make an emergency call to the specified phone number with the given reason.

        Args:
            phone_number (str): The phone number to call (in E.164 format)
            call_reason (str): The reason for the emergency call
            additional_context (dict): Additional context like case details, location, etc.
        """
        try:
            # Create structured output for emergency information
            self._create_emergency_structured_output()

            # Create or get emergency assistant
            print(f"Creating emergency assistant for {additional_context}")
            assistant_id = self._create_emergency_assistant(call_reason, additional_context or {})

            # Make the call
            call = self.vapi.calls.create(
                phone_number_id=self.phone_number_id,
                customer={"number": phone_number},
                assistant_id=assistant_id
            )

            print(f"Emergency call initiated: {call.id} to {phone_number}")
            return {
                "success": True,
                "call_id": call.id,
                "message": f"Emergency call initiated to {phone_number}"
            }

        except Exception as e:
            print(f"Error making emergency call: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _create_emergency_structured_output(self):
        """Create structured output schema for emergency response information."""
        url = "https://api.vapi.ai/structured-output"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "name": "Emergency Response Info",
            "type": "ai",
            "description": "Extract critical emergency response information and dispatch confirmation",
            "schema": {
                "type": "object",
                "properties": {
                    "emergencyType": {
                        "type": "string",
                        "description": "Type of emergency (medical, police, fire, etc.)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Exact location of the emergency"
                    },
                    "personInDanger": {
                        "type": "string",
                        "description": "Name of the person who needs help"
                    },
                    "serviceRequested": {
                        "type": "string",
                        "description": "Specific emergency service requested"
                    },
                    "dispatchConfirmed": {
                        "type": "boolean",
                        "description": "Whether emergency services confirmed dispatch"
                    },
                    "estimatedArrivalTime": {
                        "type": "string",
                        "description": "Estimated time of arrival provided by operator"
                    },
                    "operatorInstructions": {
                        "type": "string",
                        "description": "Any instructions provided by the emergency operator"
                    },
                    "additionalInfoProvided": {
                        "type": "string",
                        "description": "Additional information shared with operator"
                    }
                },
                "required": ["emergencyType", "location", "personInDanger", "serviceRequested"]
            }
        }

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        self.structured_output_id = data["id"]
        print(f"Created emergency structured output: {self.structured_output_id}")
        return self.structured_output_id

    def _create_emergency_assistant(self, call_reason: str, context: dict):
        """Create an emergency response assistant tailored to the specific situation."""

        # Build context-specific prompt
        context_info = self._build_context_prompt(context)

        assistant = self.vapi.assistants.create(
            name=f"Emergency Response Agent",
            first_message=self._get_emergency_greeting(call_reason, context),
            model={
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.3,
                "messages": [{
                    "role": f"system",
                    "content": f"""
                    You are an AI emergency response coordinator for the Citizen Assistance Platform. 
                    This is a CRITICAL emergency situation that requires immediate professional response.

                    EMERGENCY DETAILS:
                    - Case Reference: {context.get('case_code', 'Not provided')}
                    - Emergency Type: {call_reason.upper()} EMERGENCY
                    - Person in Danger: {context.get('reported_by', 'Citizen')}
                    - Location: {context.get('location', 'Location not specified')}
                    - Urgency Level: {context.get('urgency_level', 'HIGH')}
                    - Additional Details: {context.get('additional_notes', 'No additional details')}

                    YOUR PRIMARY MISSION:
                    You are calling emergency services on behalf of {context.get('reported_by', 'a citizen')} who is in immediate danger. 
                    You must clearly communicate that this person needs urgent help and request immediate dispatch of appropriate emergency services.

                    SPECIFIC ACTION REQUIRED BASED ON EMERGENCY TYPE:

                    MEDICAL EMERGENCY:
                    - Clearly state: "I'm calling to request immediate medical assistance for {context.get('reported_by', 'a citizen')} who is experiencing a medical emergency"
                    - Describe the medical situation: "{context.get('additional_notes', 'Medical emergency in progress')}"
                    - Urgently request: "Please dispatch an ambulance and medical team immediately to {context.get('location', 'the specified location')}"
                    - Provide critical medical details from the context

                    POLICE EMERGENCY:
                    - Clearly state: "I'm calling to request immediate police assistance for {context.get('reported_by', 'a citizen')} who is in danger"
                    - Describe the security situation: "{context.get('additional_notes', 'Security emergency in progress')}"
                    - Urgently request: "Please dispatch police units immediately to {context.get('location', 'the specified location')}"
                    - Mention any threats, weapons, or ongoing dangers

                    FIRE EMERGENCY:
                    - Clearly state: "I'm calling to report a fire emergency affecting {context.get('reported_by', 'citizens')}"
                    - Describe the fire situation: "{context.get('additional_notes', 'Fire emergency in progress')}"
                    - Urgently request: "Please dispatch fire services immediately to {context.get('location', 'the specified location')}"
                    - Mention trapped individuals, fire size, hazards

                    GENERAL EMERGENCY:
                    - Clearly state: "I'm calling to request emergency assistance for {context.get('reported_by', 'a citizen')} in distress"
                    - Describe the situation: "{context.get('additional_notes', 'Emergency situation in progress')}"
                    - Urgently request: "Please dispatch appropriate emergency services to {context.get('location', 'the specified location')}"

                    CRITICAL COMMUNICATION PROTOCOL:
                    1. FIRST: Identify yourself as an AI emergency coordinator from Citizen Assistance Platform
                    2. SECOND: Immediately state that you're calling because a specific person is in danger
                    3. THIRD: Clearly request the appropriate emergency service dispatch
                    4. FOURTH: Provide exact location and critical details
                    5. FIFTH: Answer any follow-up questions from the emergency operator

                    ESSENTIAL INFORMATION TO PROVIDE:
                    - "This is an automated emergency call on behalf of {context.get('reported_by', 'a citizen')}"
                    - "The person is at: {context.get('location', 'Unknown location - please check GPS')}"
                    - "Emergency type: {call_reason.upper()} - {context.get('additional_notes', 'Immediate response required')}"
                    - "Urgency level: {context.get('urgency_level', 'HIGH')} - Immediate dispatch needed"

                    RESPONSE GUIDELINES:
                    - Speak with urgency but remain calm and professional
                    - Immediately establish that this is a real emergency, not a test
                    - Repeat critical information if necessary (location, person in danger)
                    - Stay on the line until emergency services confirm they're dispatching help
                    - Provide any additional details the operator requests
                    - If transferred to another department, clearly restate the emergency situation

                    Remember: You are the voice for someone in danger. Your clear, urgent communication can save lives.
                    """
                }]
            },
            voice={
                "provider": "11labs",
                "voiceId": "aPfeouerZvEVukwmLSP0",
                "speed": 1.0,
                "stability": 0.7
            },
            artifact_plan={
                "structuredOutputIds": [self.structured_output_id]
            },
            max_duration_seconds=600,
            background_sound="off"
        )

        self.assistant_id = assistant.id
        print(f"Emergency assistant created: {self.assistant_id}")
        return self.assistant_id

    def _build_context_prompt(self, context: dict) -> str:
        """Build context-specific prompt based on provided emergency context."""
        context_parts = []

        if context.get('case_code'):
            context_parts.append(f"- Case Reference: {context['case_code']}")
        if context.get('emergency_type'):
            context_parts.append(f"- Emergency Type: {context['emergency_type']}")
        if context.get('location'):
            context_parts.append(f"- Reported Location: {context['location']}")
        if context.get('reported_by'):
            context_parts.append(f"- Reported By: {context['reported_by']}")
        if context.get('additional_notes'):
            context_parts.append(f"- Additional Notes: {context['additional_notes']}")
        if context.get('urgency_level'):
            context_parts.append(f"- Urgency Level: {context['urgency_level']}")

        return "\n".join(context_parts) if context_parts else "- No additional context provided"

    def _get_emergency_greeting(self, call_reason: str, context: dict) -> str:
        """Get appropriate emergency greeting that immediately states the emergency."""
        person = context.get('reported_by', 'A citizen')
        location = context.get('location', 'an unspecified location')

        greetings = {
            "medical": f"Emergency! I'm calling to request immediate medical assistance for {person} who is experiencing a medical emergency at {location}. This is urgent.",
            "police": f"Emergency! I'm calling to request immediate police assistance for {person} who is in danger at {location}. This is a security emergency.",
            "fire": f"Emergency! I'm calling to report a fire emergency affecting {person} at {location}. Fire services are needed immediately.",
            "general": f"Emergency! I'm calling to request immediate assistance for {person} in distress at {location}. This is an urgent emergency situation."
        }

        return greetings.get(call_reason.lower(), greetings["general"])

    def get_call_status(self, call_id: str):
        """Get the status of a specific call."""
        try:
            call = self.vapi.calls.get(call_id)
            return {
                "call_id": call.id,
                "status": call.status,
                "started_at": call.started_at,
                "ended_at": call.ended_at,
                "duration": call.duration_seconds
            }
        except Exception as e:
            return {"error": str(e)}

    def get_structured_output(self, call_id: str):
        """Retrieve structured output data from a completed call."""
        try:
            # This would typically involve querying VAPI's API for call artifacts
            # The exact implementation depends on VAPI's specific endpoints
            url = f"https://api.vapi.ai/call/{call_id}/artifacts"
            headers = {"Authorization": f"Bearer {self.api_key}"}

            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"error": "Unable to retrieve structured output"}
        except Exception as e:
            return {"error": str(e)}


# Usage Example:
if __name__ == "__main__":
    # Initialize the emergency call agent
    agent = EmergencyCallAgent()

    # Make an emergency call
    result = agent.make_emergency_call(
        phone_number="+923472533106",
        call_reason="medical",
        additional_context={
            "case_code": "C-A812CD34",
            "emergency_type": "Heart attack emergency",
            "location": "Gulberg III, Lahore",
            "reported_by": "Ahmed Hassan",
            "urgency_level": "CRITICAL",
            "additional_notes": "Patient is conscious but experiencing chest pain"
        }
    )

    if result["success"]:
        print(f"Emergency call initiated successfully: {result['call_id']}")
    else:
        print(f"Failed to initiate call: {result['error']}")