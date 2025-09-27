from rest_framework import generics
from rest_framework.response import Response
from apps.ai_agents.models import AIAgent, AIAgentInstance, Capability
from apps.ai_agents.api.serializers import AIAgentInstanceDetailSerializer, AIAgentSerializer, AIAgentShortSerializer, AIAgentInstanceSerializer, CapabilitySerializer
from rest_framework import generics, status
from apps.core.mixins.workspace_required import WorkspaceRequiredMixin
from django.http import JsonResponse
from rest_framework import filters
from django.views import View
from django.shortcuts import get_object_or_404
from django.db.models import Q

class PingView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "pong"})


# I want to add search functionality to this endpoint
class AIAgentListView(WorkspaceRequiredMixin, generics.ListAPIView):
    """List all AI Agents"""
    queryset = AIAgent.objects.all()
    serializer_class = AIAgentShortSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['workspace'] = self.request.workspace
        context['user'] = self.request.user
        return context


class AIAgentRetrieveView(WorkspaceRequiredMixin, generics.RetrieveAPIView):
    """Retrieve a specific AI Agent by pk or slug"""
    queryset = AIAgent.objects.all()
    serializer_class = AIAgentSerializer
    
    def get_object(self):
        lookup_value = self.kwargs['slug_or_id']
        queryset = self.filter_queryset(self.get_queryset())

        # Handle both UUID (pk) and slug resolution
        return get_object_or_404(
            queryset,
            Q(pk=lookup_value) | Q(slug=lookup_value)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['workspace'] = self.request.workspace
        context['user'] = self.request.user
        return context


class CapabilityListView(WorkspaceRequiredMixin, generics.ListAPIView):
    """List all AI Agent Capabilities"""
    queryset = Capability.objects.all()
    serializer_class = CapabilitySerializer
    



class AIAgentInstanceListCreateView(WorkspaceRequiredMixin, generics.ListCreateAPIView):
    """List all AI Agent Instances in a workspace & create a new one"""
    serializer_class = AIAgentInstanceSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['ai_agent__name']
    
    def get_queryset(self):
        """Filter AI Agent instances by workspace"""
        return AIAgentInstance.objects.filter(
            workspace=self.request.workspace
        ).select_related('ai_agent').order_by('ai_agent__name')
    

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['workspace'] = self.request.workspace
        return context
    

    def create(self, request, *args, **kwargs):
        request.workspace

        """Custom response format for create operation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # DRF automatically sets the "status" and "data" in the response
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AIAgentInstanceRetrieveUpdateDestroyView(WorkspaceRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific AI Agent Instance"""
    serializer_class = AIAgentInstanceDetailSerializer
    
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['workspace'] = self.request.workspace
        context['user'] = self.request.user
        return context
    
    def get_queryset(self):
        """Filter AI Agent instances by workspace"""
        return AIAgentInstance.objects.filter(
            workspace=self.request.workspace
        ).select_related('ai_agent')
    
    def update(self, request, *args, **kwargs):
        """Add success message to update response"""
        response = super().update(request, *args, **kwargs)
        response.data = {
            "detail": "Agent instance updated successfully",
            **response.data
        }
        return response
    
    def destroy(self, request, *args, **kwargs):
        """Custom success message for delete operation"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "Agent instance deleted successfully"})