from typing import Dict, Any, Type
from .base import AgentServiceInterface
from .agno_service import AgnoAgentService

# Future integrations
# from .langgraph_service import LangGraphAgentService
# from .langchain_service import LangChainAgentService


class AgentServiceFactory:
    """
    Class-based factory for agent services. Initializes with config
    and automatically loads the correct agent service implementation.
    """

    FRAMEWORK_MAP: Dict[str, Type[AgentServiceInterface]] = {
        "agno": AgnoAgentService,
        # "langgraph": LangGraphAgentService,
        # "langchain": LangChainAgentService,
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.framework = config.get("framework", "agno").lower()

        service_class = self.FRAMEWORK_MAP.get(self.framework)
        if not service_class:
            raise ValueError(
                f"Unsupported agent framework: '{self.framework}'. "
                f"Supported frameworks: {', '.join(self.FRAMEWORK_MAP.keys())}"
            )

        self.service: AgentServiceInterface = service_class()

    def configure_agent(self) -> None:
        self.service.configure_agent(self.config)

    def run(self, *args, **kwargs):
        return self.service.run(*args, **kwargs)

    def run_stream(self, *args, **kwargs):
        return self.service.run_stream(*args, **kwargs)
