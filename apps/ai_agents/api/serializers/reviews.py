from apps.ai_agents.models import AIAgent, AIAgentInstance, AgentReview, TaskExecutionReview
from apps.authentication.api.serializers import UserMinimalSerializer
from django.db.models import Count
from rest_framework import serializers
from apps.executions.models import TaskExecution
from apps.executions.api.serializers import TaskExecutionSerializer 
from collections import defaultdict




class AgentReviewSerializer(serializers.ModelSerializer):
    """Serializer for creating agent reviews"""
    user = UserMinimalSerializer(read_only=True)
    ai_agent_instance = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )
    ai_agent_instance_id = serializers.CharField(write_only=True)

    class Meta:
        model = AgentReview
        fields = [
            'id', 'ai_agent_instance', 'ai_agent_instance_id',
            'user', 'rating', 'headline', 'review_text', 'created_at'
        ]
        read_only_fields = ['user', 'created_at', 'ai_agent_instance']

    def validate(self, attrs):
        # Model's clean() method will handle business logic validation
        return attrs

    # validate if ai agent instance belongs to the workspace
    def validate_ai_agent_instance_id(self, value):
        workspace = self.context.get('request').workspace
        

        ai_agent_id = self.context.get('view').kwargs.get('ai_agent_pk')

        try:
            ai_agent_instance = AIAgentInstance.objects.get(
                id=value,
                ai_agent_id=ai_agent_id,
                workspace=workspace
            )
            return ai_agent_instance.id
        except AIAgentInstance.DoesNotExist:
            raise serializers.ValidationError(
                'AI agent instance does not exist or does not belong to this agent/workspace'
            )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        instance = super().create(validated_data)
        return instance


class TaskExecutionReviewSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    execution_id = serializers.CharField()
    execution = TaskExecutionSerializer(read_only=True)

    class Meta:
        model = TaskExecutionReview
        fields = [
            'id', 'execution_id', 'execution', 'user',
            'rating', 'short_feedback', 'created_at'
        ]
        read_only_fields = ['user', 'created_at', 'execution']

    # validate if execution belongs to the workspace
    def validate_execution_id(self, value):
        user = self.context.get('request').user
        try:
            execution = TaskExecution.objects.get(id=value)
            if execution.user != user:
                raise serializers.ValidationError('You are not allowed to review this execution')
            return execution
        except TaskExecution.DoesNotExist:
            raise serializers.ValidationError('Execution does not exist')
    
    def create(self, validated_data):
        execution = validated_data.pop('execution_id')
        validated_data['execution'] = execution
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RatingDistributionSerializer(serializers.Serializer):
    """Serializer for rating distribution data"""
    total = serializers.IntegerField()
    distribution = serializers.DictField(child=serializers.IntegerField())
    average = serializers.FloatField()





class AgentReviewStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for agent review statistics
    
    TODO: Consider adding timestamp-based analytics for future features:
    - Monthly/quarterly review trends
    - Review volume over time
    - Performance improvements tracking
    """
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    rating_distribution = serializers.SerializerMethodField()
    overall_stats = serializers.SerializerMethodField()

    # Constants
    MIN_RATING = 1
    MAX_RATING = 5

    class Meta:
        model = AIAgent
        fields = ['average_rating', 'total_reviews', 'rating_distribution', 'overall_stats']

    def _get_agent_review_stats(self, obj):
        """Get agent review statistics - cached to avoid duplicate queries"""
        if not hasattr(self, '_agent_stats'):
            self._agent_stats = {}
        
        if obj.id not in self._agent_stats:
            reviews = AgentReview.objects.filter(
                ai_agent_instance__ai_agent=obj,
                rating__isnull=False
            ).values('rating').annotate(count=Count('rating'))
            
            stats = {
                'total_count': 0,
                'total_rating': 0,
                'distribution': {}
            }
            
            for review in reviews:
                rating = review['rating']
                count = review['count']
                stats['total_count'] += count
                stats['total_rating'] += rating * count
                stats['distribution'][rating] = count
            
            stats['average'] = (
                stats['total_rating'] / stats['total_count'] 
                if stats['total_count'] > 0 else 0.0
            )
            
            self._agent_stats[obj.id] = stats
        
        return self._agent_stats[obj.id]

    def _get_task_review_stats(self, obj):
        """Get task execution review statistics - cached to avoid duplicate queries"""
        if not hasattr(self, '_task_stats'):
            self._task_stats = {}
        
        if obj.id not in self._task_stats:
            reviews = TaskExecutionReview.objects.filter(
                execution__ai_agent_instance__ai_agent=obj,
                rating__isnull=False
            ).values('rating').annotate(count=Count('rating'))
            
            stats = {
                'total_count': 0,
                'total_rating': 0,
                'distribution': {}
            }
            
            for review in reviews:
                rating = review['rating']
                count = review['count']
                stats['total_count'] += count
                stats['total_rating'] += rating * count
                stats['distribution'][rating] = count
            
            stats['average'] = (
                stats['total_rating'] / stats['total_count'] 
                if stats['total_count'] > 0 else 0.0
            )
            
            self._task_stats[obj.id] = stats
        
        return self._task_stats[obj.id]

    def _get_rating_distribution_dict(self, distribution):
        """Convert rating distribution to string keys with all ratings represented"""
        result = {}
        for rating in range(self.MIN_RATING, self.MAX_RATING + 1):
            result[str(rating)] = distribution.get(rating, 0)
        return result

    def get_average_rating(self, obj):
        """Get average rating from agent reviews only"""
        stats = self._get_agent_review_stats(obj)
        return round(stats['average'], 2)

    def get_total_reviews(self, obj):
        """Get total count of agent reviews only"""
        stats = self._get_agent_review_stats(obj)
        return stats['total_count']

    def get_rating_distribution(self, obj):
        """Get rating distribution from agent reviews only"""
        stats = self._get_agent_review_stats(obj)
        return self._get_rating_distribution_dict(stats['distribution'])

    def get_overall_stats(self, obj):
        """
        Get combined statistics from both agent reviews and task execution reviews.
        Returns:
            - combined_average: weighted average of both review types
            - total_reviews: total number of reviews across both types
            - distribution: combined rating distribution
            - review_types: breakdown of reviews by type
        """
        agent_stats = self._get_agent_review_stats(obj)
        task_stats = self._get_task_review_stats(obj)
        
        # Calculate totals
        total_count = agent_stats['total_count'] + task_stats['total_count']
        total_rating = agent_stats['total_rating'] + task_stats['total_rating']
        
        # Calculate weighted average
        weighted_avg = total_rating / total_count if total_count > 0 else 0.0
        
        # Combine distributions
        combined_distribution = defaultdict(int)
        for rating, count in agent_stats['distribution'].items():
            combined_distribution[rating] += count
        for rating, count in task_stats['distribution'].items():
            combined_distribution[rating] += count
        
        return {
            'combined_average': round(weighted_avg, 2),
            'combined_average_integer': int(weighted_avg),
            'total_reviews': total_count,
            'distribution': self._get_rating_distribution_dict(dict(combined_distribution)),
            'review_types': {
                'agent_reviews': {
                    'count': agent_stats['total_count'],
                    'average': round(agent_stats['average'], 2)
                },
                'task_reviews': {
                    'count': task_stats['total_count'],
                    'average': round(task_stats['average'], 2)
                }
            }
        }