from pydantic import BaseModel, Field
from typing import Optional


class ContextSchema(BaseModel):
    primary_context: Optional[str] = Field(default=None, description="Main context for the agent to operate on.")
    secondary_context: Optional[str] = Field(default=None, description="Additional background or extended context.")

    def format_primary(self) -> str:
        content = (self.primary_context or "").strip()
        return f"<primary context>\n{content or 'None'}\n<primary context/>"

    def format_secondary(self) -> str:
        content = (self.secondary_context or "").strip()
        return f"<secondary context>\n{content or 'None'}\n<secondary context/>"

    def full(self) -> dict:
        return "\n\n".join([
            self.format_primary(),
            self.format_secondary(),
        ]).strip()
