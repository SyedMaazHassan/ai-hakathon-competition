from agno.models.openai import OpenAIChat
from agno.agent import Agent
from .prompt import ROUTER_AGENT_PROMPT
from agno.db.sqlite import SqliteDb
from .pydantic_models import RouterDecision
import json
import re
from agno.team import Team
from agno.agent import Agent
db = SqliteDb(db_file="agno.db")


from apps.depts.agents.department_agent.registry import PromptRegistry
from apps.depts.choices import DepartmentCategoryEnum

def create_department_agent(depart_ment_category: DepartmentCategoryEnum):
    prompt = PromptRegistry.get_prompt(depart_ment_category)
    return Agent(
        name=prompt.name,
        model=OpenAIChat(
            id=prompt.model,
            temperature=0.0,
            top_p=0.1
        ),
        db=db,
        role=prompt.role,
        description=prompt.description,
        instructions=prompt.instructions,
        markdown=True,
        search_knowledge=True,
        add_history_to_context=True
    )
