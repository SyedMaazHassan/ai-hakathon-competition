import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

# Now import Django models and your agents
from fastapi import FastAPI
from apps.depts.models import CitizenRequest, Department, DepartmentEntity
from apps.authentication.models import CustomUser

# Import your existing agents
from service import router_agent  # Your existing agent

app = FastAPI(title="Emergency Services AI")

@app.post("/process-request/")
async def process_citizen_request(request_text: str, user_id: int = None, location: dict = None):
    """Main endpoint for processing citizen requests"""
    try:
        # Use your existing router agent
        classification = await router_agent.run(request_text)

        # Create CitizenRequest using Django ORM
        if user_id:
            user = CustomUser.objects.get(id=user_id)
        else:
            user = None

        citizen_request = CitizenRequest.objects.create(
            user=user,
            request_text=request_text,
            category=classification.get('category'),
            urgency_level=classification.get('urgency'),
            confidence_score=classification.get('confidence'),
            ai_response=classification.get('reasoning')
        )

        return {
            "success": True,
            "case_code": citizen_request.case_code,
            "classification": classification,
            "request_id": citizen_request.id
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/")
async def root():
    return {"message": "Emergency Services AI API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)