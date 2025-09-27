from rest_framework import serializers
from apps.ai_agents.models import AIAgent, Capability, AIAgentInstance, AgentReview
from apps.executions.models import TaskExecution
from apps.executions.choices import ExecutionStatusChoices



class CapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Capability
        fields = ['id', 'name', 'description']


class AIAgentProfileSerializer(serializers.ModelSerializer):
    task_execution_count = serializers.SerializerMethodField()


    def get_task_execution_count(self, obj):
        return TaskExecution.objects.filter(ai_agent_instance__ai_agent=obj).count()

    class Meta:
        model = AIAgent
        fields = [
            'id', 'slug', 'avatar', 'dark_avatar', 'key', 'name', 'rating', 'review_count', 'task_execution_count'
        ]


class AIAgentShortSerializer(serializers.ModelSerializer):
    is_hired = serializers.SerializerMethodField()
    task_execution_count = serializers.SerializerMethodField()
    is_reviewed = serializers.SerializerMethodField()
    
    def get_is_reviewed(self, obj):
        user = self.context.get('user')
        return AgentReview.objects.filter(user = user, ai_agent_instance__ai_agent = obj).exists()

    def get_task_execution_count(self, obj):
        return TaskExecution.objects.filter(ai_agent_instance__ai_agent=obj).count()

    class Meta:
        model = AIAgent
        fields = [
            'id', 'slug', 'avatar', 'dark_avatar', 'key', 'name',
            'display_tagline', 'display_description', 'model', 'is_reviewed', 'is_hired', 'rating', 'review_count',
            'task_execution_count'
        ]

    def get_is_hired(self, obj):
        workspace = self.context.get('workspace')
        if not workspace:
            return False
        return obj.instances.filter(workspace=workspace).exists()
    

class AIAgentSerializer(serializers.ModelSerializer):
    capabilities = CapabilitySerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()
    is_hired = serializers.SerializerMethodField()
    task_execution_count = serializers.SerializerMethodField()
    is_reviewed = serializers.SerializerMethodField()
    
    def get_is_reviewed(self, obj):
        user = self.context.get('user')
        return AgentReview.objects.filter(user = user, ai_agent_instance__ai_agent = obj).exists()

    def get_task_execution_count(self, obj):
        return TaskExecution.objects.filter(ai_agent_instance__ai_agent=obj).count()
    
    def get_tasks(self, obj):
        from apps.workflows.api.serializers import TaskShortSerializer
        all_agent_tasks = obj.tasks.all()
        serialized_tasks = TaskShortSerializer(all_agent_tasks, many=True)
        return serialized_tasks.data

    def get_is_hired(self, obj):
        workspace = self.context.get('workspace')
        if not workspace:
            return False
        return obj.instances.filter(workspace=workspace).exists()

    class Meta:
        model = AIAgent
        fields = [
            'id', 'slug', 'avatar', 'rating', 'review_count', 'dark_avatar', 'is_hired', 'is_reviewed', 'key', 'name', 'display_tagline', 'display_description', 'model', 'capabilities', 'tasks', 'task_execution_count'
        ]



class AIAgentInstanceDetailSerializer(serializers.ModelSerializer):
    """Serializer for AI Agent Instance (Workspace-specific)"""
    ai_agent = serializers.PrimaryKeyRelatedField(
        queryset=AIAgent.objects.all(), 
        write_only=True
    )
    ai_agent_details = serializers.SerializerMethodField()
    task_execution_count = serializers.SerializerMethodField()
    total_success_rate = serializers.SerializerMethodField()

    def get_task_execution_count(self, obj):
        return TaskExecution.objects.filter(ai_agent_instance=obj).count()

    def get_total_success_rate(self, obj):
        total_success_executions = TaskExecution.objects.filter(ai_agent_instance=obj, status=ExecutionStatusChoices.COMPLETED).count()
        total_executions = TaskExecution.objects.filter(ai_agent_instance=obj).count()
        if total_executions == 0:
            return '0%'
        percent_success = (total_success_executions / total_executions) * 100
        return f'{round(percent_success, 2)}%'

    def get_ai_agent_details(self, obj):
        serializer = AIAgentShortSerializer(obj.ai_agent, context=self.context)
        return serializer.data

    class Meta:
        model = AIAgentInstance
        fields = [
            "id",
            "ai_agent",
            "ai_agent_details",
            "agent_instance_knowledge",
            "agent_instance_instructions",
            "workspace",
            "task_execution_count",
            "total_success_rate"
        ]
        read_only_fields = ['id']

    def get_fields(self):
        fields = super().get_fields()
        if self.instance:
            # Make ai_agent read-only on updates
            fields['ai_agent'].read_only = True
        return fields


class AIAgentInstanceSerializer(serializers.ModelSerializer):
    """Serializer for AI Agent Instance (Workspace-specific)"""
    ai_agent = serializers.PrimaryKeyRelatedField(
        queryset=AIAgent.objects.all(), 
        write_only=True
    )
    ai_agent_details = serializers.SerializerMethodField()
    task_execution_count = serializers.SerializerMethodField()

    def get_task_execution_count(self, obj):
        return TaskExecution.objects.filter(ai_agent_instance=obj).count()

    def get_ai_agent_details(self, obj):
        serializer = AIAgentShortSerializer(obj.ai_agent, context=self.context)
        return serializer.data

    class Meta:
        model = AIAgentInstance
        fields = [
            "id",
            "ai_agent",
            "ai_agent_details",
            "agent_instance_knowledge",
            "agent_instance_instructions",
            "task_execution_count"
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'ai_agent': {'write_once_only': True}
        }
    
    
    def validate(self, data):
        """Validate that this agent doesn't already exist in the workspace"""
        ai_agent = data.get('ai_agent')
        workspace = self.context['request'].workspace
        
        # Only perform this validation on create
        if self.instance is None and ai_agent:
            if AIAgentInstance.objects.filter(ai_agent=ai_agent, workspace=workspace).exists():
                raise serializers.ValidationError(
                    {"ai_agent": "This agent already exists in your workspace."}
                )
        return data
    
    def create(self, validated_data):
        """Create a new AI Agent instance tied to the workspace from middleware"""
        workspace = self.context["request"].workspace
        return AIAgentInstance.objects.create(workspace=workspace, **validated_data)
    

