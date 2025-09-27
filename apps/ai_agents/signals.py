from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.ai_agents.models import AgentReview, TaskExecutionReview
from apps.ai_agents.api.serializers import AgentReviewStatsSerializer


@receiver(post_save, sender=AgentReview)
def update_ai_agent_rating_and_count_from_agent_review(sender, instance, created, **kwargs):
    if not created:
        return
    
    agent = instance.ai_agent_instance.ai_agent
    stats_data = AgentReviewStatsSerializer(agent).data
    agent.rating = stats_data.get('overall_stats', {}).get('combined_average', 0)
    agent.review_count = stats_data.get('overall_stats', {}).get('review_types', {}).get('agent_reviews', {}).get('count', 0)
    agent.save(update_fields=['rating', 'review_count'])


@receiver(post_save, sender=TaskExecutionReview)
def update_ai_agent_rating_from_task_review(sender, instance, created, **kwargs):
    if not created:
        return

    agent = instance.execution.ai_agent_instance.ai_agent
    stats_data = AgentReviewStatsSerializer(agent).data
    agent.rating = stats_data.get('overall_stats', {}).get('combined_average', 0)
    agent.save(update_fields=['rating'])
