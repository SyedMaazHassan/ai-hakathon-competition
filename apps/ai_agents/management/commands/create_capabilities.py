from django.core.management.base import BaseCommand
from apps.ai_agents.models import AIAgent, Capability

class Command(BaseCommand):
    help = "Add relevant capabilities to all AI agents based on their role and description"

    def handle(self, *args, **kwargs):
        capabilities_mapping = {
            "ai_strategist": [
                {"name": "Market Research", "description": "Analyzes market trends and identifies opportunities."},
                {"name": "Campaign Planning", "description": "Develops and structures marketing campaigns for businesses."},
                {"name": "Brand Positioning", "description": "Helps businesses establish strong and unique brand identity."},
                {"name": "Competitive Analysis", "description": "Evaluates competitor strategies to refine marketing approaches."},
                {"name": "ROI Optimization", "description": "Maximizes return on investment through data-driven marketing decisions."}
            ],
            "ai_content_writer": [
                {"name": "SEO Optimization", "description": "Generates keyword-optimized content to boost search rankings."},
                {"name": "Ad Copywriting", "description": "Creates persuasive ad copies for different marketing channels."},
                {"name": "Blog & Article Writing", "description": "Produces high-quality, engaging content tailored to the audience."},
                {"name": "Email Sequences", "description": "Writes effective email campaigns to improve conversions."},
                {"name": "Storytelling & Engagement", "description": "Enhances content with storytelling techniques to captivate readers."}
            ],
            "ai_analyst": [
                {"name": "Data Interpretation", "description": "Extracts key insights from marketing data and reports."},
                {"name": "Performance Tracking", "description": "Monitors conversion rates, CTR, and engagement metrics."},
                {"name": "Anomaly Detection", "description": "Identifies performance issues and suggests corrective actions."},
                {"name": "Predictive Analytics", "description": "Forecasts future trends based on past performance data."},
                {"name": "Report Generation", "description": "Generates visually engaging marketing performance reports."}
            ],
            "ai_competitor_analysis": [
                {"name": "Competitor Benchmarking", "description": "Evaluates pricing, positioning, and strategies of competitors."},
                {"name": "SWOT Analysis", "description": "Identifies strengths, weaknesses, opportunities, and threats."},
                {"name": "Market Trend Analysis", "description": "Monitors industry trends and suggests adaptation strategies."},
                {"name": "Campaign Intelligence", "description": "Analyzes competitors’ paid ads, engagement, and audience sentiment."},
                {"name": "Differentiation Strategy", "description": "Provides actionable insights to stand out in the market."}
            ]
        }

        agents = AIAgent.objects.all()
        if not agents.exists():
            self.stdout.write(self.style.WARNING("No AI agents found in the database."))
            return

        for agent in agents:
            capabilities = capabilities_mapping.get(agent.key, [])
            if not capabilities:
                self.stdout.write(self.style.WARNING(f"No predefined capabilities found for agent: {agent.name}"))
                continue

            for cap_data in capabilities:
                capability, created = Capability.objects.get_or_create(
                    name=cap_data["name"],
                    ai_agent=agent,
                    defaults={"description": cap_data["description"]}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Added capability "{capability.name}" to agent "{agent.name}"'))
                else:
                    self.stdout.write(self.style.WARNING(f'Capability "{capability.name}" already exists for agent "{agent.name}"'))

        self.stdout.write(self.style.SUCCESS("Capabilities assignment completed successfully!"))
