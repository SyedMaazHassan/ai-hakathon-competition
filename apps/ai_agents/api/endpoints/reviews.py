"""
Review System API Endpoints

This module defines the API endpoints, routes, and constants for the review system.
"""
from rest_framework.routers import DefaultRouter
from apps.ai_agents.api.views.reviews import (
    AgentReviewViewSet,
    TaskExecutionReviewViewSet
)

# Register review endpoints
router = DefaultRouter()
router.register(
    r'agents/(?P<ai_agent_pk>[^/.]+)/reviews',
    AgentReviewViewSet,
    basename='agent-reviews'
)
router.register(
    r'agents/(?P<ai_agent_pk>[^/.]+)/execution-reviews',
    TaskExecutionReviewViewSet,
    basename='execution-reviews'
)

urlpatterns = router.urls