from django.urls import path
from . import views

app_name = 'ai_agents'

urlpatterns = [
    path('', views.agent_list, name='agent_list'),
    path('agent/<str:pk>/', views.agent_detail, name='agent_detail'),
    # If using class-based view: 
    # path('', views.AgentListView.as_view(), name='agent_list'),
]