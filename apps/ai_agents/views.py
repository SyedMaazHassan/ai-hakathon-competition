from django.shortcuts import render, get_object_or_404
from apps.ai_agents.models import AIAgent

def agent_list(request):
    """
    Simple view to list all AI agents
    """
    agents = AIAgent.objects.all().prefetch_related('capabilities')
    return render(request, 'ai_agents/agent_list.html', {'agents': agents})

def agent_detail(request, pk):
    """
    Detailed view for a specific AI agent showing all information
    """
    agent = get_object_or_404(
        AIAgent.objects.prefetch_related(
            'capabilities',
            'tasks__task_inputs',
            'tasks__output_schema__fields',
            'tools',
            'instances__workspace'
        ).select_related(),
        pk=pk
    )
    
    context = {
        'agent': agent,
    }
    
    return render(request, 'ai_agents/agent_detail.html', context)