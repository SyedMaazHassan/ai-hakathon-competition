from pydantic import BaseModel, Field
from typing import List
from apps.ai_agents.constants import GENERAL_AGENT_INSTRUCTIONS

class InstructionsSchema(BaseModel):
    """
    Schema for representing hierarchical instructions with different levels of specificity.
    """
    general: List[str] = Field(
        default_factory=lambda: GENERAL_AGENT_INSTRUCTIONS, 
        description="General instructions applicable to all agents"
    )
    agent_specific: List[str] = Field(default_factory=list, description="Instructions specific to a type of agent")
    agent_instance_specific: List[str] = Field(default_factory=list, description="Instructions specific to a particular agent instance")
    task_specific: List[str] = Field(default_factory=list, description="Instructions specific to a particular task")

    def format_section(self, title: str, items: List[str]) -> str:
        if not items:
            return f"## {title}\n- None"
        bullets = "\n".join(f"- {item}" for item in items)
        return f"## {title}\n{bullets}"

    def full(self) -> str:
        return "\n\n".join([
            self.format_section("General", self.general),
            self.format_section("Agent Specific", self.agent_specific),
            self.format_section("User Agent Instance Specific", self.agent_instance_specific),
            self.format_section("Task Specific", self.task_specific)
        ]).strip()