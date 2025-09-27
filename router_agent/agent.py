from agno.models.openai import OpenAIChat
from agno.agent import Agent
from .prompt import ROUTER_AGENT_PROMPT
from agno.db.sqlite import SqliteDb
from .pydantic_models import RouterDecision
import json
import re

db = SqliteDb(db_file="agno.db")
ROUTER_AGENT = Agent(
    name=ROUTER_AGENT_PROMPT.name,
    model=OpenAIChat(
        id=ROUTER_AGENT_PROMPT.model,
        temperature=0.0,
        top_p=0.1
    ),
    db=db,
    role=ROUTER_AGENT_PROMPT.role,
    description=ROUTER_AGENT_PROMPT.description,
    instructions=ROUTER_AGENT_PROMPT.instructions,
    markdown=True,
    search_knowledge=True,
    add_history_to_context=True,
    output_schema=RouterDecision,
)