import json
import logging
from typing import Dict, List, Any, Iterator, Optional, AsyncIterator
from apps.ai_agents.models import AIAgentInstance
from apps.ai_agents.ai_frameworks.agno_handler import AgnoHandler
# from apps.ai_agents.ai_frameworks.crewai_handler import CrewAIHandler

logger = logging.getLogger(__name__)

class AIWrapperException(Exception):
    """Custom exception for AIWrapper errors."""
    pass

class AIWrapper:
    """
    Wrapper for AI frameworks (Agno, CrewAI, etc.).
    - Selects the correct AI framework based on agent instance.
    - Provides a unified interface for AI execution.
    - Supports both sync and async execution.
    """

    def __init__(self, agent_instance: AIAgentInstance):
        """
        Initialize AI framework dynamically based on agent instance.
        
        Args:
            agent_instance: The AIAgentInstance to wrap
        """
        self.agent_instance = agent_instance
        self.ai_handler = None

        # Use AI framework stored in AIAgentInstance instead of global settings
        self.framework = getattr(agent_instance, "framework", "agno").lower()

        # Extract agent configuration
        agent_config = self._get_agent_configuration()

        try:
            if self.framework == "agno":
                self.ai_handler = AgnoHandler(**agent_config)
            # elif self.framework == "crewai":
            #     self.ai_handler = CrewAIHandler(**agent_config)
            else:
                raise AIWrapperException(f"Unsupported AI framework: {self.framework}")

        except Exception as e:
            logger.exception(f"Failed to initialize AI handler: {e}")
            raise AIWrapperException(f"Failed to initialize AI handler: {str(e)}")

    def _get_agent_configuration(self) -> Dict[str, Any]:
        """
        Extract configuration from the agent instance.
        
        Returns:
            Dict containing configuration for the AI handler
        """
        agent = self.agent_instance.ai_agent

        # Format instructions
        instructions = agent.instructions
        if isinstance(instructions, dict):
            if self.agent_instance.agent_instance_instructions:
                instructions["custom"] = self.agent_instance.agent_instance_instructions
            formatted_instructions = json.dumps(instructions)
        else:
            formatted_instructions = self.agent_instance.agent_instance_instructions or instructions or ""

        # Combine knowledge
        knowledge = {}
        if hasattr(agent, 'agent_knowledge') and agent.agent_knowledge:
            if isinstance(agent.agent_knowledge, dict):
                knowledge.update(agent.agent_knowledge)
        if hasattr(self.agent_instance, 'agent_instance_knowledge') and self.agent_instance.agent_instance_knowledge:
            if isinstance(self.agent_instance.agent_instance_knowledge, dict):
                knowledge.update(self.agent_instance.agent_instance_knowledge)

        # Extract tool configuration dynamically
        tools = []
        if hasattr(agent, 'tools'):
            try:
                tools = [tool.key for tool in agent.tools.all()]
            except Exception as e:
                logger.warning(f"Failed to load tools: {e}")

        # Prepare extra configuration
        extra_config = {}
        if knowledge:
            extra_config["knowledge"] = knowledge

        return {
            "model_name": agent.model,
            "description": agent.description or agent.display_description or "",
            "instructions": formatted_instructions,
            "tools": tools,
            "extra_config": extra_config
        }

    def run(self, query: str, context: Optional[List[Dict[str, Any]]] = None, stream: bool = True) -> Iterator[str]:
        """
        Runs an AI query and returns an iterator for streaming responses.
        
        Args:
            query: The user's input query
            context: Previous conversation context
            stream: Whether to stream the response
            
        Returns:
            An iterator yielding response chunks
        """
        if not self.ai_handler:
            raise AIWrapperException("AI system not properly initialized.")

        try:
            return self.ai_handler.run(query, context=context, stream=stream)
        except Exception as e:
            logger.exception(f"Error in AI wrapper run: {e}")
            raise AIWrapperException(f"Error processing request: {str(e)}")


    async def run_async(self, query: str, context: Optional[List[Dict[str, Any]]] = None, stream: bool = True) -> AsyncIterator[str]:
        """
        Async version of run that doesn't block the event loop.
        
        Args:
            query: The user's input query
            context: Previous conversation context
            stream: Whether to stream the response
            
        Returns:
            An async iterator yielding response chunks
        """
        if not self.ai_handler:
            raise AIWrapperException(f"AI system not properly initialized.")

        try:
            async for chunk in self.ai_handler.run_async(query, context=context, stream=stream):
                yield chunk
        except Exception as e:
            logger.exception(f"Error in AI wrapper async run: {e}")
            raise AIWrapperException(f"Error processing request: {str(e)}")

    @staticmethod
    def format_chat_history(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format chat history for the AI framework.
        
        Args:
            messages: List of message objects with is_user and content fields
            
        Returns:
            Formatted messages list suitable for AI context
        """
        return [
            {
                "role": "user" if msg.get("is_user", False) else "assistant",
                "content": msg.get("content", "")
            }
            for msg in messages if "content" in msg
        ]