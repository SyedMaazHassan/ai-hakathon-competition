from django.urls import path
from apps.ai_agents.api.views import (
    AIAgentListView,
    AIAgentRetrieveView,
    AIAgentInstanceListCreateView,
    AIAgentInstanceRetrieveUpdateDestroyView,
    CapabilityListView,
    PingView,
)



# Core URL views (not using ViewSet for agents yet)
urlpatterns = [
    path("ping/", PingView.as_view(), name="ping"),
    path("agents/", AIAgentListView.as_view(), name="ai-agent-list"),
    path("agents/<str:slug_or_id>/", AIAgentRetrieveView.as_view(), name="ai-agent-detail"),  # Supports both pk and slug
    path("agent-instances/", AIAgentInstanceListCreateView.as_view(), name="ai-agent-instance-list"),
    path("agent-instances/<str:pk>/", AIAgentInstanceRetrieveUpdateDestroyView.as_view(), name="ai-agent-instance-detail"),
    path("capabilities/", CapabilityListView.as_view(), name="ai-agent-capability-list"),
]



