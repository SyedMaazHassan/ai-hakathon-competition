from django.core.management.base import BaseCommand
from apps.ai_agents.models import AIAgent, Capability
from apps.workflows.models import Task, TaskInput, TaskOutputSchema, TaskOutputSchemaField
from apps.workflows.choices import TaskInputTypeChoices, TaskOutputFieldTypeChoices


class Command(BaseCommand):
    help = "Create Blog Writer AI agent with complete tasks, capabilities, input fields, and output schemas."

    def handle(self, *args, **kwargs):
        agent_data = {
            "key": "blog_writer",
            "name": "Blog Writer",
            "display_tagline": "Your AI assistant for generating SEO blogs.",
            "display_description": (
                "A specialized AI agent trained to generate SEO-optimized blog content, outlines, meta descriptions, and "
                "repurposed social snippets. It supports enhancing old blogs and improving internal linking strategies."
            ),
            "model": "gpt-4",
            "role": "You are a senior SEO-focused content strategist and blog writer.",
            "description": (
                "As Blog Writer, your job is to create high-quality, SEO-optimized, audience-specific content in blog format. "
                "You write full blogs, improve existing ones, generate outlines, and optimize on-page SEO elements such as meta descriptions "
                "and internal links. You deeply understand storytelling, formatting, CTAs, and user personas."
            ),
            "agent_instructions": [
                "Always follow best practices for SEO blog writing.",
                "Use a structured format with clear H2s, short paragraphs, and CTA where applicable.",
                "Respect tone, audience, and keyword placement carefully.",
                "Don’t make up facts. If uncertain, be general or ask for clarification.",
                "Outputs should be useful, actionable, and formatted for copy-paste usage."
            ]
        }

        capabilities = [
            {"name": "SEO Blog Generation", "description": "Writes full-length SEO-optimized blog posts."},
            {"name": "Blog Outline Creation", "description": "Creates structured outlines with SEO headers."},
            {"name": "Content Enhancement", "description": "Improves clarity, tone, and SEO of existing blog content."},
            {"name": "Meta Description Writing", "description": "Generates keyword-rich SEO meta descriptions."},
            {"name": "Content Repurposing", "description": "Extracts social media post snippets from long-form blog content."},
            {"name": "Internal Linking", "description": "Suggests internal URLs based on blog topic and structure."}
        ]

        tasks = [
            {
                "key": "generate_blog_outline",
                "name": "Create Blog Outline",
                "display_description": "Generate a structured blog outline with headers and CTA idea.",
                "description": "Use topic and primary keyword to generate an SEO-friendly blog outline with H2s and CTA suggestion.",
                "inputs": [
                    {"name": "Topic", "key": "topic", "input_type": TaskInputTypeChoices.TEXT, "description": "Main blog topic"},
                    {"name": "Primary Keyword", "key": "primary_keyword", "input_type": TaskInputTypeChoices.TEXT, "description": "Focus keyword"}
                ],
                "outputs": [
                    {"name": "Outline", "key": "outline", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "Formatted outline with sections"}
                ]
            },
            {
                "key": "generate_full_blog",
                "name": "Write Full Blog",
                "display_description": "Generate a complete SEO blog article.",
                "description": "Use topic, keyword, tone, and audience info to write a complete blog post with structure and CTA.",
                "inputs": [
                    {"name": "Topic", "key": "topic", "input_type": TaskInputTypeChoices.TEXT, "description": "Main blog topic"},
                    {"name": "Keyword", "key": "keyword", "input_type": TaskInputTypeChoices.TEXT, "description": "Primary SEO keyword"},
                    {"name": "Audience", "key": "audience", "input_type": TaskInputTypeChoices.TEXTAREA, "description": "Target audience"},
                    {"name": "Tone", "key": "tone", "input_type": TaskInputTypeChoices.SELECT, "options": ["Professional", "Conversational", "Witty", "Educational"], "description": "Tone of voice"}
                ],
                "outputs": [
                    {"name": "Title", "key": "title", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "SEO-optimized blog title"},
                    {"name": "Content", "key": "content", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "Full blog content"},
                    {"name": "Meta Description", "key": "meta_description", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "Short SEO description"}
                ]
            },
            {
                "key": "improve_existing_blog",
                "name": "Blog Enhancer",
                "display_description": "Improve tone, SEO, and clarity of existing blog content.",
                "description": "Analyze and enhance an existing blog to improve structure, tone, keyword usage, and SEO quality.",
                "inputs": [
                    {"name": "Existing Blog", "key": "existing_blog", "input_type": TaskInputTypeChoices.TEXTAREA, "description": "Paste existing blog content"},
                    {"name": "Target Audience", "key": "audience", "input_type": TaskInputTypeChoices.TEXT, "description": "Who is the blog for"},
                    {"name": "Keyword", "key": "keyword", "input_type": TaskInputTypeChoices.TEXT, "description": "Primary SEO keyword"},
                    {"name": "Tone", "key": "tone", "input_type": TaskInputTypeChoices.SELECT, "options": ["Professional", "Conversational", "Witty", "Educational"], "description": "Target tone"}
                ],
                "outputs": [
                    {"name": "Improved Blog", "key": "improved_blog", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "Enhanced blog version"},
                    {"name": "Suggestions", "key": "suggestions", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "List of improvements made"}
                ]
            },
            {
                "key": "write_meta_description",
                "name": "SEO Meta Description",
                "display_description": "Generate a 150–160 character SEO meta description.",
                "description": "Use blog title and summary to generate a concise and keyword-rich SEO meta description.",
                "inputs": [
                    {"name": "Blog Title", "key": "title", "input_type": TaskInputTypeChoices.TEXT, "description": "The title of the blog"},
                    {"name": "Blog Summary", "key": "summary", "input_type": TaskInputTypeChoices.TEXTAREA, "description": "Brief summary or intro paragraph"}
                ],
                "outputs": [
                    {"name": "Meta Description", "key": "meta_description", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "SEO meta description"}
                ]
            },
            {
                "key": "blog_to_social_teasers",
                "name": "Convert Blog to Social Snippets",
                "display_description": "Extract social post formats from blog content.",
                "description": "Generate teaser posts or captions from full blog for platforms like LinkedIn, Twitter, or email intros.",
                "inputs": [
                    {"name": "Blog Content", "key": "blog_content", "input_type": TaskInputTypeChoices.TEXTAREA, "description": "Full blog or selected section"},
                    {"name": "Platform", "key": "platform", "input_type": TaskInputTypeChoices.SELECT, "options": ["LinkedIn", "Twitter", "Instagram", "Email"], "description": "Where the teaser will be used"}
                ],
                "outputs": [
                    {"name": "Social Snippet", "key": "snippet", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "Short, engaging teaser"}
                ]
            },
            {
                "key": "suggest_internal_links",
                "name": "Internal Link Finder",
                "display_description": "Suggest internal blog/page links.",
                "description": "Given a topic and list of available internal URLs, recommend relevant internal links to include in the blog.",
                "inputs": [
                    {"name": "Blog Topic", "key": "topic", "input_type": TaskInputTypeChoices.TEXT, "description": "Topic or title of the blog"},
                    {"name": "Available URLs", "key": "urls", "input_type": TaskInputTypeChoices.TEXTAREA, "description": "List of internal blog/page URLs"}
                ],
                "outputs": [
                    {"name": "Suggested Links", "key": "links", "field_type": TaskOutputFieldTypeChoices.STRING, "description": "Relevant internal links"}
                ]
            }
        ]

        agent, created = AIAgent.objects.get_or_create(key=agent_data["key"], defaults=agent_data)
        if created:
            self.stdout.write(self.style.SUCCESS(f"✅ Created agent: {agent.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ Agent already exists: {agent.name}"))

        for cap in capabilities:
            Capability.objects.get_or_create(name=cap["name"], ai_agent=agent, defaults={"description": cap["description"]})

        for task_def in tasks:
            inputs = task_def.pop("inputs", [])
            outputs = task_def.pop("outputs", [])
            task, _ = Task.objects.get_or_create(key=task_def["key"], defaults={**task_def, "ai_agent": agent})
            for i, input_data in enumerate(inputs):
                TaskInput.objects.get_or_create(
                    task=task,
                    key=input_data["key"],
                    defaults={
                        "name": input_data["name"],
                        "input_type": input_data["input_type"],
                        "description": input_data.get("description", ""),
                        "order": i,
                        "options": input_data.get("options", []),
                        "is_required": True,
                    }
                )
            output_schema, _ = TaskOutputSchema.objects.get_or_create(
                task=task,
                defaults={
                    "name": f"{task.name} Output",
                    "description": f"Output schema for task {task.name}"
                }
            )
            for j, field in enumerate(outputs):
                TaskOutputSchemaField.objects.get_or_create(
                    task_output_schema=output_schema,
                    key=field["key"],
                    defaults={
                        "name": field["name"],
                        "field_type": field["field_type"],
                        "description": field["description"],
                        "order": j,
                        "is_required": True
                    }
                )

        self.stdout.write(self.style.SUCCESS("🎯 Blog Writer agent and all tasks set up successfully!"))
