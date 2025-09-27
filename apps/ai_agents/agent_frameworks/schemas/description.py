from pydantic import BaseModel, Field
from typing import List, Optional


class CapabilityItem(BaseModel):
    name: str
    description: Optional[str] = ""


class TaskItem(BaseModel):
    name: str
    input_fields: List[str] = Field(default_factory=list)


class DescriptionSchema(BaseModel):
    raw_description: str = Field(default_factory="", description="Agent identity and persona for system prompt.")
    capabilities: List[CapabilityItem] = Field(default_factory=list)
    tasks: List[TaskItem] = Field(default_factory=list)

    def format_persona(self) -> str:
        return self.raw_description.strip()

    def format_capabilities(self) -> str:
        if not self.capabilities:
            return "<capabilities>\n- None\n<capabilities/>"
        return "<capabilities>\n" + "\n".join(
            f"- {c.name}: {c.description or 'No description'}" for c in self.capabilities
        ) + "\n<capabilities/>"

    def format_tasks(self) -> str:
        if not self.tasks:
            return "<supported tasks>\n- None\n<supported tasks/>"
        return "<supported tasks>\n" + "\n".join(
            f"- {t.name} (inputs: {', '.join(t.input_fields)})" for t in self.tasks
        ) + "\n<supported tasks/>"

    def full(self) -> str:
        return "\n\n".join([
            self.format_persona(),
            self.format_capabilities(),
            self.format_tasks()
        ]).strip()
