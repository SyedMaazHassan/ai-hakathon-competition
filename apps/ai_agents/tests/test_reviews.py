from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ai_agents.models import (
    AIAgent,
    AIAgentInstance,
    AgentReview,
    TaskExecutionReview
)
from apps.executions.models import TaskExecution
from apps.ai_agents.api.constants import REVIEW_ORDERING_FIELDS

User = get_user_model()

class ReviewBaseTestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create AI Agent and Instance
        self.ai_agent = AIAgent.objects.create(
            name='Test Agent',
            description='Test Description'
        )
        self.agent_instance = AIAgentInstance.objects.create(
            ai_agent=self.ai_agent,
            name='Test Instance'
        )

        # Create an execution for task review tests
        self.execution = TaskExecution.objects.create(
            ai_agent_instance=self.agent_instance,
            user=self.user,
            status='completed'
        )

class AgentReviewTests(ReviewBaseTestCase):
    def setUp(self):
        super().setUp()
        self.review_data = {
            'rating': 5,
            'headline': 'Great Agent!',
            'review_text': 'This agent is amazing.',
            'ai_agent_instance_id': None  # Will be set in each test
        }
        self.list_url = reverse('agent-reviews-list', kwargs={'ai_agent_pk': self.ai_agent.pk})

    def test_create_review(self):
        """Test creating a new agent review"""
        self.review_data['ai_agent_instance_id'] = self.agent_instance.id
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AgentReview.objects.count(), 1)
        self.assertEqual(response.data['rating'], 5)

    def test_prevent_duplicate_review(self):
        """Test that a user cannot review the same instance twice"""
        self.review_data['ai_agent_instance_id'] = self.agent_instance.id
        
        # First review should succeed
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Second review should fail
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already reviewed', str(response.data))

    def test_invalid_rating(self):
        """Test that invalid ratings are rejected"""
        self.review_data['ai_agent_instance_id'] = self.agent_instance.id
        self.review_data['rating'] = 6  # Invalid rating > 5
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_ordering(self):
        """Test review list ordering"""
        # Create multiple reviews with different users and ratings
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        instance2 = AIAgentInstance.objects.create(
            ai_agent=self.ai_agent,
            name='Test Instance 2'
        )

        AgentReview.objects.create(
            user=self.user,
            ai_agent_instance=self.agent_instance,
            rating=5,
            headline='Great!',
            review_text='Amazing'
        )
        AgentReview.objects.create(
            user=user2,
            ai_agent_instance=instance2,
            rating=3,
            headline='Good',
            review_text='Decent'
        )

        # Test each ordering field
        for order_field in REVIEW_ORDERING_FIELDS:
            response = self.client.get(f'{self.list_url}?ordering={order_field}')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)

    def test_review_stats(self):
        """Test review statistics endpoint"""
        # Create multiple reviews with different ratings
        user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass123')
        instance2 = AIAgentInstance.objects.create(ai_agent=self.ai_agent, name='Test Instance 2')

        reviews = [
            AgentReview(user=self.user, ai_agent_instance=self.agent_instance, rating=5),
            AgentReview(user=user2, ai_agent_instance=instance2, rating=3)
        ]
        AgentReview.objects.bulk_create(reviews)

        stats_url = reverse('agent-reviews-stats', kwargs={'ai_agent_pk': self.ai_agent.pk})
        response = self.client.get(stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_rating'], 4.0)
        self.assertEqual(response.data['total_reviews'], 2)

class TaskExecutionReviewTests(ReviewBaseTestCase):
    def setUp(self):
        super().setUp()
        self.review_data = {
            'rating': 4,
            'short_feedback': 'Good execution',
            'execution_id': None  # Will be set in each test
        }
        self.list_url = reverse('execution-reviews-list', kwargs={'ai_agent_pk': self.ai_agent.pk})

    def test_create_execution_review(self):
        """Test creating a new execution review"""
        self.review_data['execution_id'] = str(self.execution.id)
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskExecutionReview.objects.count(), 1)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['execution']['id'], str(self.execution.id))

    def test_prevent_duplicate_execution_review(self):
        """Test that a user cannot review the same execution twice"""
        self.review_data['execution_id'] = str(self.execution.id)
        
        # First review should succeed
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Second review should fail
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already reviewed', str(response.data))

    def test_invalid_execution_review_rating(self):
        """Test that invalid ratings are rejected for execution reviews"""
        self.review_data['execution_id'] = str(self.execution.id)
        self.review_data['rating'] = 0  # Invalid rating < 1
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_execution_review_ordering(self):
        """Test execution review list ordering"""
        # Create multiple reviews
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        execution2 = TaskExecution.objects.create(
            ai_agent_instance=self.agent_instance,
            user=user2,
            status='completed'
        )

        TaskExecutionReview.objects.create(
            user=self.user,
            execution=self.execution,
            rating=5,
            short_feedback='Excellent'
        )
        TaskExecutionReview.objects.create(
            user=user2,
            execution=execution2,
            rating=3,
            short_feedback='Good'
        )

        # Test each ordering field
        for order_field in REVIEW_ORDERING_FIELDS:
            response = self.client.get(f'{self.list_url}?ordering={order_field}')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)

    def test_invalid_execution_id(self):
        """Test that invalid execution IDs are rejected"""
        self.review_data['execution_id'] = 'non-existent-id'
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Execution does not exist', str(response.data))

    def test_wrong_user_execution(self):
        """Test that users can't review other users' executions"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        execution2 = TaskExecution.objects.create(
            ai_agent_instance=self.agent_instance,
            user=user2,
            status='completed'
        )
        
        self.review_data['execution_id'] = str(execution2.id)
        response = self.client.post(self.list_url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not allowed to review', str(response.data)) 