from typing import Literal, Dict, Any, Optional
from .factory import AgentServiceFactory
from .prompt_builder import PromptBuilder
from .memory_service import MemoryService

from apps.ai_agents.models import AIAgentInstance
from apps.workspaces.models import Workspace
from apps.authentication.models import CustomUser as User

class AIAgentExecutor:
    """
    Executes an AI AgentInstance by orchestrating memory, prompt building, and agent execution.
    """

    def __init__(
        self,
        workspace: Workspace,
        user: User,
        agent_instance: AIAgentInstance,
        session_id: Optional[str] = None,
    ):
        self.workspace = workspace
        self.user = user
        self.agent_instance = agent_instance
        self.session_id = session_id

    def execute(
        self,
        mode: Literal["task", "conversation"],
        task_description: Optional[str],
        input_data: Dict[str, Any],
        stream: bool = False,
    ) -> Any:
        """
        Handles full agent execution flow.
        """
        agent = self.agent_instance.ai_agent

        # Load memory context and knowledge
        memory_service = MemoryService(
            workspace=self.workspace,
            user=self.user,
            agent_instance=self.agent_instance,
            session_id=self.session_id
        )
        context = memory_service.load_context()
        knowledge = memory_service.load_knowledge()

        # Build prompt
        builder = PromptBuilder(
            role=agent.role,
            task=task_description,
            context=context,
            knowledge=knowledge,
            instructions=agent.instructions
        )
        prompt = builder.build()

        # Prepare agent service
        config = {
            "framework": "agno",
            "model": agent.model,
            "name": agent.name,
            "role": agent.role,
            "description": agent.description,
            "instructions": agent.instructions,
            "tools": list(agent.tools.all()),  # Optional: serialize or map
            "context": {},
            "memory": None,
            "user_id": str(self.user.id),
            "session_id": self.session_id,
            "session_state": {},  # Expand later
        }

        service = AgentServiceFactory(config)
        service.configure_agent()

        if stream:
            return service.run_stream(mode=mode, input_data={"prompt": prompt})

        result = service.run(mode=mode, input_data={"prompt": prompt})

        # Store memory post-run
        if not result.get("error"):
            memory_service.store_context_memory(
                context={"input": input_data},
                last_messages=[prompt, result["output"]]
            )
            memory_service.store_instance_memory(
                memory_type="long-term",
                data={"last_output": result["output"]}
            )

        return result
