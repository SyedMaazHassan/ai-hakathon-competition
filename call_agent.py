import os
import requests
from vapi import Vapi


class CallAgent:
    def __init__(self, api_key: str, phone_number_id: str, assistant_id: str = None):
        self.vapi = Vapi(token=api_key)
        self.api_key = api_key
        self.phone_number_id = phone_number_id
        self.assistant_id = assistant_id
        self.structured_output_id = None

    def create_structured_output(self) -> str:
        """Create a structured output schema for customer info using HTTP request (like cURL)."""
        url = "https://api.vapi.ai/structured-output"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "name": "Customer Info",
            "type": "ai",
            "description": "Extract customer contact information",
            "schema": {
                "type": "object",
                "properties": {
                    "firstName": {
                        "type": "string",
                        "description": "Customer's first name"
                    },
                    "lastName": {
                        "type": "string",
                        "description": "Customer's last name"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Customer's email address"
                    },
                    "phone": {
                        "type": "string",
                        "pattern": "^\\+?[1-9]\\d{1,14}$",
                        "description": "Phone number in E.164 format"
                    }
                },
                "required": ["firstName", "lastName"]
            }
        }

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        self.structured_output_id = data["id"]
        print(f"Created structured output: {self.structured_output_id}")
        return self.structured_output_id

    def create_assistant(self, name: str, first_message: str) -> str:
        """Create a new Distack Solutions assistant and store its ID."""
        if not self.structured_output_id:
            raise ValueError("Structured output must be created before assistant.")

        assistant = self.vapi.assistants.create(
            name=name,
            first_message=first_message,
            model={
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
                "messages": [{
                    "role": "system",
                    "content": (
                        "You are a professional AI voice assistant representing Distack Solutions "
                        "(https://distack-solutions.com/). "
                        "At the beginning of each call, warmly greet the customer and politely collect their contact "
                            "You are a professional AI voice assistant representing Distack Solutions. "
                            "Always greet customers warmly. Detect the customer’s spoken language automatically "
                            "(English, Urdu, Arabic, Spanish, etc.) and respond in the same language. "
                            "When collecting contact details (first name, last name, email, phone), ask questions "
                            "in the customer’s language. Ensure structured output always contains English field keys, "
                            "but values should be in the language provided by the customer. "
                            "After collecting details, continue explaining Distack Solutions’ IT services clearly, "
                            "adapted to the customer’s language. "
                        "Ensure these details are captured accurately in the structured output. "
                        "After collecting the details, continue the conversation as a trusted IT partner specializing in "
                        "Generative AI, custom web and mobile apps, cybersecurity, cloud computing, and consulting services. "
                        "Emphasize values: innovation, transparency, customer-driven solutions, and maximizing returns. "
                        "Mention that we have completed 275+ projects with 99% client satisfaction. "
                        "When asked about pricing, never give numbers. Instead politely say: "
                        "'For pricing details, please call us at +92-347-2533106 or email contact@distack-solutions.com'. "
                        "Keep all responses concise, under 40 words, professional, and helpful."
                    )
                }]
            },
            voice={
                "provider": "11labs",
                "voiceId": "aPfeouerZvEVukwmLSP0"
            },
            artifact_plan={
                "structuredOutputIds": [self.structured_output_id]
            }
        )
        self.assistant_id = assistant.id
        print(f"Assistant created: {self.assistant_id}")
        return self.assistant_id

    def make_call(self, customer_number: str):
        """Start an outbound call to the customer."""
        if not self.assistant_id:
            raise ValueError("Assistant ID not set. Create an assistant first.")

        call = self.vapi.calls.create(
            phone_number_id=self.phone_number_id,
            customer={"number": customer_number},
            assistant_id=self.assistant_id
        )
        print(f"Call created: {call.id}")
        return call


if __name__ == "__main__":
    agent = CallAgent(
        api_key=os.getenv("VAPI_API_KEY", "31b2c18d-d8c6-4750-a871-eb6b76e059c6"),
        phone_number_id=os.getenv("VAPI_PHONE_NUMBER_ID", "0b99a20e-1109-4ef3-9c61-ab3aca4fd5c5")
    )

    # Step 1: Create structured output (required first)
    structured_output_id = agent.create_structured_output()

    # Step 2: Create assistant (links to structured output)
    assistant_id = agent.create_assistant(
        name="Distack Solutions Agent",
        first_message="Hi! This is Distack Solutions, your trusted IT partner. How can I assist you today?"
    )

    # Step 3: Make a test call
    agent.make_call("+14155552671")
