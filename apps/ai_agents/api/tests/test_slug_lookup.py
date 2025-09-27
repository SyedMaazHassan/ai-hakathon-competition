from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.ai_agents.models import AIAgent
from apps.workspaces.models import Workspace

User = get_user_model()


class AIAgentSlugLookupTestCase(APITestCase):
    """Test cases for AI Agent slug lookup functionality"""
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create a test workspace
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            created_by=self.user
        )
        
        # Create a test AI Agent
        self.agent = AIAgent.objects.create(
            name='Test AI Agent',
            slug='test-ai-agent',
            key='test-agent-key',
            display_tagline='A test agent',
            display_description='This is a test AI agent',
            model='gpt-4'
        )
        
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
        
        # Set workspace in session (simulate WorkspaceRequiredMixin)
        session = self.client.session
        session['workspace_id'] = self.workspace.id
        session.save()
    
    def test_retrieve_agent_by_pk(self):
        """Test retrieving AI Agent by primary key (ID)"""
        url = reverse('ai-agent-detail', kwargs={'pk': str(self.agent.pk)})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.agent.id)
        self.assertEqual(response.data['slug'], self.agent.slug)
        self.assertEqual(response.data['name'], self.agent.name)
    
    def test_retrieve_agent_by_slug(self):
        """Test retrieving AI Agent by slug"""
        url = reverse('ai-agent-detail', kwargs={'pk': self.agent.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.agent.id)
        self.assertEqual(response.data['slug'], self.agent.slug)
        self.assertEqual(response.data['name'], self.agent.name)
    
    def test_retrieve_nonexistent_agent(self):
        """Test retrieving non-existent AI Agent returns 404"""
        url = reverse('ai-agent-detail', kwargs={'pk': 'nonexistent-slug'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_slug_field_in_response(self):
        """Test that slug field is included in all relevant serializers"""
        # Test list view
        list_url = reverse('ai-agent-list')
        list_response = self.client.get(list_url)
        
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        if list_response.data['results']:
            self.assertIn('slug', list_response.data['results'][0])
        
        # Test detail view
        detail_url = reverse('ai-agent-detail', kwargs={'pk': str(self.agent.pk)})
        detail_response = self.client.get(detail_url)
        
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertIn('slug', detail_response.data)
        self.assertEqual(detail_response.data['slug'], self.agent.slug)