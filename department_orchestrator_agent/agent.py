from agno.models.openai import OpenAIChat
from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from pydantic_models.hackathon_agents import (
    OrchestratorPlan, UrgencyLevel, CommunicationMethod,
    BookingType, FollowUpSchedule, RouterDecision
)
import json
import re
from datetime import datetime

db = SqliteDb(db_file="agno.db")

# Department Orchestrator Agent Configuration
DEPARTMENT_ORCHESTRATOR_AGENT = Agent(
    name="Department Orchestrator Agent",
    model=OpenAIChat(
        id="gpt-4o-mini",
        temperature=0.1,
        top_p=0.1
    ),
    db=db,
    role="You are the Department Orchestrator Agent - the central coordinator for Pakistani government emergency services.",
    description="""You receive classified requests and create comprehensive action plans including:
    1. Urgency assessment (LOW/MEDIUM/HIGH/CRITICAL)
    2. Action plan creation with immediate actions
    3. Communication method determination (email/SMS/call)
    4. Follow-up requirements and scheduling
    5. User response generation in appropriate language""",
    instructions=[
        "You must return ONLY valid JSON matching the OrchestratorPlan schema.",
        "Assess urgency based on: CRITICAL (life-threatening), HIGH (serious), MEDIUM (important), LOW (routine)",
        "For CRITICAL/HIGH: use emergency_call or phone_call communication",
        "For MEDIUM/LOW: use email or sms communication",
        "Always include clear user acknowledgment in detected language (Urdu/English)",
        "Set requires_matcher_service=true if need specific entity (hospital, police station)",
        "Set requires_booking=true for appointments or scheduled services",
        "Set requires_follow_up=true for HIGH/CRITICAL cases",
        "Provide realistic timelines and clear next steps for citizens",
        "Confidence score should reflect certainty of plan appropriateness"
    ],
    markdown=True,
    search_knowledge=True,
    add_history_to_context=True,
    output_schema=OrchestratorPlan,
)