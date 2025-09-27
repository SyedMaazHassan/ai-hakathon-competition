from django.contrib import admin
from .models import AIAgent, Capability, AIAgentInstance, AgentReview, TaskExecutionReview

@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "model", "role")
    search_fields = ("name", "key", "model")
    list_filter = ("model", "role")

    def get_queryset(self, request):
        return AIAgent.all_objects.get_queryset()

@admin.register(Capability)
class CapabilityAdmin(admin.ModelAdmin):
    list_display = ("name", "ai_agent")
    search_fields = ("name",)
    list_filter = ("ai_agent",)

@admin.register(AIAgentInstance)
class AIAgentInstanceAdmin(admin.ModelAdmin):
    list_display = ("ai_agent", "workspace")
    search_fields = ("ai_agent__name", "workspace__name")
    list_filter = ("workspace",)


# Register AgentReview and TaskExecutionReview
@admin.register(AgentReview)
class AgentReviewAdmin(admin.ModelAdmin):
    list_display = ("ai_agent_instance", "user", "rating", "created_at")

@admin.register(TaskExecutionReview)
class TaskExecutionReviewAdmin(admin.ModelAdmin):
    list_display = ("execution", "user", "rating", "created_at")