import logging
from typing import Optional
from django.db import DatabaseError

from apps.knowledge_manager.models import (
    SessionMemory,
    AIAgentInstanceMemory,
    WorkspaceMemory,
    GlobalMemory,
    UserMemory,
)
from apps.ai_agents.models import AIAgentInstance
from apps.workspaces.models import Workspace
from apps.authentication.models import User

logger = logging.getLogger(__name__)


class MemoryService:
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

    def load_context(self) -> str:
        context_parts = []

        if self.session_id:
            try:
                session_mems = SessionMemory.objects.filter(
                    session_id=self.session_id,
                    ai_agent_instance=self.agent_instance
                )
                for idx, mem in enumerate(session_mems, start=1):
                    context_parts.append(f"[Session #{idx} Context]\n{str(mem.context)}")
                    if mem.last_messages:
                        context_parts.append(f"[Session #{idx} Last Messages]\n" + "\n".join(mem.last_messages))
            except DatabaseError as e:
                logger.error(f"[MemoryService] Failed to load session memory: {e}")

        try:
            user_mem = UserMemory.objects.filter(user=self.user).first()
            if user_mem:
                context_parts.append("[User Preferences]\n" + str(user_mem.preferences))
                context_parts.append("[User Past Interactions]\n" + str(user_mem.past_interactions))
        except DatabaseError as e:
            logger.error(f"[MemoryService] Failed to load user memory: {e}")

        return "\n\n".join(context_parts)

    def load_knowledge(self) -> str:
        knowledge_parts = []

        try:
            ws_mems = WorkspaceMemory.objects.filter(workspace=self.workspace)
            for idx, mem in enumerate(ws_mems, start=1):
                knowledge_parts.append(f"[Workspace Memory #{idx}]\n{str(mem.memory)}")
        except DatabaseError as e:
            logger.error(f"[MemoryService] Failed to load workspace memory: {e}")

        try:
            instance_mems = AIAgentInstanceMemory.objects.filter(ai_agent_instance=self.agent_instance)
            for mem in instance_mems:
                knowledge_parts.append(f"[{mem.memory_type.title()} Memory]\n{str(mem.memory)}")
        except DatabaseError as e:
            logger.error(f"[MemoryService] Failed to load agent instance memory: {e}")

        try:
            global_mems = GlobalMemory.objects.all().order_by("-created_at")[:5]
            for mem in global_mems:
                knowledge_parts.append(f"[Global Memory – {mem.title}]\n{mem.content}")
        except DatabaseError as e:
            logger.error(f"[MemoryService] Failed to load global memory: {e}")

        return "\n\n".join(knowledge_parts)

    def store_context_memory(self, context: dict, last_messages: Optional[list] = None):
        """
        Stores or updates session-level memory after a run.
        """
        if not self.session_id:
            logger.warning("[MemoryService] Cannot store session memory — session_id not provided.")
            return

        try:
            memory_obj, _ = SessionMemory.objects.update_or_create(
                session_id=self.session_id,
                ai_agent_instance=self.agent_instance,
                defaults={
                    "context": context,
                    "last_messages": last_messages or [],
                }
            )
            logger.debug(f"[MemoryService] Updated SessionMemory: {memory_obj.id}")
        except DatabaseError as e:
            logger.error(f"[MemoryService] Failed to store session memory: {e}")

    def store_instance_memory(self, memory_type: str, data: dict):
        """
        Stores or updates long-term memory for the AI Agent Instance.
        """
        try:
            memory_obj, _ = AIAgentInstanceMemory.objects.update_or_create(
                ai_agent_instance=self.agent_instance,
                memory_type=memory_type,
                defaults={"memory": data}
            )
            logger.debug(f"[MemoryService] Updated InstanceMemory: {memory_obj.id}")
        except DatabaseError as e:
            logger.error(f"[MemoryService] Failed to store instance memory: {e}")
