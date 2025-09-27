import logging
from typing import Any, Dict, Literal, Optional, Iterator

from .base import AgentServiceInterface
from agno.agent import Agent as AgnoAgent, RunResponse
from agno.models.openai import OpenAIChat

logger = logging.getLogger(__name__)

class AgnoAgentService(AgentServiceInterface):
    """
    Agent runner using Agno framework.
    """

    def __init__(self):
        self.agent = None
        self.config = {}

    def configure_agent(self, config: Dict[str, Any]) -> None:
        self.config = config

        model_id = config.get("model", "gpt-3.5-turbo")
        model = OpenAIChat(id=model_id)

        self.agent = AgnoAgent(
            model=model,
            name=config.get("name"),
            role=config.get("role", "assistant"),
            instructions=config.get("instructions", []),
            description=config.get("description", ""),
            tools=config.get("tools", []),
            context=config.get("context", {}),
            memory=config.get("memory"),
            session_id=config.get("session_id"),
            user_id=config.get("user_id"),
            user_data=config.get("user_data", {}),
            session_state=config.get("session_state", {}),
            add_context=True,
        )

    def run(
        self,
        mode: Literal["conversation", "task"],
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the agent in non-streaming mode.

        Returns:
            {
                "output": str,
                "metadata": dict,
                "tokens_used": dict,
                "error": Optional[str]
            }
        """
        if not self.agent:
            raise ValueError("Agent not configured. Call configure_agent() first.")

        prompt = input_data.get("prompt") or input_data.get("message") or ""

        try:
            run_response: RunResponse = self.agent.run(prompt)
            output = run_response.message.content if run_response.message else ""

            return {
                "output": output,
                "metadata": getattr(run_response, "metadata", {}),
                "tokens_used": getattr(run_response, "usage", {}),
                "error": None,
            }

        except Exception as e:
            logger.exception(f"[AgnoAgentService] Failed to run agent: {str(e)}")
            return {
                "output": "",
                "metadata": {},
                "tokens_used": {},
                "error": str(e),
            }

    def run_stream(
        self,
        mode: Literal["conversation", "task"],
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Iterator[RunResponse]:
        """
        Executes the agent in streaming mode.
        Returns a generator that yields RunResponse chunks.
        """
        if not self.agent:
            raise ValueError("Agent not configured. Call configure_agent() first.")

        prompt = input_data.get("prompt") or input_data.get("message") or ""

        try:
            return self.agent.run(prompt, stream=True)
        except Exception as e:
            logger.exception(f"[AgnoAgentService] Streaming error: {str(e)}")

            def error_stream():
                yield RunResponse(message=None, metadata={}, error=str(e))

            return error_stream()
