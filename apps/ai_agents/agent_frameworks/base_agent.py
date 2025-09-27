from abc import ABC, abstractmethod
from typing import Any, Iterator
from .schemas.instructions import InstructionsSchema
from .schemas.description import DescriptionSchema
from apps.knowledge_manager.services.knowledge_retrieval_service import AgentsUpKnowledgeBase

class BaseAgent(ABC):
    """
    Base class for all AI AgentUp wrappers (Agno, Crew, LangGraph, etc).
    Handles shared config parsing from AIAgentInstance.
    """

    def __str__(self):
        information = f'''
        Name: {self.name}
        Role: {self.role}
        Instance: {self.ai_agent_instance}
        '''.strip()
        return information

    def __init__(self, ai_agent_instance, *, mode="conversational", task=None, response_model=None, is_structured=False):
        self.ai_agent_instance = ai_agent_instance
        self.mode = mode
        self.task = task
        self.response_model = response_model
        self.is_structured = is_structured

        self.name = None
        self.role = None
        self.model = None
        self.description = None
        self.knowledge_base = None
        self.agent_knowledge = None
        self.agent_instance_knowledge = None
        self.agent = None
        self.instructions = None
        self.capabilities = []
        self.tasks = []
        self.context = {}
        self.set_capabilities()
        self.set_tasks()
        self.set_agent_config() 
        self.set_knowledge()
        self.set_context()
        self.set_framework_agent()

    def set_context(self, additional_context: dict = None):
        from apps.executions.models import TaskExecution
        ai_agent_instance = self.ai_agent_instance
        workspace = ai_agent_instance.workspace
        # get latest 3 executions inputs
        latest_executions = TaskExecution.objects.filter(
            workspace=workspace,
            ai_agent_instance=ai_agent_instance
        ).order_by('-started_at')[:3]
        inputs = [execution.inputs for execution in latest_executions]
        self.context['past_inputs'] = inputs
        if additional_context:
            self.context['additional_context'] = additional_context

    def set_knowledge(self):
        workspace_id = self.ai_agent_instance.workspace.id
        knowledge_base = AgentsUpKnowledgeBase(
            workspace_id=workspace_id,
            ai_agent_id=self.ai_agent_instance.ai_agent.id,
            agent_instance_id=self.ai_agent_instance.id 
        )
        self.knowledge_base = knowledge_base

    def set_capabilities(self):
        capabilities = self.ai_agent_instance.ai_agent.get_capabilities()
        self.capabilities = [cap.to_pydantic() for cap in capabilities]

    def set_tasks(self):
        tasks = self.ai_agent_instance.ai_agent.get_tasks()
        self.tasks = [task.to_pydantic() for task in tasks]

    def set_agent_config(self):
        agent = self.ai_agent_instance.ai_agent

        # Agent specific details
        self.name = agent.name
        self.role = agent.role
        self.model = agent.model
        self.description = agent.description
        self.agent_knowledge = agent.agent_knowledge

        # Agent Instance specific 
        self.agent_instance_knowledge = self.ai_agent_instance.agent_instance_knowledge
        task_instructions = self.task.task_instructions if self.task else []
        self.instructions = InstructionsSchema(
            agent_specific = agent.agent_instructions,
            agent_instance_specific = self.ai_agent_instance.agent_instance_instructions,
            task_specific = task_instructions
        )
        self.description = DescriptionSchema(
            raw_description=self.ai_agent_instance.ai_agent.description or "",
            capabilities=self.capabilities,
            tasks=self.tasks
        )


    def get_config(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "model": self.model,
            "description": self.description.dict(),
            "instructions": self.instructions.dict(),
            "context": self.context,
            "agent_knowledge": self.agent_knowledge,
            "agent_instance_knowledge": self.agent_instance_knowledge,
            "capabilities": self.capabilities,
            "tasks": self.tasks
        }

    @abstractmethod
    def set_framework_agent(self):
        pass

    @abstractmethod
    def get_model(self, model_id: str) -> Any:
        pass

    @abstractmethod
    def run(self, prompt: str, context: str=None) -> dict:
        pass

    @abstractmethod
    def run_stream(self, prompt: str, context: str=None) -> Iterator[Any]:
        pass
