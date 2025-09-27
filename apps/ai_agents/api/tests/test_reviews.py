from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.ai_agents.models import (
    AIAgent,
    AIAgentInstance,
    AgentReview,
    TaskExecutionReview
)
from apps.executions.models import TaskExecution

User = get_user_model()


class ReviewAPITestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # Create AI Agent and instance
        self.ai_agent = AIAgent.objects.create(
            name='Test Agent',
            description='Test Description'
        )
        self.agent_instance = AIAgentInstance.objects.create(
            ai_agent=self.ai_agent,
            user=self.user
        )

        # Create task execution
        self.task_execution = TaskExecution.objects.create(
            ai_agent_instance=self.agent_instance,
            user=self.user,
            task_input='Test input'
        )

    def test_create_agent_review(self):
        """Test creating a new agent review"""
        url = reverse('agent-reviews', kwargs={'ai_agent_pk': self.ai_agent.pk})
        data = {
            'ai_agent_instance_id': str(self.agent_instance.id),
            'rating': 5,
            'headline': 'Great agent!',
            'review_text': 'This agent is amazing!'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AgentReview.objects.count(), 1)
        self.assertEqual(response.data['rating'], 5)

    def test_duplicate_agent_review(self):
        """Test that a user cannot review the same agent instance twice"""
        # Create first review
        AgentReview.objects.create(
            ai_agent_instance=self.agent_instance,
            user=self.user,
            rating=5
        )

        url = reverse('agent-reviews', kwargs={'ai_agent_pk': self.ai_agent.pk})
        data = {
            'ai_agent_instance_id': str(self.agent_instance.id),
            'rating': 4,
            'headline': 'Second review'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AgentReview.objects.count(), 1)

    def test_create_execution_review(self):
        """Test creating a new execution review"""
        url = reverse('execution-reviews', kwargs={'ai_agent_pk': self.ai_agent.pk})
        data = {
            'execution_id': str(self.task_execution.id),
            'rating': 4,
            'short_feedback': 'Good execution'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskExecutionReview.objects.count(), 1)
        self.assertEqual(response.data['rating'], 4)

    def test_get_review_stats(self):
        """Test getting review statistics"""
        # Create some reviews
        AgentReview.objects.create(
            ai_agent_instance=self.agent_instance,
            user=self.user,
            rating=5
        )
        TaskExecutionReview.objects.create(
            execution=self.task_execution,
            user=self.user,
            rating=4,
            ai_agent_instance=self.agent_instance
        )

        url = reverse('agent-review-stats', kwargs={'ai_agent_pk': self.ai_agent.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['main_reviews']['total'], 1)
        self.assertEqual(response.data['execution_reviews']['total'], 1)
        self.assertEqual(response.data['main_reviews']['average'], 5.0)
        self.assertEqual(response.data['execution_reviews']['average'], 4.0)

    def test_list_reviews_ordering(self):
        """Test review list ordering"""
        # Create reviews with different ratings
        for rating in [3, 5, 1, 4, 2]:
            AgentReview.objects.create(
                ai_agent_instance=self.agent_instance,
                user=User.objects.create_user(
                    username=f'user{rating}',
                    email=f'user{rating}@example.com',
                    password='pass123'
                ),
                rating=rating
            )

        url = reverse('agent-reviews', kwargs={'ai_agent_pk': self.ai_agent.pk})
        
        # Test ascending order
        response = self.client.get(f"{url}?ordering=rating")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [r['rating'] for r in response.data['results']]
        self.assertEqual(ratings, [1, 2, 3, 4, 5])

        # Test descending order
        response = self.client.get(f"{url}?ordering=-rating")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [r['rating'] for r in response.data['results']]
        self.assertEqual(ratings, [5, 4, 3, 2, 1]) 