from typing import Type
from .base_agent import BaseAgent
from .agno_agent import AgnoAgent
from apps.knowledge_manager.services.vector_store_service import LlamaIndexVectorStoreService
# from .langgraph_agent import LangGraphAgent
# from .crew_agent import CrewAgent
from typing import Literal
from apps.workflows.models import TaskOutputSchema

class AgentsUpAgent:
    """
    Public interface for all agents in the system.
    Loads the appropriate agent runtime based on framework and delegates methods to it.
    """
    ALLOWED_MODES = ["conversational", "task"]
    AGENT_MAP: dict[str, Type[BaseAgent]] = {
        "agno": AgnoAgent,
        # "langgraph": LangGraphAgent,
        # "crew": CrewAgent,
    }

    def __init__(
            self, 
            ai_agent_instance,
            user_id: str = None,
            workspace_id: str = None,
            session_id: str = None,
             
            primary_context:dict={}, 
            *,
            framework: str = "agno",
            mode: Literal["conversational", "task"] = "conversational",
            is_structured: bool = False,
            task = None
        ):
        framework = framework.lower()
        agent_class = self.AGENT_MAP.get(framework)

        if not agent_class:
            raise ValueError(
                f"Unsupported framework: '{framework}'. Supported: {', '.join(self.AGENT_MAP.keys())}"
            )
        
        if mode not in self.ALLOWED_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Allowed values are: {self.ALLOWED_MODES}")

        if mode == "task" and not task:
            raise ValueError("Task is required when mode is 'task'")


        self.mode = mode
        self.task = task
        self.is_structured = is_structured
        
        self.response_model = task.get_outputs if task else None
        if not is_structured and self.response_model:
            self.response_model = TaskOutputSchema.convert_pydantic_to_string(self.response_model)

        self.agent: BaseAgent = agent_class(
            ai_agent_instance, 
            mode=mode, 
            task=task, 
            response_model=self.response_model,
            is_structured=is_structured
        )


    def get_context_base(
        self,
        workspace_id: str,
        user_id: str,
        agent_instance_id: str,
        session_id: str = None,
        top_k: int = 8
    ):
        vector_service = LlamaIndexVectorStoreService()
        context_base = vector_service.get_query_engine_with_scope_filter(
            workspace_id=workspace_id,
            user_id=user_id,
            agent_instance_id=agent_instance_id,
            session_id=session_id,
            top_k=top_k
        )
        return context_base

    def resolve_context(self,
        prompt: str,
        context_base,
        min_score=0.74
    ):
        nodes = context_base.retrieve(prompt)
        filtered_nodes = [n for n in nodes if n.score and n.score > min_score]  # You can tune this threshold
        context_str = "\n\n".join([node.get_content() for node in filtered_nodes])
        upgraded_prompt = self.upgrade_prompt(prompt, context=context_str)
        return upgraded_prompt

    def upgrade_prompt(self, prompt: str, context: str=None) -> str:
        updated_prompt = f'{prompt}\n\n<Useful Context Information>\n{context}\n</Useful Context Information>'''
        return updated_prompt

    def run(self, prompt: str, context: str=None) -> dict:
        return self.agent.run(prompt, context=context)

    def run_stream(self, prompt: str, context: str=None):
        return self.agent.run_stream(prompt, context=context)

    def get_agent_object(self):
        return self.agent
    
    def __str__(self):
        return str(self.agent)
