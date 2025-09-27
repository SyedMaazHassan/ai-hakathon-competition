from abc import ABC, abstractmethod
from typing import Any, Dict, Literal, Optional, Iterator

class AgentServiceInterface(ABC):
    """
    Interface for any AI agent execution engine.
    """

    @abstractmethod
    def configure_agent(self, config: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def run(
        self,
        mode: Literal["conversation", "task"],
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def run_stream(
        self,
        mode: Literal["conversation", "task"],
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Any]:
        """
        Streamed version of run(). Returns an iterator over partial responses.
        """
        pass
