import asyncio
import logging
from typing import Dict, List, Any, Iterator, Optional, AsyncIterator
from datetime import datetime
from agno.agent import Agent
from agno.models.openai import OpenAIChat

logger = logging.getLogger(__name__)

class AgnoHandler:
    """
    Handles AI interactions using the Agno framework.
    Provides both synchronous and asynchronous interfaces.
    """
    def __init__(self, 
                model_name: str, 
                description: str, 
                instructions: str, 
                tools: Optional[List[str]] = None,
                extra_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Agno AI Agent.
        
        Args:
            model_name: The name of the model to use (e.g., "gpt-4o")
            description: Agent description
            instructions: Detailed instructions for the agent
            tools: List of tool names to enable
            extra_config: Additional configuration parameters
        """
        try:
            # Initialize tools
            agent_tools = []
            
            # Add default ExaTools if enabled
            # if not tools or "exa" in tools:
                # agent_tools.append(ExaTools(start_published_date=today, type="keyword"))
            
            # Add other tools as needed
            # TODO: Implement dynamic tool loading based on the tools parameter
            
            # Initialize agent
            self.agent = Agent(
                model=OpenAIChat(id=model_name),
                tools=agent_tools,
                description=description,
                instructions=instructions,
                markdown=True,
                show_tool_calls=True,
                add_datetime_to_instructions=True,
                **(extra_config or {})
            )
            
            self.initialized = True
            
        except Exception as e:
            logger.exception(f"Failed to initialize Agno agent: {e}")
            self.initialized = False
            self.init_error = str(e)
    
    def run(self, 
           query: str, 
           context: Optional[List[Dict[str, Any]]] = None, 
           stream: bool = True) -> Iterator[str]:
        """
        Runs an AI query and returns an iterator for streaming responses.
        
        Args:
            query: The user's input query
            context: Previous conversation context
            stream: Whether to stream the response
            
        Returns:
            An iterator yielding response chunks
        """
        if not self.initialized:
            raise RuntimeError(f"Agno agent not properly initialized: {getattr(self, 'init_error', 'Unknown error')}")
        
        try:
            return self.agent.run(query, context=context, stream=stream)
        except Exception as e:
            logger.exception(f"Error running Agno agent: {e}")
            def error_iterator():
                yield f"Error processing request: {str(e)}"
            return error_iterator()
    
    async def run_async(self, 
                       query: str, 
                       context: Optional[List[Dict[str, Any]]] = None, 
                       stream: bool = True) -> AsyncIterator[str]:
        """
        Async version of run that doesn't block the event loop.
        
        Args:
            query: The user's input query
            context: Previous conversation context
            stream: Whether to stream the response
            
        Returns:
            An async iterator yielding response chunks
        """
        if not self.initialized:
            raise RuntimeError(f"Agno agent not properly initialized: {getattr(self, 'init_error', 'Unknown error')}")
        
        try:
            # Run in a separate thread to avoid blocking
            result_iterator = await asyncio.to_thread(
                self.agent.run,
                query,
                context=context,
                stream=stream
            )
            
            # Convert the iterator to an async iterator
            for chunk in result_iterator:
                yield chunk
                # Small sleep to allow other tasks to run
                await asyncio.sleep(0)
                
        except Exception as e:
            logger.exception(f"Error in async Agno execution: {e}")
            yield f"Error processing request: {str(e)}"