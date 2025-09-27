from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import BaseModel
from apps.ai_agents.agent_frameworks.schemas.description import CapabilityItem
from apps.ai_agents.choices import Mode
from apps.ai_agents.managers import ActiveAIAgentManager
from apps.executions.choices import ExecutionStatusChoices, ExecutionContextChoices
from django.utils.text import slugify

# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver

class AIAgent(BaseModel):  
    PREFIX = "agent"
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True, db_index=True, help_text="Slug for the AI agent")
    avatar = models.ImageField(upload_to="agents/logos", null=True, blank=True)
    dark_avatar = models.ImageField(upload_to="agents/logos", null=True, blank=True, help_text="Dark mode avatar for the AI agent")
    key = models.CharField(max_length=255, unique=True, db_index=True, help_text="Unique identifier for the AI agent")
    name = models.CharField(max_length=255, db_index=True, help_text="AI Agent Name")
    mode = models.CharField(max_length=255, choices=Mode.choices, default=Mode.LIVE) 
    display_tagline = models.TextField(blank=True, null=True, help_text="One line description for users")
    display_description = models.TextField(blank=True, null=True, help_text="User-facing description of the AI agent for platform users")
    model = models.CharField(max_length=255, default="gpt-3.5-turbo", help_text="Model type (e.g., GPT-4, Claude, etc.)")
    role = models.CharField(max_length=255, blank=True, null=True, help_text="Defines AI role (Assistant, Strategist, etc.)")
    description = models.TextField(blank=True, null=True, help_text="Internal description for the AI model (used in prompts)")
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], help_text="Average rating of the AI agent")
    review_count = models.IntegerField(default=0, help_text="Total number of reviews for the AI agent")
    tools = models.ManyToManyField(
        "tools.AIAgentTool",
        related_name="ai_agents",
        help_text="External Tools",
        blank=True
    )
    agent_instructions = models.JSONField(default=list, null=True, blank=True, help_text="Custom instructions for the AI agent")
    agent_knowledge = models.JSONField(default=dict, null=True, blank=True, help_text="Shared knowledge across all instances")
    is_testable = models.BooleanField(
        default=False,
        help_text="Allow this agent to be used in test mode"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this agent is active")

    objects = ActiveAIAgentManager()  # Default: only active
    all_objects = models.Manager()    # All, for admin

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_capabilities(self):
        return self.capabilities.all()
    
    def get_tasks(self):
        return self.tasks.all()

    class Meta:
        verbose_name = "AI Agent"
        verbose_name_plural = "AI Agents"

    def __str__(self):
        return self.name
    

class Capability(BaseModel):
    PREFIX = "cap"
    name = models.CharField(max_length=255, db_index=True, help_text="Name of the AI agent capability")
    description = models.TextField(blank=True, null=True, help_text="Detailed description of the capability")
    ai_agent = models.ForeignKey(
        AIAgent,
        on_delete=models.CASCADE,
        related_name="capabilities",
        db_index=True,
        help_text="The AI Agent this capability belongs to"
    )

    def to_pydantic(self) -> CapabilityItem:
        return CapabilityItem(
            name=self.name,
            description=self.description or ""
        )

    class Meta:
        verbose_name = "AI Agent Capability"
        verbose_name_plural = "AI Agent Capabilities"
        unique_together = (("name", "ai_agent"),)
        

    def __str__(self):
        return self.name


class AIAgentInstance(BaseModel):
    PREFIX = "agentinst"
    is_demo = models.BooleanField(default=False, help_text="Whether this agent instance is a demo instance")
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="ai_agent_instances",
        help_text="Workspace where this AI agent instance is used"
    )
    ai_agent = models.ForeignKey(
        AIAgent,
        on_delete=models.CASCADE,
        related_name="instances",
        db_index=True,
        help_text="Reference to the original AI Agent"
    )
    agent_instance_knowledge = models.JSONField(default=dict, help_text="Personalized knowledge for this instance")
    agent_instance_instructions = models.JSONField(default=list, null=True, help_text="Task-specific modifications for this AI Agent instance")

    class Meta:
        verbose_name = "AI Agent Instance"
        verbose_name_plural = "AI Agent Instances"

    def __str__(self):
        return f"{self.ai_agent.name} in {self.workspace.name}"


class AgentReview(BaseModel):
    PREFIX = "agentrev"
    ai_agent_instance = models.ForeignKey(
        'AIAgentInstance',
        on_delete=models.CASCADE,
        related_name='main_reviews'
    )
    user = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.CASCADE,
        related_name='agent_reviews'
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    headline = models.CharField(max_length=200)
    review_text = models.TextField()

    class Meta:
        unique_together = ('ai_agent_instance', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} for {self.ai_agent_instance}"

    def clean(self):
        # Check if user has hired and executed tasks with this agent instance
        from apps.executions.models import TaskExecution
        has_executions = TaskExecution.objects.filter(
            ai_agent_instance=self.ai_agent_instance,
            user=self.user,
            status=ExecutionStatusChoices.COMPLETED
        ).exists()

        if not has_executions:
            raise ValidationError(
                'You must have hired and completed at least one task with this agent to leave a review.'
            )



class TaskExecutionReview(BaseModel):
    """
    Model for storing reviews of specific task executions.
    """
    PREFIX = "taskexecrev"
    user = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.CASCADE,
        related_name='task_reviews'
    )
    execution = models.ForeignKey(
        'executions.TaskExecution',
        on_delete=models.CASCADE,
        related_name='review'
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    test_mode = models.BooleanField(default=False)
    short_feedback = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'execution']

    def save(self, *args, **kwargs):
        if self.execution.execution_context != ExecutionContextChoices.FULL_AGENT:
            self.test_mode = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review for execution {self.execution_id} by {self.user}" 