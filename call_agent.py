import os
import requests
from vapi import Vapi


class EmergencyCallAgent:
    def __init__(self, api_key: str = None, phone_number_id: str = None):
        self.api_key = api_key or os.getenv("VAPI_API_KEY", "31b2c18d-d8c6-4750-a871-eb6b76e059c6")
        self.phone_number_id = phone_number_id or os.getenv("VAPI_PHONE_NUMBER_ID",
                                                            "0b99a20e-1109-4ef3-9c61-ab3aca4fd5c5")
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
            "description": "Extract critical emergency response information",
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
                    "situationStatus": {
                        "type": "string",
                        "description": "Current status of the situation"
                    },
                    "numberOfPeople": {
                        "type": "integer",
                        "description": "Number of people involved"
                    },
                    "urgencyLevel": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                        "description": "Urgency level of the emergency"
                    },
                    "callerName": {
                        "type": "string",
                        "description": "Name of the person calling"
                    },
                    "callerStatus": {
                        "type": "string",
                        "description": "Caller's condition (safe, injured, etc.)"
                    }
                },
                "required": ["emergencyType", "location", "urgencyLevel"]
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
            name=f"Emergency Response Agent - {call_reason}",
            first_message=self._get_emergency_greeting(call_reason),
            model={
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.3,  # Lower temperature for more consistent emergency responses
                "messages": [{
                    "role": "system",
                    "content": f"""
                    You are an AI emergency response coordinator for the Citizen Assistance Platform. 
                    This is a CRITICAL emergency situation that requires immediate professional response.

                    CALL CONTEXT:
                    - Reason for call: {call_reason}
                    {context_info}

                    YOUR ROLE AND INSTRUCTIONS:
                    1. IMMEDIATELY identify the language of the responder and respond in the same language
                    2. Clearly state that this is an emergency call from the Citizen Assistance Platform
                    3. Collect essential information in this order:
                       - Exact location and address
                       - Type of emergency (medical, police, fire, other)
                       - Number of people involved and their condition
                       - Immediate dangers or hazards present
                       - Any specific assistance already provided or needed

                    4. Speak calmly but with urgency - your tone should be professional and reassuring
                    5. For medical emergencies: Ask about injuries, medical conditions, consciousness
                    6. For police emergencies: Ask about safety, weapons, suspects, ongoing threats
                    7. For fire emergencies: Ask about fire size, trapped people, hazardous materials
                    8. If the responder seems confused, clarify this is a REAL emergency response call
                    9. Document all information accurately in the structured output
                    10. Once critical information is collected, inform them help is being dispatched
                    11. Provide emergency instructions if needed (CPR, safety measures, etc.)
                    12. Stay on the line until professional responders confirm they have taken over

                    CRITICAL RULES:
                    - Never panic or raise your voice
                    - Always verify information for accuracy
                    - If language barriers exist, use simple clear phrases
                    - Prioritize life-threatening information first
                    - Keep responses concise but comprehensive
                    - Confirm understanding with the responder

                    Remember: Lives may be at stake. Your calm, professional coordination is essential.
                    """
                }]
            },
            voice={
                "provider": "11labs",
                "voiceId": "aPfeouerZvEVukwmLSP0",
                "speed": 1.0,  # Normal speed for clarity
                "stability": 0.7  # Balanced stability for emergency tone
            },
            artifact_plan={
                "structuredOutputIds": [self.structured_output_id]
            },
            max_duration_seconds=600,  # 10 minute maximum for emergency calls
            background_sound="off"  # No background sound for clarity
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

    def _get_emergency_greeting(self, call_reason: str) -> str:
        """Get appropriate emergency greeting based on call reason."""
        greetings = {
            "medical": "Emergency medical response call. This is an urgent medical emergency alert. Please respond immediately.",
            "police": "Emergency police dispatch call. This is a critical security emergency alert. Please respond immediately.",
            "fire": "Emergency fire response call. This is a urgent fire emergency alert. Please respond immediately.",
            "general": "Emergency response call. This is a critical emergency alert from the Citizen Assistance Platform. Please respond immediately."
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
        phone_number="+14155552671",
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