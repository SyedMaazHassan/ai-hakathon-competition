"""
Review-related views for the AI Agents API.
"""
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from apps.core.mixins.workspace_required import WorkspaceRequiredMixin
from apps.ai_agents.models import AgentReview, TaskExecutionReview, AIAgent
from apps.ai_agents.api.serializers import (
    AgentReviewSerializer,
    TaskExecutionReviewSerializer,
    AgentReviewStatsSerializer
)
from apps.ai_agents.api.constants import REVIEW_ORDERING_FIELDS


class AgentReviewViewSet(
    WorkspaceRequiredMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet for managing AI Agent reviews.
    
    list:
        Get all reviews for an AI Agent
    create:
        Create a new review for an AI Agent instance
    retrieve:
        Get a specific review
    stats:
        Get review statistics for an AI Agent
    """
    serializer_class = AgentReviewSerializer
    
    filter_backends = [OrderingFilter]
    ordering_fields = REVIEW_ORDERING_FIELDS
    ordering = ['-created_at']  # Default ordering

    # send context to serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['ai_agent_id'] = self.kwargs['ai_agent_pk']
        return context

    def get_queryset(self):
        return AgentReview.objects.filter(
            ai_agent_instance__ai_agent_id=self.kwargs['ai_agent_pk']
        ).select_related(
            'user',
            'ai_agent_instance',
            'ai_agent_instance__ai_agent'
        )

    def perform_create(self, serializer):
        # Validate that ai_agent_instance belongs to the correct ai_agent
        ai_agent_instance_id = serializer.validated_data['ai_agent_instance_id']
            
        # Check if user has already reviewed this instance
        if AgentReview.objects.filter(
            ai_agent_instance_id=ai_agent_instance_id,
            user=self.request.user
        ).exists():
            raise serializers.ValidationError({
                'non_field_errors': ['You have already reviewed this agent instance']
            })
            
        serializer.save()

    @action(detail=False, methods=['get'])
    def stats(self, request, ai_agent_pk=None):
        """Get aggregated review statistics for an AI Agent"""
        try:
            ai_agent = AIAgent.objects.get(pk=ai_agent_pk)
        except AIAgent.DoesNotExist:
            return Response(
                {'detail': 'AI Agent not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AgentReviewStatsSerializer(ai_agent)
        return Response(serializer.data)


class TaskExecutionReviewViewSet(
    WorkspaceRequiredMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet for managing task execution reviews.
    
    list:
        Get all execution reviews for an AI Agent
    create:
        Create a new execution review
    retrieve:
        Get a specific execution review
    """
    serializer_class = TaskExecutionReviewSerializer
    
    filter_backends = [OrderingFilter]
    ordering_fields = REVIEW_ORDERING_FIELDS
    ordering = ['-created_at']  # Default ordering

    # send context to serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        return TaskExecutionReview.objects.filter(
            execution__ai_agent_instance__ai_agent_id=self.kwargs['ai_agent_pk']
        ).select_related(
            'user',
            'execution',
            'execution__ai_agent_instance'
        )

    def perform_create(self, serializer):
        # Check if user has already reviewed this execution
        execution_id = serializer.validated_data.get('execution_id')

        if TaskExecutionReview.objects.filter(
            execution_id=execution_id,
            user=self.request.user
        ).exists():
            raise serializers.ValidationError({
                'non_field_errors': ['You have already reviewed this execution']
            })
            
        serializer.save() 