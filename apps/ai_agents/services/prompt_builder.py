from typing import List, Optional


class PromptBuilder:
    """
    Builds structured prompts using modular sections.
    """

    def __init__(
        self,
        role: Optional[str] = None,
        task: Optional[str] = None,
        knowledge: Optional[str] = None,
        context: Optional[str] = None,
        instructions: Optional[List[str]] = None,
    ):
        self.role = role
        self.task = task
        self.knowledge = knowledge
        self.context = context
        self.instructions = instructions or []

    def build(self) -> str:
        """
        Builds the complete prompt string based on available sections.
        """

        prompt_parts = []

        if self.role or self.task:
            prompt_parts.append(self._format_section("system", f"You are an expert {self.role} agent helping with {self.task}.".strip()))

        if self.knowledge:
            prompt_parts.append(self._format_section("knowledge", self.knowledge))

        if self.context:
            prompt_parts.append(self._format_section("context", self.context))

        if self.instructions:
            joined = "\n".join(f"- {i}" for i in self.instructions)
            prompt_parts.append(self._format_section("instruction", joined))

        return "\n\n".join(prompt_parts)

    def _format_section(self, title: str, content: str) -> str:
        return f"[{title}]\n{content.strip()}"
