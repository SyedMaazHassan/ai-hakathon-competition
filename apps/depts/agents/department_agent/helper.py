from pydantic import BaseModel, Field
from typing import List


class PromptTemplate(BaseModel):
    """Template for defining AI prompts with structured instructions"""
    
    name: str = Field(..., description="Name/identifier for this prompt template")
    description: str = Field(..., description="Description of what this prompt does")
    model: str = Field(..., description="AI model to use (e.g., 'gpt-4', 'claude-3')")
    instructions: List[str] = Field(default_factory=list, description="List of instruction steps")
    role: str = Field(..., description="System role for the AI (e.g., 'assistant', 'expert')")
