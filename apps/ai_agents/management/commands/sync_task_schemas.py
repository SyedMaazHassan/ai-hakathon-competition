from django.core.management.base import BaseCommand
from apps.workflows.models import Task, TaskInput, TaskOutputSchema, TaskOutputSchemaField
from apps.workflows.choices import TaskInputTypeChoices, TaskOutputFieldTypeChoices


class Command(BaseCommand):
    help = "Update inputs and outputs for existing Blog Writer agent tasks"

    def handle(self, *args, **kwargs):
        TASK_SCHEMAS = [
            # SEO Blog Writer
            {
                "key": "find_untapped_keywords",
                "output_schema_name": "Untapped Keyword Opportunity Map",
                "output_schema_description": "A curated list of high-potential, low-competition long-tail keywords designed for content creation that aligns with customer pain points and SEO growth goals.",
                "inputs": [
                    {
                        "name": "Business Name",
                        "key": "business_name",
                        "input_type": "text",
                        "description": "Official name of your company/product for contextual alignment",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience Pain Points",
                        "key": "audience_pain_points",
                        "input_type": "textarea",
                        "description": "Top 3-5 specific problems your audience faces (e.g., low conversion rates, poor SEO scalability)",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Core Solutions Offered",
                        "key": "core_solutions",
                        "input_type": "textarea",
                        "description": "Your primary product/service solutions aligned with pain points",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Target Geography",
                        "key": "target_geography",
                        "input_type": "text",
                        "description": "Geo-focus for search volume (e.g., US, Global, UK)",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Content Conversion Goal",
                        "key": "conversion_goal",
                        "input_type": "text",
                        "description": "Primary action for readers (e.g., free trial, demo request)",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Domain Authority (DA)",
                        "key": "domain_authority",
                        "input_type": "number",
                        "description": "Your website's estimated DA (0-100) for competition calibration",
                        "order": 6,
                        "is_required": True
                    },
                    {
                        "name": "Search Volume Range",
                        "key": "search_volume_range",
                        "input_type": "text",
                        "description": "Acceptable monthly searches (e.g., 100-2000)",
                        "order": 7,
                        "is_required": True
                    },
                    {
                        "name": "Max Keyword Difficulty",
                        "key": "max_difficulty",
                        "input_type": "number",
                        "description": "Highest acceptable difficulty score (0-100 scale)",
                        "order": 8,
                        "is_required": True
                    },
                    {
                        "name": "Competitor URLs (Optional)",
                        "key": "competitor_urls",
                        "input_type": "textarea",
                        "description": "3 competitors for gap analysis (comma-separated URLs)",
                        "order": 9,
                        "is_required": False
                    },
                    {
                        "name": "Excluded Keywords",
                        "key": "excluded_keywords",
                        "input_type": "textarea",
                        "description": "Keywords to avoid (comma-separated)",
                        "order": 10,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Keyword",
                        "key": "keyword",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Untapped long-tail keyword with commercial intent",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Monthly Volume",
                        "key": "monthly_volume",
                        "field_type": "integer",
                        "description": "Estimated search volume in target geo",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Difficulty",
                        "key": "difficulty",
                        "field_type": "float",
                        "description": "Keyword difficulty score (0-100)",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Competition Level",
                        "key": "competition_level",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "'Low', 'Medium', or 'High' based on SERP analysis",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Intent Category",
                        "key": "intent_category",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Problem-solving intent type (e.g., 'Solution-Finding', 'Pain-Point')",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Content Strategy",
                        "key": "content_strategy",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Content approach to dominate this keyword",
                        "is_required": True,
                        "order": 6
                    },
                    {
                        "name": "Priority Score",
                        "key": "priority_score",
                        "field_type": "float",
                        "description": "Strategic value score (1-100) based on volume/difficulty/CTR potential",
                        "is_required": True,
                        "order": 7
                    },
                    {
                        "name": "CTA Integration",
                        "key": "cta_integration",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Natural call-to-action suggestion for conversion goals",
                        "is_required": False,
                        "order": 8
                    }
                ]
            },
            {
                "key": "write_ranking_blogs",
                "output_schema_name": "High-Impact SEO Blog Post",
                "output_schema_description": "A long-form, SEO-optimized blog post crafted to outrank competitors, capture featured snippets, and drive conversions through comprehensive, value-driven content.",
                "inputs": [
                    {
                        "name": "Primary Target Keyword",
                        "key": "primary_target_keyword",
                        "input_type": "text",
                        "description": "The main keyword this blog post is designed to rank for. Must reflect high-intent, informational or commercial search queries.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Working Blog Title",
                        "key": "working_blog_title",
                        "input_type": "text",
                        "description": "A preliminary title for the blog post to set the creative and structural direction. This can be refined during content generation.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience Description",
                        "key": "target_audience_description",
                        "input_type": "textarea",
                        "description": "Describe the ideal reader of this blog, including their role, industry, goals, and pain points. This informs tone, examples, and depth.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Competitor URLs",
                        "key": "competitor_urls",
                        "input_type": "textarea",
                        "description": "List 3–5 top-ranking competitor blog URLs for this keyword. These will be analyzed for content gaps and improvement opportunities.",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Primary Pain Point to Address",
                        "key": "primary_pain_point",
                        "input_type": "text",
                        "description": "What is the most important problem or question the blog should help the reader solve?",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Desired Reader Outcome",
                        "key": "desired_reader_outcome",
                        "input_type": "text",
                        "description": "What should the reader understand, achieve, or do after reading this blog? This sets the success goal of the content.",
                        "order": 6,
                        "is_required": True
                    },
                    {
                        "name": "Funnel CTA Goal",
                        "key": "funnel_cta_goal",
                        "input_type": "select",
                        "description": "Choose the primary call-to-action goal for this blog post to guide reader behavior.",
                        "options": [
                            {"value": "newsletter_signup", "label": "Newsletter Signup"},
                            {"value": "resource_download", "label": "Resource Download"},
                            {"value": "demo_request", "label": "Product Demo Request"},
                            {"value": "trial_signup", "label": "Free Trial Signup"},
                            {"value": "product_page_redirect", "label": "Redirect to Product Page"}
                        ],
                        "order": 7,
                        "is_required": True
                    },
                    {
                        "name": "Brand Voice and Tone",
                        "key": "brand_voice_tone",
                        "input_type": "select",
                        "description": "Select the tone that best matches your brand identity and audience expectations.",
                        "options": [
                            {"value": "professional", "label": "Professional & Confident"},
                            {"value": "casual", "label": "Casual & Approachable"},
                            {"value": "insightful", "label": "Insightful & Thought Leadership"},
                            {"value": "direct", "label": "Direct & Action-Oriented"}
                        ],
                        "order": 8,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "SEO-Optimized Blog Title",
                        "key": "seo_blog_title",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "A compelling, keyword-optimized title that reflects search intent and encourages clicks.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Suggested H1 Heading",
                        "key": "h1_heading",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Primary H1 headline used to structure the blog and communicate its main promise.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Formatted Blog Content (Markdown)",
                        "key": "blog_markdown",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "The complete, long-form blog content formatted in clean markdown with H2s, bullets, and clear sections.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Embedded CTA Suggestions",
                        "key": "cta_suggestions",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Context-aware CTA snippets and suggested placements based on funnel goals.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Competitor Gap Highlights",
                        "key": "competitor_gap_highlights",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Brief explanation of how this content improves upon and fills gaps in top-ranking competitor blogs.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Internal Link Opportunities",
                        "key": "internal_link_opportunities",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "List of internal pages or articles to link to, including anchor text suggestions and rationale.",
                        "is_required": False,
                        "order": 6
                    },
                    {
                        "name": "Authoritative External Sources",
                        "key": "external_sources",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "List of authoritative external resources referenced for credibility and E-A-T alignment.",
                        "is_required": False,
                        "order": 7
                    }
                ]
            },
            {
                "key": "update_old_blogs",
                "output_schema_name": "SEO Refreshed Blog Content",
                "output_schema_description": "An enhanced version of an existing blog post updated with new keywords, data, structure, and internal linking to improve search performance and user experience.",
                "inputs": [
                    {
                        "name": "Original Blog URL",
                        "key": "original_blog_url",
                        "input_type": "url",
                        "description": "Public URL of the blog post you want to update for improved SEO performance.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Keyword for Refresh",
                        "key": "refresh_target_keyword",
                        "input_type": "text",
                        "description": "New or expanded keyword to target in the updated version of the blog. Should reflect recent user search trends.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Core Performance Issue",
                        "key": "core_performance_issue",
                        "input_type": "select",
                        "description": "What specific problem are you trying to solve with this update?",
                        "options": [
                            {"value": "ranking_drop", "label": "Ranking has dropped"},
                            {"value": "outdated_content", "label": "Content is outdated"},
                            {"value": "low_ctr", "label": "Low click-through rate"},
                            {"value": "not_converting", "label": "Traffic but no conversions"},
                            {"value": "competitor_overtook", "label": "Competitor outranked us"}
                        ],
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Primary CTA Goal",
                        "key": "primary_cta_goal",
                        "input_type": "select",
                        "description": "What updated action do you want readers to take after reading this refreshed blog?",
                        "options": [
                            {"value": "newsletter_signup", "label": "Newsletter Signup"},
                            {"value": "product_page", "label": "Redirect to Product Page"},
                            {"value": "demo_request", "label": "Request a Demo"},
                            {"value": "trial_signup", "label": "Start Free Trial"},
                            {"value": "resource_download", "label": "Download a Resource"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Top Competing URLs (Optional)",
                        "key": "top_competitor_urls",
                        "input_type": "textarea",
                        "description": "List 2–3 URLs of competitor blog posts currently outranking or outperforming yours. Used for gap analysis.",
                        "order": 5,
                        "is_required": False
                    },
                    {
                        "name": "Internal Pages to Link (Optional)",
                        "key": "internal_pages_to_link",
                        "input_type": "textarea",
                        "description": "List any internal URLs that should be linked from this blog post to build topic clusters.",
                        "order": 6,
                        "is_required": False
                    },
                    {
                        "name": "Original Meta Description",
                        "key": "original_meta_description",
                        "input_type": "text",
                        "description": "Paste the current meta description. This will be optimized or rewritten.",
                        "order": 7,
                        "is_required": False
                    },
                    {
                        "name": "Tone/Voice Adjustment",
                        "key": "tone_voice_adjustment",
                        "input_type": "select",
                        "description": "Do you want to update the tone or keep the original?",
                        "options": [
                            {"value": "keep_same", "label": "Keep Same"},
                            {"value": "make_more_authoritative", "label": "Make More Authoritative"},
                            {"value": "make_more_conversational", "label": "Make More Conversational"},
                            {"value": "align_with_brand", "label": "Align with Updated Brand Voice"}
                        ],
                        "order": 8,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Updated Title Tag",
                        "key": "updated_title_tag",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "SEO-enhanced title tag rewritten to reflect updated topic, keyword, and CTR potential.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Updated Meta Description",
                        "key": "updated_meta_description",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "An optimized meta description under 160 characters to improve SERP click-through rate.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Updated Blog Content (Markdown)",
                        "key": "updated_blog_markdown",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "The full blog post content with refreshed sections, new keywords, improved structure, and formatting. Markdown supported.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "New Content Sections Added",
                        "key": "new_sections_summary",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Summary of new content sections added to improve depth and match competitor coverage.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Updated Internal Links",
                        "key": "updated_internal_links",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "List of internal links added with anchor text suggestions and link target rationale.",
                        "is_required": False,
                        "order": 5
                    },
                    {
                        "name": "Updated External Sources",
                        "key": "updated_external_sources",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Authoritative external references included for accuracy and credibility.",
                        "is_required": False,
                        "order": 6
                    },
                    {
                        "name": "Updated CTA Placement",
                        "key": "updated_cta_placement",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Details of where and how new CTAs were added for better funnel alignment.",
                        "is_required": False,
                        "order": 7
                    },
                    {
                        "name": "Refresh Strategy Summary",
                        "key": "refresh_strategy_summary",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Explanation of what changed in this update and why — highlighting gaps fixed and improvements made.",
                        "is_required": True,
                        "order": 8
                    }
                ]
            },
            {
                "key": "link_blogs_for_authority",
                "output_schema_name": "Internal Linking Strategy Map",
                "output_schema_description": "A structured internal linking strategy that builds content clusters and improves SEO authority through logical, user-friendly pathways across related blog posts.",
                "inputs": [
                    {
                        "name": "Pillar Blog URL",
                        "key": "pillar_blog_url",
                        "input_type": "url",
                        "description": "The central blog post or hub page that other related posts should link to and from.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Pillar Blog Topic",
                        "key": "pillar_topic",
                        "input_type": "text",
                        "description": "Main topic or focus area of the pillar blog (e.g., 'Email Marketing Automation').",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Pillar Blog Content",
                        "key": "pillar_content",
                        "input_type": "textarea",
                        "description": "The full text content of the pillar blog for contextual linking suggestions.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Related Cluster Blog URLs",
                        "key": "related_cluster_blog_urls",
                        "input_type": "textarea",
                        "description": "Comma-separated URLs of related blog posts that can be linked from/to the pillar page.",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Current Site Categories or Topics",
                        "key": "site_categories",
                        "input_type": "textarea",
                        "description": "List of your blog’s primary content categories to ensure contextual consistency in the internal link network.",
                        "order": 5,
                        "is_required": False
                    },
                    {
                        "name": "Priority for Link Focus",
                        "key": "linking_priority",
                        "input_type": "select",
                        "description": "Choose whether you want to focus more on SEO value or user navigation.",
                        "options": [
                            {"value": "seo_boost", "label": "SEO Authority Boost"},
                            {"value": "user_journey", "label": "Improved Content Journey"},
                            {"value": "balanced", "label": "Balanced Approach"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Cluster to Pillar Link Suggestions",
                        "key": "cluster_to_pillar_links",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Plain text summary of links to be added from each cluster blog to the pillar post, including anchor text and rationale.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Pillar to Cluster Link Suggestions",
                        "key": "pillar_to_cluster_links",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Plain text summary of links to be added from the pillar post to each related blog, including anchor text and insertion context.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Optimized Anchor Text Pairs",
                        "key": "optimized_anchor_texts",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "List of SEO-optimized anchor texts mapped to their respective link targets for consistent usage.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Suggested Topic Cluster Name",
                        "key": "suggested_cluster_name",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "A name for this group of linked posts that can be reused in future content creation (e.g., 'B2B SEO Pillar Cluster').",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Linking Strategy Rationale",
                        "key": "linking_strategy_rationale",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "A strategic explanation of why the suggested internal links improve topical authority and SEO architecture.",
                        "is_required": True,
                        "order": 5
                    }
                ]
            },
            {
                "key": "track_blog_performance",
                "output_schema_name": "Blog Performance Audit Report",
                "output_schema_description": "A diagnostic report of key SEO, engagement, and technical issues affecting blog performance, with clear insights and recommendations to fix ranking and user experience drops.",
                "inputs": [
                    {
                        "name": "Blog URL",
                        "key": "blog_url",
                        "input_type": "url",
                        "description": "Link to the blog post that needs performance tracking and analysis.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Keyword",
                        "key": "target_keyword",
                        "input_type": "text",
                        "description": "Primary keyword the blog post is intended to rank for.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Business Goal for Blog",
                        "key": "blog_business_goal",
                        "input_type": "select",
                        "description": "The business outcome this blog is designed to drive.",
                        "options": [
                            {"value": "lead_generation", "label": "Lead Generation"},
                            {"value": "organic_traffic", "label": "Increase Organic Traffic"},
                            {"value": "product_awareness", "label": "Promote Product Awareness"},
                            {"value": "email_signups", "label": "Grow Email List"},
                            {"value": "conversion", "label": "Drive Conversions"}
                        ],
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Last Known Ranking Position",
                        "key": "last_known_rank",
                        "input_type": "number",
                        "description": "Last recorded position of the blog post in SERP for the target keyword.",
                        "order": 4,
                        "is_required": False
                    },
                    {
                        "name": "Performance Snapshot File",
                        "key": "performance_snapshot_file",
                        "input_type": "file",
                        "description": "Optional CSV or exported PDF from Google Analytics, Search Console, or SEO tools with metrics for this blog.",
                        "order": 5,
                        "is_required": False
                    },
                    {
                        "name": "Date of Last Blog Update",
                        "key": "last_updated_date",
                        "input_type": "date & time",
                        "description": "When this blog was last revised or optimized.",
                        "order": 6,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Overall Performance Summary",
                        "key": "overall_performance_summary",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "High-level summary of how the blog is currently performing across key SEO and engagement indicators.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Detected Issues",
                        "key": "detected_issues",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Plain text list of SEO, content, or UX-related issues identified during the audit.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Search Ranking Insights",
                        "key": "search_ranking_insights",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Details on current ranking position, fluctuation trends, and keyword ranking threats.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Technical SEO Problems",
                        "key": "technical_seo_issues",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Issues like indexing problems, mobile usability, broken links, or crawl errors detected.",
                        "is_required": False,
                        "order": 4
                    },
                    {
                        "name": "User Engagement Warnings",
                        "key": "user_engagement_warnings",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Behavioral signals like high bounce rate, low time-on-page, or poor interaction rates.",
                        "is_required": False,
                        "order": 5
                    },
                    {
                        "name": "Actionable Fix Recommendations",
                        "key": "fix_recommendations",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "A list of recommended next steps to resolve issues and boost performance.",
                        "is_required": True,
                        "order": 6
                    },
                    {
                        "name": "Priority Score",
                        "key": "priority_score",
                        "field_type": "float",
                        "description": "A score from 1–100 indicating how urgent and impactful fixing this blog is.",
                        "is_required": True,
                        "order": 7
                    }
                ]
            },
            {
                "key": "write_customer_centric_outlines",
                "output_schema_name": "Customer-Centric Blog Outline",
                "output_schema_description": "A structured and SEO-friendly blog outline designed to address specific customer pain points and deliver high value to the target audience.",
                "inputs": [
                    {
                        "name": "Target Audience Description",
                        "key": "target_audience_description",
                        "input_type": "textarea",
                        "description": "Describe the core audience (e.g., busy founders, growth marketers) including their goals, roles, and frustrations.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Primary Blog Topic or Working Title",
                        "key": "blog_topic_or_title",
                        "input_type": "text",
                        "description": "The main topic or draft title that captures the core subject and customer problem.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Core Problem This Blog Solves",
                        "key": "core_problem_solved",
                        "input_type": "text",
                        "description": "The key issue, blocker, or pain point your customer is facing which this blog addresses.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Key Questions to Answer",
                        "key": "key_questions_to_answer",
                        "input_type": "textarea",
                        "description": "List 3-5 real questions customers have asked or are likely to search related to this blog topic.",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Desired Reader Outcome",
                        "key": "desired_reader_outcome",
                        "input_type": "text",
                        "description": "What knowledge or decision-making ability should the reader gain after reading this post?",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Primary Target Keyword (Optional)",
                        "key": "primary_target_keyword",
                        "input_type": "text",
                        "description": "A specific SEO keyword to optimize the outline structure around.",
                        "default_value": "",
                        "order": 6,
                        "is_required": False
                    },
                    {
                        "name": "Representative Customer Quote or Insight (Optional)",
                        "key": "customer_quote_insight",
                        "input_type": "textarea",
                        "description": "A real quote or insight from a user that helps root the outline in real-world context.",
                        "default_value": "",
                        "order": 7,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Proposed Blog Title",
                        "key": "proposed_blog_title",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "SEO-friendly blog title aligned with customer problems and search intent.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Suggested H1 Heading",
                        "key": "suggested_h1_heading",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Main headline that introduces the promise of the blog.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Main Sections",
                        "key": "main_sections",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "listing H2 sections, each with summary and optional H3 subheadings.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Key Takeaways / Conclusion Summary",
                        "key": "conclusion_summary",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Concise wrap-up summarizing key solutions and benefits for the reader.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Call-to-Action (CTA) Suggestions",
                        "key": "cta_suggestions",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "of 1-2 CTAs aligned with reader’s next logical step (e.g., signup, demo).",
                        "is_required": False,
                        "order": 5
                    },
                    {
                        "name": "Internal Linking Opportunities",
                        "key": "internal_link_opportunities",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "suggesting anchor text + internal links to strengthen topic clusters.",
                        "is_required": False,
                        "order": 6
                    },
                    {
                        "name": "Brief Outline Rationale",
                        "key": "outline_rationale",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "2–3 sentence explanation of how the structure addresses the user's pain point.",
                        "is_required": False,
                        "order": 7
                    }
                ]
            },
   
   
            # Meta Ad optimizer
            {
                "key": "write_test_ad_copy",
                "output_schema_name": "Test-Ready Meta Ad Copy Variants",
                "output_schema_description": "A set of high-performing ad copy variants crafted for A/B testing on Meta platforms, optimized for emotional resonance, funnel fit, and CTR performance.",
                "inputs": [
                    {
                        "name": "Product or Offer Name",
                        "key": "offer_name",
                        "input_type": "text",
                        "description": "The name or title of the product, service, or offer being promoted in the ad.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience Description",
                        "key": "audience_description",
                        "input_type": "textarea",
                        "description": "Define who you're targeting — their job roles, pain points, motivations, and buying triggers.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Primary Value Proposition",
                        "key": "primary_value_prop",
                        "input_type": "text",
                        "description": "One-sentence summary of what makes this offer compelling to the target audience.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Top 3 Customer Pain Points",
                        "key": "pain_points",
                        "input_type": "textarea",
                        "description": "List the 3 biggest frustrations or challenges your audience faces that this offer solves.",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Top 3 Benefits or Outcomes",
                        "key": "benefits",
                        "input_type": "textarea",
                        "description": "List 3 specific results, transformations, or wins your product delivers.",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Call-To-Action Goal",
                        "key": "cta_goal",
                        "input_type": "text",
                        "description": "What should the user do next? (e.g., 'Book a Demo', 'Download Guide', 'Start Free Trial')",
                        "order": 6,
                        "is_required": True
                    },
                    {
                        "name": "Stage of Funnel",
                        "key": "funnel_stage",
                        "input_type": "select",
                        "description": "Where in the funnel the user will see this ad (TOFU, MOFU, BOFU)",
                        "options": ["Top of Funnel", "Middle of Funnel", "Bottom of Funnel"],
                        "order": 7,
                        "is_required": True
                    },
                    {
                        "name": "Brand Tone of Voice",
                        "key": "tone",
                        "input_type": "select",
                        "description": "Choose the preferred voice for your brand message",
                        "options": ["Professional", "Conversational", "Bold", "Empathetic", "Witty"],
                        "order": 8,
                        "is_required": False
                    },
                    {
                        "name": "Any Compliance Constraints?",
                        "key": "compliance_constraints",
                        "input_type": "textarea",
                        "description": "List any specific claims, industries, or topics to avoid due to Meta ad policy or industry regulations.",
                        "order": 9,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Ad Variant Type",
                        "key": "variant_type",
                        "description": "Type of messaging style used in this variant (e.g., Pain-Point, Benefit-Driven, Curiosity-Based).",
                        "field_type": "string"
                    },
                    {
                        "name": "Primary Hook",
                        "key": "hook",
                        "description": "The attention-grabbing opening line crafted to stop scrolling and spark interest.",
                        "field_type": "string"
                    },
                    {
                        "name": "Ad Body Text",
                        "key": "ad_body",
                        "description": "Full main copy of the ad (1-3 sentences) explaining the problem, solution, and CTA.",
                        "field_type": "string"
                    },
                    {
                        "name": "Call-To-Action (CTA)",
                        "key": "cta_text",
                        "description": "Recommended CTA phrase aligned with funnel stage and user intent.",
                        "field_type": "string"
                    },
                    {
                        "name": "Recommended Placement",
                        "key": "recommended_placement",
                        "description": "Best performing Meta ad placement for this variant (e.g., Instagram Feed, Facebook Stories).",
                        "field_type": "string"
                    },
                    {
                        "name": "Performance Testing Priority",
                        "key": "priority_score",
                        "description": "Priority score (1-100) estimating which variant should be tested first based on expected CTR or engagement.",
                        "field_type": "float"
                    }
                ]
            },
            {
                "key": "test_ad_creatives_copy",
                "output_schema_name": "Weekly Creative-Copy Test Summary",
                "output_schema_description": "A structured breakdown of tested ad variants combining copy types and creative formats, including winning combinations, performance metrics, and actionable recommendations.",
                "inputs": [
                    {
                        "name": "Campaign Objective",
                        "key": "campaign_objective",
                        "input_type": "select",
                        "description": "Select the primary goal for this campaign test (e.g., Leads, Conversions, Engagement).",
                        "options": ["Lead Generation", "Conversions", "Traffic", "Engagement", "Video Views"],
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience Overview",
                        "key": "audience_overview",
                        "input_type": "textarea",
                        "description": "Describe the audience segment being targeted (interests, pain points, demographics, funnel stage).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Copy Variants to Test",
                        "key": "copy_variants",
                        "input_type": "json",
                        "description": "Provide 3–5 ad copy variants using different tones and angles (pain-first, benefit-driven, curiosity).",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Creative Assets or Descriptions",
                        "key": "creative_assets",
                        "input_type": "json",
                        "description": "Upload creatives or describe them by format (e.g., single image, video, carousel, UGC-style).",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Budget for Testing Phase",
                        "key": "testing_budget",
                        "input_type": "number",
                        "description": "Total budget allocated for this weekly creative-copy test (in USD).",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Performance Thresholds",
                        "key": "performance_thresholds",
                        "input_type": "json",
                        "description": "Define minimum CTR, max CPA, or target ROAS to decide winning/eliminated variants.",
                        "order": 6,
                        "is_required": True
                    },
                    {
                        "name": "Funnel Stage",
                        "key": "funnel_stage",
                        "input_type": "select",
                        "description": "Where in the customer journey these ads are placed.",
                        "options": ["Top of Funnel", "Middle of Funnel", "Bottom of Funnel"],
                        "order": 7,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Tested Variant ID",
                        "key": "variant_id",
                        "description": "Unique identifier for each tested copy-creative combination.",
                        "field_type": "string"
                    },
                    {
                        "name": "Copy Type",
                        "key": "copy_type",
                        "description": "Message style used: Pain-Point, Benefit-First, or Curiosity-Based.",
                        "field_type": "string"
                    },
                    {
                        "name": "Creative Format",
                        "key": "creative_format",
                        "description": "Format used in this variant (e.g., Image, Video, Carousel, UGC).",
                        "field_type": "string"
                    },
                    {
                        "name": "Click-Through Rate (CTR)",
                        "key": "ctr",
                        "description": "CTR percentage this variant achieved during the test.",
                        "field_type": "float"
                    },
                    {
                        "name": "Cost Per Acquisition (CPA)",
                        "key": "cpa",
                        "description": "Average cost to acquire one conversion with this variant.",
                        "field_type": "float"
                    },
                    {
                        "name": "Return on Ad Spend (ROAS)",
                        "key": "roas",
                        "description": "Revenue return divided by spend (ROAS) for this combination.",
                        "field_type": "float"
                    },
                    {
                        "name": "Performance Verdict",
                        "key": "performance_verdict",
                        "description": "Categorization: 'Winner', 'Eliminated', or 'Retest Needed'.",
                        "field_type": "string"
                    },
                    {
                        "name": "Optimization Recommendation",
                        "key": "optimization_recommendation",
                        "description": "Specific advice on how to improve or scale this creative-copy pair.",
                        "field_type": "string"
                    }
                ]
            },
            {
                "key": "fix_ad_lp_mismatches",
                "output_schema_name": "Ad-to-Landing Page Congruency Report",
                "output_schema_description": "Detailed audit results showing message mismatches between ad campaigns and landing pages with recommendations to improve congruency and conversion.",
                "inputs": [
                    {
                        "name": "Ad Campaign Name",
                        "key": "campaign_name",
                        "input_type": "text",
                        "description": "Name or identifier of the Meta ad campaign under review.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Ad Copy Text",
                        "key": "ad_copy",
                        "input_type": "textarea",
                        "description": "Full text of the ad copy as it appears on Meta (including headline, primary text, and CTA).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Creative Screenshot or Description",
                        "key": "ad_creative_visual",
                        "input_type": "file",
                        "description": "Upload a screenshot or visual reference of the ad creative to evaluate visual-message congruency.",
                        "order": 3,
                        "is_required": False
                    },
                    {
                        "name": "Landing Page URL",
                        "key": "landing_page_url",
                        "input_type": "url",
                        "description": "Live link to the landing page where the ad directs users after the click.",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Primary Ad Promise",
                        "key": "ad_promise",
                        "input_type": "text",
                        "description": "The main claim, offer, or benefit the ad promotes (e.g., '50% off for new users').",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience Segment",
                        "key": "target_audience",
                        "input_type": "text",
                        "description": "The audience group this campaign targets (e.g., 'new customers in US', 'ecom buyers').",
                        "order": 6,
                        "is_required": False
                    },
                    {
                        "name": "Conversion Goal",
                        "key": "conversion_goal",
                        "input_type": "select",
                        "description": "Select the intended user action.",
                        "options": ["Sign Up", "Purchase", "Download", "Schedule Call", "Free Trial"],
                        "order": 7,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Mismatch Type",
                        "key": "mismatch_type",
                        "description": "Category of mismatch identified (e.g., Offer Inconsistency, CTA Confusion, Tone Mismatch).",
                        "field_type": "string"
                    },
                    {
                        "name": "Mismatch Explanation",
                        "key": "mismatch_explanation",
                        "description": "Brief explanation of why the ad and landing page are not aligned.",
                        "field_type": "string"
                    },
                    {
                        "name": "Suggested Fix",
                        "key": "suggested_fix",
                        "description": "Recommended change to either the ad or landing page to restore congruency.",
                        "field_type": "string"
                    },
                    {
                        "name": "Confidence Score",
                        "key": "confidence_score",
                        "description": "Confidence level (0-100) that resolving this mismatch will improve conversions.",
                        "field_type": "integer"
                    },
                    {
                        "name": "CTA Alignment Verdict",
                        "key": "cta_alignment",
                        "description": "'Aligned', 'Partial Match', or 'Misaligned' based on CTA match between ad and landing page.",
                        "field_type": "string"
                    },
                    {
                        "name": "Visual Congruency Feedback",
                        "key": "visual_feedback",
                        "description": "Commentary on whether visual elements in the ad match the landing page experience.",
                        "field_type": "string"
                    }
                ]
            },
            {
                "key": "reallocate_budget_daily",
                "output_schema_name": "Daily Budget Optimization Report",
                "output_schema_description": "Summary of daily ad spend adjustments based on real-time ROAS and performance trends. Highlights budget shifts and scaling decisions.",
                "inputs": [
                    {
                        "name": "Campaign Group Name",
                        "key": "campaign_group_name",
                        "input_type": "text",
                        "description": "Name of the ad campaign group being monitored for optimization.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Daily Budget Pool",
                        "key": "daily_budget",
                        "input_type": "number",
                        "description": "Total available daily budget (in USD) for distribution across campaigns.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "ROAS Threshold",
                        "key": "roas_threshold",
                        "input_type": "number",
                        "description": "Minimum acceptable ROAS value for a campaign to keep receiving budget.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Performance Snapshot",
                        "key": "performance_data",
                        "input_type": "file",
                        "description": "CSV or JSON file containing yesterday’s campaign performance data.",
                        "order": 4,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Scaled Campaigns",
                        "key": "scaled_campaigns",
                        "description": "List of campaigns that received increased budget due to strong performance.",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    },
                    {
                        "name": "Paused or Limited Campaigns",
                        "key": "limited_campaigns",
                        "description": "List of underperforming campaigns that were paused or received reduced spend.",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    },
                    {
                        "name": "New Budget Allocation",
                        "key": "new_budget_plan",
                        "description": "Final per-campaign daily budget allocation after optimization.",
                        "field_type": "object"
                    },
                    {
                        "name": "Optimization Notes",
                        "key": "optimization_notes",
                        "description": "Agent reasoning or commentary behind the adjustments made.",
                        "field_type": "string"
                    }
                ]
            },
            {
                "key": "create_ads_by_buyer_stage",
                "output_schema_name": "Buyer Journey Ad Set",
                "output_schema_description": "Tailored ad campaign sets structured by funnel stages — cold, warm, hot — with matching copy, creative, and CTA strategy.",
                "inputs": [
                    {
                        "name": "Product or Offer Name",
                        "key": "offer_name",
                        "input_type": "text",
                        "description": "Name of the product, service, or offer being promoted.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience Description",
                        "key": "audience_description",
                        "input_type": "textarea",
                        "description": "Brief about the audience personas (e.g., startup founders, fitness moms, etc).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Funnel Goals",
                        "key": "funnel_goals",
                        "input_type": "textarea",
                        "description": "Key actions you want at each funnel stage (e.g., awareness, lead, purchase).",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Creative Types Available",
                        "key": "available_creatives",
                        "input_type": "select",
                        "description": "Type of creatives you have ready to use.",
                        "options": ["Image", "Video", "Carousel", "UGC", "All"],
                        "order": 4,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Cold Audience Ads",
                        "key": "cold_ads",
                        "description": "Top-of-funnel ads focused on awareness and education.",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    },
                    {
                        "name": "Warm Audience Ads",
                        "key": "warm_ads",
                        "description": "Middle-of-funnel ads using proof, testimonials, or authority.",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    },
                    {
                        "name": "Hot Audience Ads",
                        "key": "hot_ads",
                        "description": "Bottom-of-funnel ads using urgency, scarcity, or conversion CTAs.",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    },
                    {
                        "name": "Funnel Progression Strategy",
                        "key": "funnel_progression_strategy",
                        "description": "Suggested retargeting strategy to move users across funnel stages.",
                        "field_type": "string"
                    }
                ]
            },
            {
                "key": "adapt_competitor_ads",
                "output_schema_name": "Competitor Ad Adaptation Blueprint",
                "output_schema_description": "Breakdown of high-performing competitor Meta ads and customized adaptation recommendations aligned with your brand.",
                "inputs": [
                    {
                        "name": "Competitor Brand Name",
                        "key": "competitor_name",
                        "input_type": "text",
                        "description": "Name of the brand you want to analyze for ad ideas.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Product or Category",
                        "key": "product_category",
                        "input_type": "text",
                        "description": "Product or service area you want to compare (e.g., CRM tool, skincare serum).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Your Unique Selling Point",
                        "key": "your_usp",
                        "input_type": "textarea",
                        "description": "What makes your brand different or better (used to rewrite adapted copy).",
                        "order": 3,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Top Competitor Ads Found",
                        "key": "competitor_ads",
                        "description": "List of analyzed competitor ad examples (copy summaries or screenshots).",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    },
                    {
                        "name": "Psychological Triggers Used",
                        "key": "triggers_identified",
                        "description": "Key emotional or persuasive levers used in the original ad.",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    },
                    {
                        "name": "Adapted Copy Ideas",
                        "key": "adapted_copy",
                        "description": "Recommended variations of ad copy tailored to your brand.",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    },
                    {
                        "name": "Suggested Visual Style",
                        "key": "suggested_visuals",
                        "description": "Creative format suggestions that match your offer + funnel stage.",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING
                    }
                ]
            },


            # Landing page copy expert
            {
                "key": "write_main_headline_subheadline",
                "output_schema_name": "Headline & Subheadline Variants",
                "output_schema_description": "Multiple attention-grabbing headline and subheadline combinations that clearly communicate value.",
                "inputs": [
                    {
                        "name": "Product or Offer Name",
                        "key": "offer_name",
                        "input_type": "text",
                        "description": "The name of the product, service, or offer being promoted.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Main Value Proposition",
                        "key": "value_prop",
                        "input_type": "textarea",
                        "description": "Briefly describe the core benefit or outcome your offer provides.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience",
                        "key": "target_audience",
                        "input_type": "text",
                        "description": "Who is this page speaking to (e.g. busy founders, marketing leads)?",
                        "order": 3,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Headline Variants",
                        "key": "headline_variants",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Multiple options for main headlines that grab attention.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Subheadline Variants",
                        "key": "subheadline_variants",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Matching subheadlines that support and clarify the headline.",
                        "is_required": True,
                        "order": 2
                    }
                ]
            },
            {
                "key": "features_to_benefits",
                "output_schema_name": "Feature-to-Benefit Conversion Bullets",
                "output_schema_description": "Bullet points that translate technical features into real-world user benefits.",
                "inputs": [
                    {
                        "name": "Product Features",
                        "key": "product_features",
                        "input_type": "textarea",
                        "description": "List of product features (one per line or comma-separated).",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Persona",
                        "key": "target_persona",
                        "input_type": "text",
                        "description": "Describe who these features benefit most.",
                        "order": 2,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Benefit Bullet Points",
                        "key": "benefit_bullets",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "User-facing bullet points highlighting benefits.",
                        "is_required": True,
                        "order": 1
                    }
                ]
            },
            {
                "key": "write_cta_buttons_instructions",
                "output_schema_name": "CTA Buttons + Microcopy",
                "output_schema_description": "High-performing CTA button text and instruction snippets to reduce friction and drive action.",
                "inputs": [
                    {
                        "name": "Desired User Action",
                        "key": "cta_action",
                        "input_type": "select",
                        "description": "What action should the user take?",
                        "options": ["Sign Up", "Book Demo", "Buy Now", "Get Free Trial", "Download"],
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Funnel Stage",
                        "key": "funnel_stage",
                        "input_type": "select",
                        "description": "Stage of the user in the funnel.",
                        "options": ["Top", "Middle", "Bottom"],
                        "order": 2,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "CTA Button Text",
                        "key": "cta_text",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Different versions of button text designed to convert.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Microcopy",
                        "key": "cta_microcopy",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Short trust-building copy to place near the CTA (e.g., 'No credit card required').",
                        "is_required": True,
                        "order": 2
                    }
                ]
            },
            {
                "key": "check_ad_lp_message_match",
                "output_schema_name": "Ad-Landing Page Message Audit",
                "output_schema_description": "Analysis of message consistency between ads and landing pages with suggestions for alignment.",
                "inputs": [
                    {
                        "name": "Ad Copy",
                        "key": "ad_copy",
                        "input_type": "textarea",
                        "description": "The full ad text users see before clicking through.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Landing Page URL",
                        "key": "landing_page_url",
                        "input_type": "url",
                        "description": "The page where users land after clicking the ad.",
                        "order": 2,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Message Alignment Verdict",
                        "key": "alignment_verdict",
                        "field_type": "string",
                        "description": "Result of congruency check: Aligned, Minor Mismatch, or Major Mismatch.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Mismatch Areas",
                        "key": "mismatch_areas",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "List of sections where misalignment was found (e.g., headline, CTA).",
                        "is_required": False,
                        "order": 2
                    },
                    {
                        "name": "Fix Recommendations",
                        "key": "fix_recommendations",
                        "field_type": "string",
                        "description": "How to resolve mismatches between ad and landing page.",
                        "is_required": True,
                        "order": 3
                    }
                ]
            },
            {
                "key": "explain_offer_price_guarantees",
                "output_schema_name": "Offer Clarity and Guarantee Block",
                "output_schema_description": "Copy block clearly explaining what users get, what it costs, and guarantee terms to boost conversions.",
                "inputs": [
                    {
                        "name": "Offer Name",
                        "key": "offer_name",
                        "input_type": "text",
                        "description": "The product, plan, or service name.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "What’s Included",
                        "key": "included_features",
                        "input_type": "textarea",
                        "description": "List of benefits or items included in the offer.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Pricing Model",
                        "key": "pricing_model",
                        "input_type": "text",
                        "description": "How pricing works (e.g., monthly, one-time fee).",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Guarantee Type",
                        "key": "guarantee_type",
                        "input_type": "text",
                        "description": "What confidence-boosting promise you offer (e.g., 30-day money-back guarantee).",
                        "order": 4,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Offer Summary",
                        "key": "offer_summary",
                        "field_type": "string",
                        "description": "Short explanation of the full offer value.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Pricing Clarity Text",
                        "key": "pricing_text",
                        "field_type": "string",
                        "description": "Simple, persuasive breakdown of cost.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Guarantee Text",
                        "key": "guarantee_text",
                        "field_type": "string",
                        "description": "Confidence-boosting statement related to the guarantee.",
                        "is_required": False,
                        "order": 3
                    }
                ]
            },
            {
                "key": "shorten_text_mobile",
                "output_schema_name": "Mobile-Optimized Copy",
                "output_schema_description": "Shortened, scannable version of the original copy tailored for mobile screens.",
                "inputs": [
                    {
                        "name": "Original Landing Page Copy",
                        "key": "original_copy",
                        "input_type": "textarea",
                        "description": "Full desktop version of the landing page text to be optimized.",
                        "order": 1,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Condensed Mobile Version",
                        "key": "condensed_copy",
                        "field_type": "string",
                        "description": "Shortened copy with clear line breaks and mobile-friendly formatting.",
                        "is_required": True,
                        "order": 1
                    }
                ]
            },
            {
                "key": "use_competitor_lp_examples",
                "output_schema_name": "Competitor-Inspired Copy Ideas",
                "output_schema_description": "New landing page copy sections inspired by high-performing competitor pages and adapted to your brand.",
                "inputs": [
                    {
                        "name": "Competitor Page URLs",
                        "key": "competitor_urls",
                        "input_type": "textarea",
                        "description": "List of competitor landing page links for reference.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Your Product/Service Summary",
                        "key": "your_offer_summary",
                        "input_type": "textarea",
                        "description": "1–2 sentence summary of your product/service for context.",
                        "order": 2,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Copy Idea 1",
                        "key": "copy_idea_1",
                        "field_type": "string",
                        "description": "Adapted copy suggestion based on a competitor example.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Copy Idea 2",
                        "key": "copy_idea_2",
                        "field_type": "string",
                        "description": "Another original idea derived from a competitor reference.",
                        "is_required": True,
                        "order": 2
                    }
                ]
            },
            # Social Content Planner
            {
                "key": "plan_monthly_posts",
                "output_schema_name": "Monthly Content Calendar",
                "output_schema_description": "A comprehensive 15-20 post monthly calendar strategically mapped to awareness, nurture, and conversion goals across platforms.",
                "inputs": [
                    {
                        "name": "Brand Name",
                        "key": "brand_name",
                        "input_type": "text",
                        "description": "The name of your brand or company for consistent messaging.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Platforms",
                        "key": "target_platforms",
                        "input_type": "select",
                        "description": "Select all platforms where you'll be posting content.",
                        "options": [
                            {"value": "instagram", "label": "Instagram"},
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "tiktok", "label": "TikTok"},
                            {"value": "twitter", "label": "Twitter/X"}
                        ],
                        "order": 2,
                        "is_required": True,
                        "multiple": True
                    },
                    {
                        "name": "Monthly Theme",
                        "key": "monthly_theme",
                        "input_type": "text",
                        "description": "Central theme or campaign focus for the month (e.g., 'Q4 Product Launch', 'Customer Success Stories').",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Awareness Stage Topics",
                        "key": "awareness_topics",
                        "input_type": "textarea",
                        "description": "List topics that attract new audiences and introduce your brand (comma-separated).",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Nurture Stage Topics",
                        "key": "nurture_topics",
                        "input_type": "textarea",
                        "description": "List educational content topics that build trust and authority (comma-separated).",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Conversion Goals",
                        "key": "conversion_goals",
                        "input_type": "textarea",
                        "description": "Specific conversion actions you want to drive (e.g., demo bookings, free trial signups, webinar registrations).",
                        "order": 6,
                        "is_required": True
                    },
                    {
                        "name": "Content Pillars",
                        "key": "content_pillars",
                        "input_type": "textarea",
                        "description": "Your 3-5 main content categories or pillars (e.g., 'Industry Insights, Product Tips, Customer Stories').",
                        "order": 7,
                        "is_required": True
                    },
                    {
                        "name": "Key Dates & Events",
                        "key": "key_dates",
                        "input_type": "textarea",
                        "description": "Important dates to plan around (product launches, holidays, industry events) - format: 'Date: Event'.",
                        "order": 8,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Weekly Post Schedule",
                        "key": "weekly_post_schedule",
                        "field_type": "string",
                        "description": "Detailed breakdown of posts by week, including platform, format, and funnel stage.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Platform-Specific Calendar",
                        "key": "platform_calendar",
                        "field_type": "string",
                        "description": "Individual posting schedules optimized for each platform's best times and formats.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Content Format Mix",
                        "key": "content_format_mix",
                        "field_type": "string",
                        "description": "Recommended distribution of post formats (reels, carousels, stories, etc.) per platform.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Funnel Stage Distribution",
                        "key": "funnel_distribution",
                        "field_type": "string",
                        "description": "Percentage breakdown of awareness vs nurture vs conversion content.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Key Performance Indicators",
                        "key": "kpis",
                        "field_type": "string",
                        "description": "Specific metrics to track for each funnel stage and platform.",
                        "is_required": True,
                        "order": 5
                    }
                ]
            },
            {
                "key": "write_engagement_captions",
                "output_schema_name": "High-Engagement Caption Templates",
                "output_schema_description": "Platform-optimized captions designed to maximize saves, shares, and meaningful interactions through psychological triggers.",
                "inputs": [
                    {
                        "name": "Post Topic",
                        "key": "post_topic",
                        "input_type": "text",
                        "description": "Main subject or theme of the post (e.g., '5 Email Marketing Mistakes').",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Platform",
                        "key": "target_platform",
                        "input_type": "select",
                        "description": "Platform where this caption will be posted.",
                        "options": [
                            {"value": "instagram", "label": "Instagram"},
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "tiktok", "label": "TikTok"},
                            {"value": "twitter", "label": "Twitter/X"}
                        ],
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Post Format",
                        "key": "post_format",
                        "input_type": "select",
                        "description": "Type of content this caption accompanies.",
                        "options": [
                            {"value": "single_image", "label": "Single Image"},
                            {"value": "carousel", "label": "Carousel"},
                            {"value": "reel", "label": "Reel/Video"},
                            {"value": "story", "label": "Story"},
                            {"value": "text_only", "label": "Text Only"}
                        ],
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience",
                        "key": "target_audience",
                        "input_type": "text",
                        "description": "Specific audience segment (e.g., 'B2B SaaS marketers', 'E-commerce founders').",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Desired Action",
                        "key": "desired_action",
                        "input_type": "select",
                        "description": "Primary engagement goal for this post.",
                        "options": [
                            {"value": "save", "label": "Save for Later"},
                            {"value": "share", "label": "Share/Repost"},
                            {"value": "comment", "label": "Comment/Reply"},
                            {"value": "dm", "label": "Send DM"},
                            {"value": "click_link", "label": "Click Link"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Brand Voice",
                        "key": "brand_voice",
                        "input_type": "select",
                        "description": "Tone and personality for the caption.",
                        "options": [
                            {"value": "professional", "label": "Professional & Authoritative"},
                            {"value": "friendly", "label": "Friendly & Conversational"},
                            {"value": "bold", "label": "Bold & Provocative"},
                            {"value": "educational", "label": "Educational & Helpful"},
                            {"value": "inspirational", "label": "Inspirational & Motivating"}
                        ],
                        "order": 6,
                        "is_required": True
                    },
                    {
                        "name": "Key Message Points",
                        "key": "key_points",
                        "input_type": "textarea",
                        "description": "Main points to cover in the caption (bullet points or comma-separated).",
                        "order": 7,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Primary Caption",
                        "key": "primary_caption",
                        "field_type": "string",
                        "description": "Main caption optimized for engagement with platform-specific formatting.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Hook Variations",
                        "key": "hook_variations",
                        "field_type": "list of strings",
                        "description": "3-5 alternative opening lines to test for maximum scroll-stopping power.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Engagement Triggers",
                        "key": "engagement_triggers",
                        "field_type": "string",
                        "description": "Specific psychological triggers used and why they work for this audience.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Hashtag Strategy",
                        "key": "hashtag_strategy",
                        "field_type": "string",
                        "description": "Platform-optimized hashtag recommendations with reach potential.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "A/B Test Suggestions",
                        "key": "ab_test_suggestions",
                        "field_type": "string",
                        "description": "Elements to test for improving engagement rates.",
                        "is_required": True,
                        "order": 5
                    }
                ]
            },
            {
                "key": "add_traffic_ctas",
                "output_schema_name": "Traffic-Driving CTA Framework",
                "output_schema_description": "Strategic calls-to-action optimized for each platform to convert social engagement into website traffic and conversions.",
                "inputs": [
                    {
                        "name": "Content Type",
                        "key": "content_type",
                        "input_type": "select",
                        "description": "Type of content you're adding CTAs to.",
                        "options": [
                            {"value": "carousel", "label": "Carousel Post"},
                            {"value": "reel", "label": "Reel/Short Video"},
                            {"value": "story", "label": "Story"},
                            {"value": "live_video", "label": "Live Video"},
                            {"value": "long_form_video", "label": "Long Form Video"}
                        ],
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target URL",
                        "key": "target_url",
                        "input_type": "url",
                        "description": "Landing page, blog post, or signup page you want to drive traffic to.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Platform",
                        "key": "platform",
                        "input_type": "select",
                        "description": "Platform where this content will be posted.",
                        "options": [
                            {"value": "instagram", "label": "Instagram"},
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "tiktok", "label": "TikTok"},
                            {"value": "youtube", "label": "YouTube"}
                        ],
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Content Topic",
                        "key": "content_topic",
                        "input_type": "text",
                        "description": "Main topic of the content piece (e.g., 'Email automation tips').",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Conversion Goal",
                        "key": "conversion_goal",
                        "input_type": "select",
                        "description": "What you want visitors to do on the landing page.",
                        "options": [
                            {"value": "read_blog", "label": "Read Blog Post"},
                            {"value": "download_resource", "label": "Download Resource"},
                            {"value": "book_demo", "label": "Book Demo"},
                            {"value": "start_trial", "label": "Start Free Trial"},
                            {"value": "join_waitlist", "label": "Join Waitlist"},
                            {"value": "purchase", "label": "Make Purchase"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Audience Temperature",
                        "key": "audience_temp",
                        "input_type": "select",
                        "description": "How familiar is this audience with your brand?",
                        "options": [
                            {"value": "cold", "label": "Cold - New to Brand"},
                            {"value": "warm", "label": "Warm - Knows Brand"},
                            {"value": "hot", "label": "Hot - Engaged Followers"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Primary CTA Copy",
                        "key": "primary_cta",
                        "field_type": "string",
                        "description": "Main call-to-action text optimized for the platform and format.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "CTA Placement Strategy",
                        "key": "cta_placement",
                        "field_type": "string",
                        "description": "Where and when to place CTAs within the content for maximum clicks.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Supporting Microcopy",
                        "key": "supporting_copy",
                        "field_type": "string",
                        "description": "Additional text to build urgency and value around the CTA.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Visual CTA Elements",
                        "key": "visual_elements",
                        "field_type": "string",
                        "description": "Design recommendations for CTA buttons, stickers, or graphics.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Tracking Parameters",
                        "key": "tracking_params",
                        "field_type": "string",
                        "description": "UTM parameters and tracking setup for measuring CTA performance.",
                        "is_required": True,
                        "order": 5
                    }
                ]
            },
            {
                "key": "apply_audience_trends",
                "output_schema_name": "Trend Application Strategy",
                "output_schema_description": "Customized trend formats that align with brand voice while maximizing organic reach through timely, relevant content.",
                "inputs": [
                    {
                        "name": "Current Trends",
                        "key": "current_trends",
                        "input_type": "textarea",
                        "description": "List trending formats, sounds, or templates you've spotted (include platform).",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Brand Values",
                        "key": "brand_values",
                        "input_type": "textarea",
                        "description": "Core brand values and messaging pillars to maintain while trend-jacking.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Target Audience Demographics",
                        "key": "audience_demographics",
                        "input_type": "text",
                        "description": "Age range, interests, and characteristics of your core audience.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Content Boundaries",
                        "key": "content_boundaries",
                        "input_type": "textarea",
                        "description": "Topics or formats to avoid (e.g., controversial topics, competitor mentions).",
                        "order": 4,
                        "is_required": False
                    },
                    {
                        "name": "Previous Viral Content",
                        "key": "previous_viral",
                        "input_type": "textarea",
                        "description": "Examples of your past content that performed exceptionally well.",
                        "order": 5,
                        "is_required": False
                    },
                    {
                        "name": "Trend Adaptation Speed",
                        "key": "adaptation_speed",
                        "input_type": "select",
                        "description": "How quickly can you create and publish trend-based content?",
                        "options": [
                            {"value": "same_day", "label": "Same Day"},
                            {"value": "next_day", "label": "Next Day"},
                            {"value": "within_week", "label": "Within a Week"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Trend Adaptation Ideas",
                        "key": "trend_adaptations",
                        "field_type": "list of strings",
                        "description": "5-7 specific ways to apply current trends to your brand content.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Content Scripts",
                        "key": "content_scripts",
                        "field_type": "string",
                        "description": "Ready-to-use scripts or content outlines for top trend opportunities.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Trend Timing Strategy",
                        "key": "timing_strategy",
                        "field_type": "string",
                        "description": "When to jump on trends vs. when to skip them based on lifecycle.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Brand Safety Checklist",
                        "key": "brand_safety",
                        "field_type": "string",
                        "description": "Quick checks to ensure trend content aligns with brand guidelines.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Trend Performance Metrics",
                        "key": "performance_metrics",
                        "field_type": "string",
                        "description": "KPIs to track for trend-based content vs. regular content.",
                        "is_required": True,
                        "order": 5
                    }
                ]
            },
            {
                "key": "post_pain_point_questions",
                "output_schema_name": "Pain Point Discovery Framework",
                "output_schema_description": "Strategic social prompts designed to uncover buyer challenges and generate qualified engagement for demand generation.",
                "inputs": [
                    {
                        "name": "Target Buyer Persona",
                        "key": "buyer_persona",
                        "input_type": "text",
                        "description": "Specific role or persona you're targeting (e.g., 'B2B Marketing Directors').",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Product/Service Category",
                        "key": "product_category",
                        "input_type": "text",
                        "description": "What you sell that solves their problems (e.g., 'Marketing automation software').",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Known Pain Points",
                        "key": "known_pain_points",
                        "input_type": "textarea",
                        "description": "Current challenges you know your audience faces (comma-separated).",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Discovery Goals",
                        "key": "discovery_goals",
                        "input_type": "select",
                        "description": "What you want to learn from audience responses.",
                        "options": [
                            {"value": "new_pain_points", "label": "Discover New Pain Points"},
                            {"value": "validate_assumptions", "label": "Validate Current Assumptions"},
                            {"value": "buying_objections", "label": "Uncover Buying Objections"},
                            {"value": "feature_requests", "label": "Gather Feature Requests"},
                            {"value": "competitor_intel", "label": "Learn About Competitors"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Engagement Platform",
                        "key": "engagement_platform",
                        "input_type": "select",
                        "description": "Where you'll post these discovery questions.",
                        "options": [
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "twitter", "label": "Twitter/X"},
                            {"value": "facebook_groups", "label": "Facebook Groups"},
                            {"value": "instagram", "label": "Instagram"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Follow-up Strategy",
                        "key": "followup_strategy",
                        "input_type": "select",
                        "description": "How you'll engage with respondents.",
                        "options": [
                            {"value": "public_reply", "label": "Public Reply Only"},
                            {"value": "dm_followup", "label": "DM Follow-up"},
                            {"value": "email_capture", "label": "Move to Email"},
                            {"value": "calendar_link", "label": "Book Discovery Call"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Discovery Questions",
                        "key": "discovery_questions",
                        "field_type": "list of strings",
                        "description": "10-15 engaging questions designed to surface buyer challenges.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Question Frameworks",
                        "key": "question_frameworks",
                        "field_type": "string",
                        "description": "Templates for creating future pain point questions.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Response Handling Guide",
                        "key": "response_guide",
                        "field_type": "string",
                        "description": "How to respond to different types of comments to maximize value.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Lead Qualification Criteria",
                        "key": "qualification_criteria",
                        "field_type": "string",
                        "description": "How to identify high-intent prospects from responses.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Insight Documentation Template",
                        "key": "insight_template",
                        "field_type": "string",
                        "description": "Framework for capturing and organizing discovered pain points.",
                        "is_required": True,
                        "order": 5
                    }
                ]
            },
            {
                "key": "optimize_social_performance",
                "output_schema_name": "Performance Optimization Playbook",
                "output_schema_description": "Data-driven framework for killing underperforming content and scaling winners based on clear performance metrics.",
                "inputs": [
                    {
                        "name": "Performance Data Export",
                        "key": "performance_data",
                        "input_type": "file",
                        "description": "CSV export of last 30 days social media performance data.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Primary Success Metric",
                        "key": "success_metric",
                        "input_type": "select",
                        "description": "Main KPI for determining content success.",
                        "options": [
                            {"value": "engagement_rate", "label": "Engagement Rate"},
                            {"value": "reach", "label": "Reach/Impressions"},
                            {"value": "link_clicks", "label": "Link Clicks"},
                            {"value": "conversions", "label": "Conversions"},
                            {"value": "follower_growth", "label": "Follower Growth"}
                        ],
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Content Categories",
                        "key": "content_categories",
                        "input_type": "textarea",
                        "description": "List your content categories/pillars for performance comparison.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Budget for Promotion",
                        "key": "promotion_budget",
                        "input_type": "number",
                        "description": "Weekly budget available for boosting top performers (in USD).",
                        "order": 4,
                        "is_required": False
                    },
                    {
                        "name": "Team Capacity",
                        "key": "team_capacity",
                        "input_type": "select",
                        "description": "How many posts can your team create/repurpose weekly?",
                        "options": [
                            {"value": "1-5", "label": "1-5 posts"},
                            {"value": "6-10", "label": "6-10 posts"},
                            {"value": "11-20", "label": "11-20 posts"},
                            {"value": "20+", "label": "20+ posts"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Performance Review Frequency",
                        "key": "review_frequency",
                        "input_type": "select",
                        "description": "How often do you want to review and optimize?",
                        "options": [
                            {"value": "weekly", "label": "Weekly"},
                            {"value": "biweekly", "label": "Bi-weekly"},
                            {"value": "monthly", "label": "Monthly"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Kill List",
                        "key": "kill_list",
                        "field_type": "list of strings",
                        "description": "Content types/topics to stop creating with performance rationale.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Scale List",
                        "key": "scale_list",
                        "field_type": "list of strings",
                        "description": "Top 10% content to repurpose, repost, or expand on.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Repurposing Strategy",
                        "key": "repurposing_strategy",
                        "field_type": "string",
                        "description": "Specific ways to remix and redistribute winning content.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Performance Patterns",
                        "key": "performance_patterns",
                        "field_type": "string",
                        "description": "Key insights about what drives success for your audience.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Optimization Roadmap",
                        "key": "optimization_roadmap",
                        "field_type": "string",
                        "description": "4-week plan for implementing performance improvements.",
                        "is_required": True,
                        "order": 5
                    }
                ]
            },
            # Customer Persona Builder
            {
                "key": "create_data_driven_personas",
                "output_schema_name": "Data-Driven Buyer Personas",
                "output_schema_description": "3-5 comprehensive buyer personas combining your business context with market intelligence and behavioral patterns.",
                "inputs": [
                    {
                        "name": "Company Description",
                        "key": "company_description",
                        "input_type": "textarea",
                        "description": "Describe your company, product/service, and unique value proposition.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Market",
                        "key": "target_market",
                        "input_type": "text",
                        "description": "Primary market segment (e.g., 'B2B SaaS for Healthcare', 'E-commerce Tools').",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Customer Success Stories",
                        "key": "success_stories",
                        "input_type": "textarea",
                        "description": "2-3 examples of your best customers and why they love your product.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Price Point",
                        "key": "price_point",
                        "input_type": "text",
                        "description": "Your pricing model and average deal size (e.g., '$500-5000/month').",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Key Differentiators",
                        "key": "differentiators",
                        "input_type": "textarea",
                        "description": "What makes you different from competitors (features, approach, philosophy).",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Geographic Focus",
                        "key": "geographic_focus",
                        "input_type": "select",
                        "description": "Primary geographic market for these personas.",
                        "options": [
                            {"value": "north_america", "label": "North America"},
                            {"value": "europe", "label": "Europe"},
                            {"value": "asia_pacific", "label": "Asia Pacific"},
                            {"value": "global", "label": "Global"},
                            {"value": "specific_country", "label": "Specific Country/Region"}
                        ],
                        "order": 6,
                        "is_required": True
                    },
                    {
                        "name": "Customer Insights (Optional)",
                        "key": "customer_insights",
                        "input_type": "file",
                        "description": "Any customer data, surveys, or analytics you'd like to incorporate.",
                        "order": 7,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Persona Profiles",
                        "key": "persona_profiles",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Detailed profiles including demographics, role, company characteristics, and decision-making style.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Day-in-the-Life Scenarios",
                        "key": "daily_scenarios",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Typical workday challenges and workflows for each persona.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Jobs-to-be-Done Framework",
                        "key": "jobs_to_be_done",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Functional, emotional, and social jobs each persona is trying to accomplish.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Buying Committee Map",
                        "key": "buying_committee",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Who's involved in the purchase decision and their influence levels.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Content Preferences",
                        "key": "content_preferences",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Preferred content types, channels, and information sources for each persona.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Messaging Strategy",
                        "key": "messaging_strategy",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Tailored value propositions and key messages that resonate with each persona.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "find_purchase_pain_points",
                "output_schema_name": "Purchase-Triggering Pain Points",
                "output_schema_description": "AI-discovered pain points that drive purchases in your market, with quantified business impact.",
                "inputs": [
                    {
                        "name": "Product Category",
                        "key": "product_category",
                        "input_type": "text",
                        "description": "What type of solution you provide (e.g., 'Project Management Software').",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Target Customer Profile",
                        "key": "target_profile",
                        "input_type": "textarea",
                        "description": "Describe your ideal customer (role, company size, industry).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Current Market Challenges",
                        "key": "market_challenges",
                        "input_type": "textarea",
                        "description": "Major trends or disruptions affecting your customers' industries.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Alternative Solutions",
                        "key": "alternatives",
                        "input_type": "textarea",
                        "description": "What customers currently use instead of your solution (including manual processes).",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Transformation Promise",
                        "key": "transformation",
                        "input_type": "textarea",
                        "description": "The 'before and after' transformation your product enables.",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Industry Vertical",
                        "key": "industry_vertical",
                        "input_type": "select",
                        "description": "Primary industry focus for pain point analysis.",
                        "options": [
                            {"value": "technology", "label": "Technology"},
                            {"value": "healthcare", "label": "Healthcare"},
                            {"value": "finance", "label": "Finance"},
                            {"value": "retail", "label": "Retail/E-commerce"},
                            {"value": "manufacturing", "label": "Manufacturing"},
                            {"value": "services", "label": "Professional Services"},
                            {"value": "education", "label": "Education"},
                            {"value": "multiple", "label": "Multiple Industries"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Core Pain Points",
                        "key": "core_pain_points",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Top 5 pain points ranked by urgency and impact on purchase decisions.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Pain Point Equations",
                        "key": "pain_equations",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Formulas showing the real cost of each pain point (time + money + opportunity).",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Trigger Events",
                        "key": "trigger_events",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Specific events or thresholds that make pain unbearable enough to buy.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Emotional Drivers",
                        "key": "emotional_drivers",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Psychological and emotional factors that amplify each pain point.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Solution Positioning",
                        "key": "solution_positioning",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "How to position your product as the ideal pain reliever.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Competitive Advantage Map",
                        "key": "competitive_advantage",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Which pain points you solve better than alternatives.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "map_objections_by_funnel",
                "output_schema_name": "Funnel Stage Objection Map",
                "output_schema_description": "AI-generated objection patterns for each funnel stage with psychological insights and conversion tactics.",
                "inputs": [
                    {
                        "name": "Business Model",
                        "key": "business_model",
                        "input_type": "text",
                        "description": "Your business model (e.g., 'B2B SaaS', 'Consulting', 'E-commerce').",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Average Deal Size",
                        "key": "deal_size",
                        "input_type": "select",
                        "description": "Typical transaction or contract value.",
                        "options": [
                            {"value": "micro", "label": "Micro ($0-100)"},
                            {"value": "small", "label": "Small ($100-1K)"},
                            {"value": "medium", "label": "Medium ($1K-10K)"},
                            {"value": "large", "label": "Large ($10K-100K)"},
                            {"value": "enterprise", "label": "Enterprise ($100K+)"}
                        ],
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Sales Cycle Length",
                        "key": "sales_cycle",
                        "input_type": "select",
                        "description": "Typical time from first touch to close.",
                        "options": [
                            {"value": "instant", "label": "Instant (Same day)"},
                            {"value": "short", "label": "Short (1-7 days)"},
                            {"value": "medium", "label": "Medium (1-4 weeks)"},
                            {"value": "long", "label": "Long (1-3 months)"},
                            {"value": "enterprise", "label": "Enterprise (3+ months)"}
                        ],
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Value Proposition",
                        "key": "value_prop",
                        "input_type": "textarea",
                        "description": "Your core value proposition in 2-3 sentences.",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Biggest Competitor",
                        "key": "main_competitor",
                        "input_type": "text",
                        "description": "Your main competitor or the status quo you're replacing.",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Trust Builders",
                        "key": "trust_builders",
                        "input_type": "textarea",
                        "description": "Your credibility factors (clients, awards, certifications, years in business).",
                        "order": 6,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "TOFU Objection Patterns",
                        "key": "tofu_patterns",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Early-stage skepticism patterns and awareness barriers with response strategies.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "MOFU Decision Blockers",
                        "key": "mofu_blockers",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Comparison and evaluation stage concerns with competitive positioning.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "BOFU Risk Reducers",
                        "key": "bofu_reducers",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Final stage fears and risk mitigation strategies.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Objection Psychology Map",
                        "key": "psychology_map",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Underlying psychological drivers behind each objection type.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Conversion Conversation Flows",
                        "key": "conversation_flows",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Natural dialogue patterns that transform objections into interest.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Content Strategy Gaps",
                        "key": "content_gaps",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Missing content pieces needed to preemptively address objections.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "update_personas_sales_insights",
                "output_schema_name": "Weekly Persona Intelligence Update",
                "output_schema_description": "AI-powered persona refinements based on market signals and behavioral patterns.",
                "inputs": [
                    {
                        "name": "Current Personas Summary",
                        "key": "current_personas",
                        "input_type": "textarea",
                        "description": "Brief description of your existing personas (names and key traits).",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "This Week's Observations",
                        "key": "weekly_observations",
                        "input_type": "textarea",
                        "description": "Key customer interactions, feedback, or patterns noticed this week.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Market Changes",
                        "key": "market_changes",
                        "input_type": "textarea",
                        "description": "Any industry news, competitor moves, or trends affecting your customers.",
                        "order": 3,
                        "is_required": False
                    },
                    {
                        "name": "Surprising Discoveries",
                        "key": "surprises",
                        "input_type": "textarea",
                        "description": "Unexpected customer behaviors, use cases, or feedback.",
                        "order": 4,
                        "is_required": False
                    },
                    {
                        "name": "Performance Metrics",
                        "key": "performance_metrics",
                        "input_type": "textarea",
                        "description": "Any notable changes in conversion rates, engagement, or sales velocity.",
                        "order": 5,
                        "is_required": False
                    },
                    {
                        "name": "Update Focus Area",
                        "key": "focus_area",
                        "input_type": "select",
                        "description": "What aspect of personas needs most refinement.",
                        "options": [
                            {"value": "behaviors", "label": "Behavioral Patterns"},
                            {"value": "motivations", "label": "Goals & Motivations"},
                            {"value": "channels", "label": "Channel Preferences"},
                            {"value": "messaging", "label": "Messaging Effectiveness"},
                            {"value": "comprehensive", "label": "Full Persona Review"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Persona Evolution Summary",
                        "key": "evolution_summary",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "How each persona is evolving based on new intelligence.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Behavioral Shifts",
                        "key": "behavioral_shifts",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "New or changing behaviors observed in each persona segment.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Messaging Refinements",
                        "key": "messaging_updates",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Updated messaging angles based on what's resonating.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Channel Intelligence",
                        "key": "channel_intelligence",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Where each persona is most active and engaged right now.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Predictive Insights",
                        "key": "predictive_insights",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Emerging trends and future behaviors to prepare for.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Action Items",
                        "key": "action_items",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Specific campaign or strategy adjustments to implement this week.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "build_negative_personas",
                "output_schema_name": "Negative Persona Exclusion Framework",
                "output_schema_description": "AI-identified unprofitable customer patterns with strategic exclusion recommendations.",
                "inputs": [
                    {
                        "name": "Business Type",
                        "key": "business_type",
                        "input_type": "text",
                        "description": "Your business model and primary offering.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Ideal Customer Profile",
                        "key": "ideal_profile",
                        "input_type": "textarea",
                        "description": "Characteristics of your most successful, profitable customers.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Problem Customer Patterns",
                        "key": "problem_patterns",
                        "input_type": "textarea",
                        "description": "Common traits of difficult, unprofitable, or churning customers.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Resource Constraints",
                        "key": "resource_constraints",
                        "input_type": "textarea",
                        "description": "What you can't provide (support level, customization, features).",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Profitability Threshold",
                        "key": "profit_threshold",
                        "input_type": "text",
                        "description": "Minimum revenue or engagement level to be profitable.",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Support Capacity",
                        "key": "support_capacity",
                        "input_type": "select",
                        "description": "Your customer support model.",
                        "options": [
                            {"value": "self_service", "label": "Self-Service Only"},
                            {"value": "basic", "label": "Basic Support"},
                            {"value": "standard", "label": "Standard Support"},
                            {"value": "premium", "label": "Premium Support"},
                            {"value": "white_glove", "label": "White Glove Service"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Negative Persona Archetypes",
                        "key": "negative_archetypes",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "2-3 detailed profiles of customer types to actively avoid.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Red Flag Indicators",
                        "key": "red_flags",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Early warning signs during sales or onboarding.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Cost Impact Analysis",
                        "key": "cost_analysis",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Hidden costs and resource drains from serving these segments.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Qualification Questions",
                        "key": "qualification_questions",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Strategic questions to identify poor-fit prospects early.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Polite Rejection Scripts",
                        "key": "rejection_scripts",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Professional ways to redirect poor-fit prospects.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Strategic Benefits",
                        "key": "strategic_benefits",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "How excluding these segments improves overall business health.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "export_audience_tags",
                "output_schema_name": "Campaign-Ready Audience Segments",
                "output_schema_description": "Platform-optimized audience targeting parameters based on persona intelligence.",
                "inputs": [
                    {
                        "name": "Persona Names",
                        "key": "persona_names",
                        "input_type": "textarea",
                        "description": "List your persona names and one-line descriptions.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Campaign Platforms",
                        "key": "campaign_platforms",
                        "input_type": "select",
                        "description": "Where you'll run campaigns.",
                        "options": [
                            {"value": "google_ads", "label": "Google Ads"},
                            {"value": "facebook", "label": "Facebook/Instagram"},
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "twitter", "label": "Twitter/X"},
                            {"value": "tiktok", "label": "TikTok"},
                            {"value": "multiple", "label": "Multiple Platforms"}
                        ],
                        "order": 2,
                        "is_required": True,
                        "multiple": True
                    },
                    {
                        "name": "Campaign Objective",
                        "key": "campaign_objective",
                        "input_type": "select",
                        "description": "Primary goal for these audiences.",
                        "options": [
                            {"value": "awareness", "label": "Brand Awareness"},
                            {"value": "consideration", "label": "Consideration/Traffic"},
                            {"value": "conversions", "label": "Conversions/Sales"},
                            {"value": "retargeting", "label": "Retargeting"},
                            {"value": "lookalike", "label": "Lookalike Expansion"}
                        ],
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Industry Focus",
                        "key": "industry_focus",
                        "input_type": "text",
                        "description": "Target industries or verticals.",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Company Characteristics",
                        "key": "company_chars",
                        "input_type": "textarea",
                        "description": "Target company size, revenue, growth stage (if B2B).",
                        "order": 5,
                        "is_required": False
                    },
                    {
                        "name": "Budget Range",
                        "key": "budget_range",
                        "input_type": "select",
                        "description": "Monthly ad spend for these audiences.",
                        "options": [
                            {"value": "small", "label": "Small ($500-2K)"},
                            {"value": "medium", "label": "Medium ($2K-10K)"},
                            {"value": "large", "label": "Large ($10K-50K)"},
                            {"value": "enterprise", "label": "Enterprise ($50K+)"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Platform Targeting Maps",
                        "key": "platform_targeting",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Ready-to-use targeting parameters for each platform.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Audience Sizing Estimates",
                        "key": "audience_sizes",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Expected reach and CPM estimates for each segment.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Interest & Behavior Targets",
                        "key": "interest_targets",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Specific interests, behaviors, and affinities to target.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Exclusion Lists",
                        "key": "exclusion_lists",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Audiences and characteristics to exclude for efficiency.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Creative Recommendations",
                        "key": "creative_recs",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Ad creative themes and messages for each audience segment.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Testing Framework",
                        "key": "testing_framework",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "A/B testing strategy for optimizing audience performance.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
        
            # Content Repurpose Writer
            {
                "key": "blog_to_social_scripts",
                "output_schema_name": "Social Media Script Collection",
                "output_schema_description": "Platform-optimized scripts for LinkedIn carousels and Instagram/TikTok reels with engagement hooks and traffic-driving CTAs.",
                "inputs": [
                    {
                        "name": "Blog Post URL",
                        "key": "blog_url",
                        "input_type": "url",
                        "description": "URL of the blog post to repurpose into social content.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Blog Title & Topic",
                        "key": "blog_topic",
                        "input_type": "text",
                        "description": "Title and main topic of the blog for context.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Target Platforms",
                        "key": "target_platforms",
                        "input_type": "select",
                        "description": "Choose platforms for script optimization.",
                        "options": [
                            {"value": "linkedin_carousel", "label": "LinkedIn Carousel"},
                            {"value": "instagram_reel", "label": "Instagram Reel"},
                            {"value": "tiktok", "label": "TikTok"},
                            {"value": "youtube_shorts", "label": "YouTube Shorts"},
                            {"value": "all", "label": "All Platforms"}
                        ],
                        "order": 3,
                        "is_required": True,
                        "multiple": True
                    },
                    {
                        "name": "Primary CTA Goal",
                        "key": "cta_goal",
                        "input_type": "select",
                        "description": "Main action you want viewers to take.",
                        "options": [
                            {"value": "read_blog", "label": "Read Full Blog"},
                            {"value": "newsletter_signup", "label": "Newsletter Signup"},
                            {"value": "download_resource", "label": "Download Resource"},
                            {"value": "book_demo", "label": "Book Demo"},
                            {"value": "follow_profile", "label": "Follow for More"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Brand Voice",
                        "key": "brand_voice",
                        "input_type": "select",
                        "description": "Tone and style for the scripts.",
                        "options": [
                            {"value": "professional", "label": "Professional & Authoritative"},
                            {"value": "conversational", "label": "Conversational & Friendly"},
                            {"value": "edgy", "label": "Edgy & Bold"},
                            {"value": "educational", "label": "Educational & Helpful"},
                            {"value": "inspirational", "label": "Inspirational & Motivating"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Key Takeaways",
                        "key": "key_takeaways",
                        "input_type": "textarea",
                        "description": "3-5 main points from the blog to highlight (optional - AI will extract if blank).",
                        "order": 6,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "LinkedIn Carousel Script",
                        "key": "linkedin_script",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "10-slide carousel script with hooks, insights, and CTA slide.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Reel/TikTok Script",
                        "key": "reel_script",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "30-60 second video script with visual cues and text overlays.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Hook Variations",
                        "key": "hook_variations",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "5 different opening hooks to test for maximum engagement.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Visual Suggestions",
                        "key": "visual_suggestions",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Design elements, graphics, and visual flow recommendations.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Platform-Specific CTAs",
                        "key": "platform_ctas",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Tailored call-to-action copy for each platform.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Hashtag Strategy",
                        "key": "hashtag_strategy",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Optimized hashtags for discovery on each platform.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "slice_webinars_to_clips",
                "output_schema_name": "Webinar Clip Package",
                "output_schema_description": "High-impact video clips extracted from webinars with emotional hooks and conversion-focused overlays.",
                "inputs": [
                    {
                        "name": "Webinar Title",
                        "key": "webinar_title",
                        "input_type": "text",
                        "description": "Title and topic of the webinar.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Webinar Duration",
                        "key": "webinar_duration",
                        "input_type": "text",
                        "description": "Total length of webinar (e.g., '45 minutes').",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Key Moments",
                        "key": "key_moments",
                        "input_type": "textarea",
                        "description": "Notable timestamps or moments to prioritize (optional).",
                        "order": 3,
                        "is_required": False
                    },
                    {
                        "name": "Target Audience",
                        "key": "target_audience",
                        "input_type": "text",
                        "description": "Who should see these clips (role, industry, pain point).",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Clip Length Preference",
                        "key": "clip_length",
                        "input_type": "select",
                        "description": "Ideal length for video clips.",
                        "options": [
                            {"value": "micro", "label": "Micro (15-30 sec)"},
                            {"value": "short", "label": "Short (30-60 sec)"},
                            {"value": "medium", "label": "Medium (1-2 min)"},
                            {"value": "long", "label": "Long (2-3 min)"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Distribution Channels",
                        "key": "distribution_channels",
                        "input_type": "select",
                        "description": "Where these clips will be posted.",
                        "options": [
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "youtube", "label": "YouTube"},
                            {"value": "instagram", "label": "Instagram"},
                            {"value": "twitter", "label": "Twitter/X"},
                            {"value": "email", "label": "Email"}
                        ],
                        "order": 6,
                        "is_required": True,
                        "multiple": True
                    },
                    {
                        "name": "Webinar Transcript",
                        "key": "webinar_transcript",
                        "input_type": "file",
                        "description": "Upload transcript for AI to analyze best moments (optional).",
                        "order": 7,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Clip Concepts",
                        "key": "clip_concepts",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "5 high-impact clip ideas with timestamps and themes.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Hook Scripts",
                        "key": "hook_scripts",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Opening lines for each clip to maximize retention.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Text Overlay Copy",
                        "key": "overlay_copy",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "On-screen text suggestions for key moments.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "CTA Overlays",
                        "key": "cta_overlays",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "End-screen CTAs tailored to each clip's content.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Posting Schedule",
                        "key": "posting_schedule",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Recommended sequence and timing for clip releases.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Caption Templates",
                        "key": "caption_templates",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Platform-specific captions for each clip.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "case_studies_to_tweet_threads",
                "output_schema_name": "Twitter Thread Collection",
                "output_schema_description": "Compelling tweet threads that transform case studies into viral-worthy narratives with clear results and lessons.",
                "inputs": [
                    {
                        "name": "Case Study Title",
                        "key": "case_study_title",
                        "input_type": "text",
                        "description": "Title of the case study to convert.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Client/Project Overview",
                        "key": "project_overview",
                        "input_type": "textarea",
                        "description": "Brief description of the client, challenge, and solution.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Key Results",
                        "key": "key_results",
                        "input_type": "textarea",
                        "description": "Quantifiable outcomes and improvements achieved.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Thread Focus",
                        "key": "thread_focus",
                        "input_type": "select",
                        "description": "Primary angle for the tweet threads.",
                        "options": [
                            {"value": "problem_solution", "label": "Problem → Solution Journey"},
                            {"value": "lessons_learned", "label": "Key Lessons & Takeaways"},
                            {"value": "behind_scenes", "label": "Behind-the-Scenes Process"},
                            {"value": "results_focused", "label": "Results & ROI Focus"},
                            {"value": "mistakes_avoided", "label": "Mistakes We Avoided"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Target Persona",
                        "key": "target_persona",
                        "input_type": "text",
                        "description": "Who should relate to this story (role, industry, challenge).",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Thread CTA",
                        "key": "thread_cta",
                        "input_type": "select",
                        "description": "Action you want readers to take.",
                        "options": [
                            {"value": "read_full_case", "label": "Read Full Case Study"},
                            {"value": "book_consultation", "label": "Book Consultation"},
                            {"value": "dm_for_info", "label": "DM for More Info"},
                            {"value": "follow_updates", "label": "Follow for Updates"},
                            {"value": "share_thread", "label": "Share if Helpful"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Thread Scripts",
                        "key": "thread_scripts",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "3-5 complete tweet threads with numbered tweets.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Hook Tweets",
                        "key": "hook_tweets",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Alternative opening tweets to test engagement.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Visual Suggestions",
                        "key": "visual_suggestions",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Images, charts, or graphics to include in threads.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Quote Highlights",
                        "key": "quote_highlights",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Tweetable quotes and stats from the case study.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Engagement Tactics",
                        "key": "engagement_tactics",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Strategies to boost replies, shares, and bookmarks.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Follow-up Content",
                        "key": "followup_content",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Ideas for continuing the conversation after threads.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "podcasts_to_email_courses",
                "output_schema_name": "Email Course Sequence",
                "output_schema_description": "5-part email course that transforms podcast insights into a nurturing journey from awareness to action.",
                "inputs": [
                    {
                        "name": "Podcast Episode Title",
                        "key": "podcast_title",
                        "input_type": "text",
                        "description": "Title and topic of the podcast episode.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Episode Summary",
                        "key": "episode_summary",
                        "input_type": "textarea",
                        "description": "Key topics, insights, and takeaways from the episode.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Guest Expert Info",
                        "key": "guest_info",
                        "input_type": "text",
                        "description": "Guest name and credentials (if applicable).",
                        "order": 3,
                        "is_required": False
                    },
                    {
                        "name": "Course Theme",
                        "key": "course_theme",
                        "input_type": "text",
                        "description": "Overarching theme for the email course.",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Target Outcome",
                        "key": "target_outcome",
                        "input_type": "textarea",
                        "description": "What subscribers should achieve after completing the course.",
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Email Frequency",
                        "key": "email_frequency",
                        "input_type": "select",
                        "description": "How often to send course emails.",
                        "options": [
                            {"value": "daily", "label": "Daily (5 days)"},
                            {"value": "every_other", "label": "Every Other Day"},
                            {"value": "twice_weekly", "label": "Twice Weekly"},
                            {"value": "weekly", "label": "Weekly"}
                        ],
                        "order": 6,
                        "is_required": True
                    },
                    {
                        "name": "Final CTA",
                        "key": "final_cta",
                        "input_type": "select",
                        "description": "Ultimate action after course completion.",
                        "options": [
                            {"value": "book_call", "label": "Book Discovery Call"},
                            {"value": "start_trial", "label": "Start Free Trial"},
                            {"value": "buy_product", "label": "Purchase Product"},
                            {"value": "join_community", "label": "Join Community"},
                            {"value": "advanced_course", "label": "Advanced Course Signup"}
                        ],
                        "order": 7,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Course Curriculum",
                        "key": "course_curriculum",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "5-email course structure with titles and objectives.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Email Scripts",
                        "key": "email_scripts",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Complete email copy for all 5 course emails.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Subject Line Variants",
                        "key": "subject_lines",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "A/B test subject lines for each email.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Teaser Sequences",
                        "key": "teaser_sequences",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Pre-course emails to build anticipation.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Homework Assignments",
                        "key": "homework_assignments",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Action items to engage subscribers between emails.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Automation Setup",
                        "key": "automation_setup",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Technical setup guide for email platform automation.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "guides_to_checklists",
                "output_schema_name": "Action Checklist Package",
                "output_schema_description": "Scannable, downloadable checklists that distill complex guides into actionable steps with embedded lead capture.",
                "inputs": [
                    {
                        "name": "Guide Title",
                        "key": "guide_title",
                        "input_type": "text",
                        "description": "Title of the guide to convert to checklist.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Guide Overview",
                        "key": "guide_overview",
                        "input_type": "textarea",
                        "description": "Main topics and sections covered in the guide.",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Target User",
                        "key": "target_user",
                        "input_type": "text",
                        "description": "Who will use this checklist (role, experience level).",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Checklist Format",
                        "key": "checklist_format",
                        "input_type": "select",
                        "description": "Preferred checklist structure.",
                        "options": [
                            {"value": "sequential", "label": "Sequential Steps"},
                            {"value": "categorized", "label": "Categorized Tasks"},
                            {"value": "priority", "label": "Priority-Based"},
                            {"value": "timeline", "label": "Timeline-Based"},
                            {"value": "role_based", "label": "Role-Based"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Lead Magnet Goal",
                        "key": "lead_goal",
                        "input_type": "select",
                        "description": "Primary lead capture objective.",
                        "options": [
                            {"value": "email_signup", "label": "Email List Growth"},
                            {"value": "demo_booking", "label": "Demo Bookings"},
                            {"value": "consultation", "label": "Consultation Requests"},
                            {"value": "tool_trial", "label": "Tool/Product Trial"},
                            {"value": "community_join", "label": "Community Membership"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Branding Elements",
                        "key": "branding",
                        "input_type": "textarea",
                        "description": "Brand colors, logo placement, design preferences.",
                        "order": 6,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Checklist Content",
                        "key": "checklist_content",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Complete checklist with action items and checkboxes.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "PDF Design Brief",
                        "key": "pdf_brief",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Design specifications for PDF creation.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Markdown Version",
                        "key": "markdown_version",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Plain text markdown for easy editing and sharing.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "CTA Placements",
                        "key": "cta_placements",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Strategic CTA locations within the checklist.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Landing Page Copy",
                        "key": "landing_copy",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Copy to promote the checklist download.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Email Nurture Ideas",
                        "key": "nurture_ideas",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Follow-up email ideas for checklist downloaders.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "lp_to_social_teasers",
                "output_schema_name": "Social Teaser Campaign",
                "output_schema_description": "3-post teaser sequence that builds curiosity and drives traffic to landing pages through strategic reveals.",
                "inputs": [
                    {
                        "name": "Landing Page URL",
                        "key": "landing_page_url",
                        "input_type": "url",
                        "description": "URL of the landing page to promote.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Offer Summary",
                        "key": "offer_summary",
                        "input_type": "textarea",
                        "description": "What the landing page offers (product, service, resource).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Unique Value Props",
                        "key": "value_props",
                        "input_type": "textarea",
                        "description": "3-5 key benefits or differentiators.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Social Proof Elements",
                        "key": "social_proof",
                        "input_type": "textarea",
                        "description": "Testimonials, stats, or credibility markers to highlight.",
                        "order": 4,
                        "is_required": False
                    },
                    {
                        "name": "Campaign Urgency",
                        "key": "urgency_level",
                        "input_type": "select",
                        "description": "Level of urgency to create.",
                        "options": [
                            {"value": "high", "label": "High (Limited Time)"},
                            {"value": "medium", "label": "Medium (Exclusive Access)"},
                            {"value": "low", "label": "Low (Evergreen)"},
                            {"value": "event", "label": "Event-Based"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Target Platforms",
                        "key": "target_platforms",
                        "input_type": "select",
                        "description": "Where to post the teaser campaign.",
                        "options": [
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "instagram", "label": "Instagram"},
                            {"value": "twitter", "label": "Twitter/X"},
                            {"value": "facebook", "label": "Facebook"},
                            {"value": "all", "label": "All Platforms"}
                        ],
                        "order": 6,
                        "is_required": True,
                        "multiple": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Teaser Post Scripts",
                        "key": "teaser_scripts",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "3 progressive posts that build interest and urgency.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Visual Concepts",
                        "key": "visual_concepts",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Image/graphic ideas for each teaser post.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Posting Schedule",
                        "key": "posting_schedule",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Optimal timing and sequence for maximum impact.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Platform Variations",
                        "key": "platform_variations",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Adapted copy for each platform's best practices.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Engagement Boosters",
                        "key": "engagement_boosters",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Tactics to increase comments and shares.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Conversion Tracking",
                        "key": "conversion_tracking",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "UTM parameters and tracking setup for ROI measurement.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },

            # Competitor Monitor
            {
                "key": "find_competitor_content_gaps",
                "output_schema_name": "Content Gap Opportunities",
                "output_schema_description": "Prioritized list of content topics and keywords where competitors rank but you don't, with traffic potential and difficulty scores.",
                "inputs": [
                    {
                        "name": "Your Domain",
                        "key": "your_domain",
                        "input_type": "url",
                        "description": "Your website domain (e.g., example.com).",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Competitor Domains",
                        "key": "competitor_domains",
                        "input_type": "textarea",
                        "description": "List of competitor domains to analyze (one per line, max 5).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Content Focus Area",
                        "key": "content_focus",
                        "input_type": "text",
                        "description": "Primary topic or niche to focus the analysis on (e.g., 'email marketing').",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Minimum Traffic Threshold",
                        "key": "min_traffic",
                        "input_type": "number",
                        "description": "Minimum monthly search volume to consider (default: 100).",
                        "order": 4,
                        "is_required": False
                    },
                    {
                        "name": "Difficulty Range",
                        "key": "difficulty_range",
                        "input_type": "select",
                        "description": "Keyword difficulty level to target.",
                        "options": [
                            {"value": "easy", "label": "Easy (0-30)"},
                            {"value": "medium", "label": "Medium (31-60)"},
                            {"value": "hard", "label": "Hard (61-100)"},
                            {"value": "all", "label": "All Difficulties"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Content Type Filter",
                        "key": "content_type",
                        "input_type": "select",
                        "description": "Type of content gaps to identify.",
                        "options": [
                            {"value": "blog", "label": "Blog Posts"},
                            {"value": "guides", "label": "How-to Guides"},
                            {"value": "comparisons", "label": "Comparison Pages"},
                            {"value": "tools", "label": "Tool/Calculator Pages"},
                            {"value": "all", "label": "All Types"}
                        ],
                        "order": 6,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "High-Priority Content Gaps",
                        "key": "priority_gaps",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Top 10-15 content opportunities ranked by potential impact.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Keyword Clusters",
                        "key": "keyword_clusters",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Related keyword groups for each content gap with search volumes.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Traffic Opportunity Score",
                        "key": "traffic_scores",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Estimated monthly traffic potential for each content gap.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Content Angle Suggestions",
                        "key": "content_angles",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Unique angles to differentiate your content from competitors.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Quick Win Opportunities",
                        "key": "quick_wins",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Easy-to-rank topics you can target immediately.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Implementation Roadmap",
                        "key": "implementation_roadmap",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Prioritized 90-day content creation plan.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "steal_competitor_ads_for_inspiration",
                "output_schema_name": "Competitor Ad Intelligence",
                "output_schema_description": "Analysis of competitors' top-performing ads with actionable insights on hooks, offers, and creative strategies.",
                "inputs": [
                    {
                        "name": "Competitor Names",
                        "key": "competitor_names",
                        "input_type": "textarea",
                        "description": "List of competitor brand names to analyze (one per line).",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Ad Platforms",
                        "key": "ad_platforms",
                        "input_type": "select",
                        "description": "Which ad platforms to monitor.",
                        "options": [
                            {"value": "facebook", "label": "Facebook/Instagram"},
                            {"value": "google", "label": "Google Ads"},
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "twitter", "label": "Twitter/X"},
                            {"value": "all", "label": "All Platforms"}
                        ],
                        "order": 2,
                        "is_required": True,
                        "multiple": True
                    },
                    {
                        "name": "Campaign Type Focus",
                        "key": "campaign_focus",
                        "input_type": "select",
                        "description": "Type of campaigns to analyze.",
                        "options": [
                            {"value": "awareness", "label": "Brand Awareness"},
                            {"value": "lead_gen", "label": "Lead Generation"},
                            {"value": "conversion", "label": "Direct Conversion"},
                            {"value": "retargeting", "label": "Retargeting"},
                            {"value": "all", "label": "All Types"}
                        ],
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Industry Vertical",
                        "key": "industry",
                        "input_type": "text",
                        "description": "Your industry for contextual analysis (e.g., 'SaaS', 'E-commerce').",
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Time Period",
                        "key": "time_period",
                        "input_type": "select",
                        "description": "How far back to analyze ads.",
                        "options": [
                            {"value": "7_days", "label": "Last 7 Days"},
                            {"value": "30_days", "label": "Last 30 Days"},
                            {"value": "90_days", "label": "Last 90 Days"},
                            {"value": "6_months", "label": "Last 6 Months"}
                        ],
                        "order": 5,
                        "is_required": True
                    },
                    {
                        "name": "Your USP",
                        "key": "your_usp",
                        "input_type": "textarea",
                        "description": "Your unique selling propositions to avoid direct copying.",
                        "order": 6,
                        "is_required": False
                    }
                ],
                "outputs": [
                    {
                        "name": "Top Performing Ad Themes",
                        "key": "ad_themes",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Most successful ad themes and messaging patterns.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Hook Formulas",
                        "key": "hook_formulas",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Proven headline and hook structures that drive engagement.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Offer Analysis",
                        "key": "offer_analysis",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Breakdown of promotional offers and value propositions used.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Creative Insights",
                        "key": "creative_insights",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Visual trends, formats, and design elements that perform well.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "CTA Patterns",
                        "key": "cta_patterns",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Effective call-to-action phrases and button copy.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Adaptation Strategies",
                        "key": "adaptation_strategies",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "How to ethically adapt these insights for your campaigns.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "track_competitor_social_posts",
                "output_schema_name": "Social Media Performance Intelligence",
                "output_schema_description": "Analysis of competitors' most engaging social posts with actionable insights on content strategy and timing.",
                "inputs": [
                    {
                        "name": "Competitor Social Handles",
                        "key": "social_handles",
                        "input_type": "textarea",
                        "description": "Social media handles to track (format: @handle or URL, one per line).",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Social Platforms",
                        "key": "social_platforms",
                        "input_type": "select",
                        "description": "Which social platforms to monitor.",
                        "options": [
                            {"value": "linkedin", "label": "LinkedIn"},
                            {"value": "twitter", "label": "Twitter/X"},
                            {"value": "instagram", "label": "Instagram"},
                            {"value": "facebook", "label": "Facebook"},
                            {"value": "tiktok", "label": "TikTok"}
                        ],
                        "order": 2,
                        "is_required": True,
                        "multiple": True
                    },
                    {
                        "name": "Content Categories",
                        "key": "content_categories",
                        "input_type": "textarea",
                        "description": "Content themes to focus on (e.g., 'product updates, thought leadership').",
                        "order": 3,
                        "is_required": False
                    },
                    {
                        "name": "Engagement Metric Priority",
                        "key": "engagement_priority",
                        "input_type": "select",
                        "description": "Which metric matters most for your analysis.",
                        "options": [
                            {"value": "likes", "label": "Likes/Reactions"},
                            {"value": "comments", "label": "Comments"},
                            {"value": "shares", "label": "Shares/Reposts"},
                            {"value": "overall", "label": "Overall Engagement Rate"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Analysis Period",
                        "key": "analysis_period",
                        "input_type": "select",
                        "description": "Time frame for post analysis.",
                        "options": [
                            {"value": "1_week", "label": "Last Week"},
                            {"value": "2_weeks", "label": "Last 2 Weeks"},
                            {"value": "1_month", "label": "Last Month"},
                            {"value": "3_months", "label": "Last 3 Months"}
                        ],
                        "order": 5,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Top Performing Posts",
                        "key": "top_posts",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "10-15 highest engaging posts with engagement metrics.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Hook Formula Analysis",
                        "key": "hook_formulas",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Successful opening lines and hook patterns identified.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Optimal Posting Times",
                        "key": "posting_times",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Best days and times for engagement based on competitor data.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Content Format Trends",
                        "key": "format_trends",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Which post formats drive most engagement (carousels, videos, etc.).",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Topic Performance Map",
                        "key": "topic_performance",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Which topics and themes generate highest engagement.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Strategy Recommendations",
                        "key": "strategy_recommendations",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Actionable tactics to improve your social performance.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "alert_competitor_changes",
                "output_schema_name": "Competitive Change Alerts",
                "output_schema_description": "Bi-weekly intelligence report on competitor pricing, features, and positioning changes with strategic implications.",
                "inputs": [
                    {
                        "name": "Competitor List",
                        "key": "competitor_list",
                        "input_type": "textarea",
                        "description": "Names and websites of competitors to monitor (one per line).",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Alert Categories",
                        "key": "alert_categories",
                        "input_type": "select",
                        "description": "Types of changes to monitor.",
                        "options": [
                            {"value": "pricing", "label": "Pricing Changes"},
                            {"value": "features", "label": "New Features"},
                            {"value": "positioning", "label": "Positioning/Messaging"},
                            {"value": "partnerships", "label": "Partnerships/Integrations"},
                            {"value": "all", "label": "All Changes"}
                        ],
                        "order": 2,
                        "is_required": True,
                        "multiple": True
                    },
                    {
                        "name": "Your Product Category",
                        "key": "product_category",
                        "input_type": "text",
                        "description": "Your product/service category for contextual analysis.",
                        "order": 3,
                        "is_required": True
                    },
                    {
                        "name": "Price Sensitivity Threshold",
                        "key": "price_threshold",
                        "input_type": "select",
                        "description": "Minimum price change % to trigger alert.",
                        "options": [
                            {"value": "any", "label": "Any Change"},
                            {"value": "5", "label": "5% or More"},
                            {"value": "10", "label": "10% or More"},
                            {"value": "20", "label": "20% or More"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Alert Frequency",
                        "key": "alert_frequency",
                        "input_type": "select",
                        "description": "How often to receive alerts.",
                        "options": [
                            {"value": "weekly", "label": "Weekly"},
                            {"value": "biweekly", "label": "Bi-weekly"},
                            {"value": "monthly", "label": "Monthly"}
                        ],
                        "order": 5,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Critical Changes Summary",
                        "key": "critical_changes",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "High-priority changes requiring immediate attention.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Pricing Updates",
                        "key": "pricing_updates",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Detailed pricing changes with before/after comparison.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Feature Releases",
                        "key": "feature_releases",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "New features or capabilities launched by competitors.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Positioning Shifts",
                        "key": "positioning_shifts",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Changes in messaging, targeting, or value propositions.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Strategic Implications",
                        "key": "strategic_implications",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "What these changes mean for your competitive strategy.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Recommended Actions",
                        "key": "recommended_actions",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Specific steps to take in response to competitor changes.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "find_competitor_backlinks",
                "output_schema_name": "Backlink Gap Analysis",
                "output_schema_description": "Prioritized list of valuable backlinks competitors have with outreach templates and contact information.",
                "inputs": [
                    {
                        "name": "Your Domain",
                        "key": "your_domain",
                        "input_type": "url",
                        "description": "Your website domain for comparison.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Competitor Domains",
                        "key": "competitor_domains",
                        "input_type": "textarea",
                        "description": "Competitor domains to analyze (one per line, max 5).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Domain Authority Minimum",
                        "key": "da_minimum",
                        "input_type": "number",
                        "description": "Minimum domain authority to consider (1-100, default: 30).",
                        "order": 3,
                        "is_required": False
                    },
                    {
                        "name": "Link Type Focus",
                        "key": "link_type",
                        "input_type": "select",
                        "description": "Types of backlinks to prioritize.",
                        "options": [
                            {"value": "editorial", "label": "Editorial/Content Links"},
                            {"value": "resource", "label": "Resource Pages"},
                            {"value": "guest_posts", "label": "Guest Post Opportunities"},
                            {"value": "directories", "label": "Industry Directories"},
                            {"value": "all", "label": "All Types"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Industry Relevance",
                        "key": "industry_relevance",
                        "input_type": "select",
                        "description": "How closely related should linking sites be.",
                        "options": [
                            {"value": "exact", "label": "Exact Industry Match"},
                            {"value": "related", "label": "Related Industries"},
                            {"value": "any", "label": "Any Relevant Site"}
                        ],
                        "order": 5,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "High-Value Link Opportunities",
                        "key": "link_opportunities",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Top 20-30 backlink opportunities ranked by value.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Contact Information",
                        "key": "contact_info",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Email addresses and contact forms for outreach.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Outreach Templates",
                        "key": "outreach_templates",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Customized email templates for different link types.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Link Context Analysis",
                        "key": "link_context",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "How competitors earned these links and replication strategies.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Quick Win Links",
                        "key": "quick_wins",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Easy-to-acquire links you can pursue immediately.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "Outreach Priority Plan",
                        "key": "priority_plan",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "30-day outreach roadmap with success metrics.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },
            {
                "key": "flag_competitor_beating_keywords",
                "output_schema_name": "Keyword Ranking Recovery Plan",
                "output_schema_description": "Prioritized list of keywords where competitors outrank you with specific optimization strategies.",
                "inputs": [
                    {
                        "name": "Your Domain",
                        "key": "your_domain",
                        "input_type": "url",
                        "description": "Your website domain.",
                        "order": 1,
                        "is_required": True
                    },
                    {
                        "name": "Primary Competitors",
                        "key": "primary_competitors",
                        "input_type": "textarea",
                        "description": "Main competitor domains to compare against (one per line).",
                        "order": 2,
                        "is_required": True
                    },
                    {
                        "name": "Keyword Categories",
                        "key": "keyword_categories",
                        "input_type": "textarea",
                        "description": "Types of keywords to analyze (e.g., 'product terms, how-to queries').",
                        "order": 3,
                        "is_required": False
                    },
                    {
                        "name": "Ranking Position Range",
                        "key": "position_range",
                        "input_type": "select",
                        "description": "Your current ranking positions to focus on.",
                        "options": [
                            {"value": "2-5", "label": "Positions 2-5 (Near wins)"},
                            {"value": "6-10", "label": "Positions 6-10 (Page 1)"},
                            {"value": "11-20", "label": "Positions 11-20 (Page 2)"},
                            {"value": "21-50", "label": "Positions 21-50"},
                            {"value": "all", "label": "All Positions"}
                        ],
                        "order": 4,
                        "is_required": True
                    },
                    {
                        "name": "Traffic Priority",
                        "key": "traffic_priority",
                        "input_type": "select",
                        "description": "Minimum monthly search volume to consider.",
                        "options": [
                            {"value": "100", "label": "100+ searches/month"},
                            {"value": "500", "label": "500+ searches/month"},
                            {"value": "1000", "label": "1000+ searches/month"},
                            {"value": "5000", "label": "5000+ searches/month"}
                        ],
                        "order": 5,
                        "is_required": True
                    }
                ],
                "outputs": [
                    {
                        "name": "Priority Recovery Keywords",
                        "key": "priority_keywords",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Top 20 keywords to focus on with current/competitor rankings.",
                        "is_required": True,
                        "order": 1
                    },
                    {
                        "name": "Gap Analysis",
                        "key": "gap_analysis",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Why competitors rank higher for each keyword cluster.",
                        "is_required": True,
                        "order": 2
                    },
                    {
                        "name": "Content Optimization Tasks",
                        "key": "optimization_tasks",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Specific on-page improvements needed for each URL.",
                        "is_required": True,
                        "order": 3
                    },
                    {
                        "name": "Technical SEO Issues",
                        "key": "technical_issues",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Technical factors affecting rankings vs competitors.",
                        "is_required": True,
                        "order": 4
                    },
                    {
                        "name": "Quick Win Keywords",
                        "key": "quick_wins",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Keywords you can potentially outrank within 30 days.",
                        "is_required": True,
                        "order": 5
                    },
                    {
                        "name": "90-Day Action Plan",
                        "key": "action_plan",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Week-by-week optimization roadmap for ranking recovery.",
                        "is_required": True,
                        "order": 6
                    }
                ]
            },

            # 
            {
                "key": "set_marketing_goals",
                "output_schema_name": "SMART Marketing Goal Plan",
                "output_schema_description": (
                    "Annual or quarterly goals cascaded into channel KPIs with owners "
                    "and success metrics."
                ),
                "inputs": [
                    {
                        "name": "Company Name",
                        "key": "company_name",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Legal or brand name.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Planning Horizon",
                        "key": "planning_horizon",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "Timeframe for the goals.",
                        "options": [
                            {"value": "annual", "label": "Annual"},
                            {"value": "quarterly", "label": "Quarterly"},
                        ],
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Start Date",
                        "key": "start_date",
                        "input_type": TaskInputTypeChoices.DATETIME,
                        "description": "Goal period start.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "End Date",
                        "key": "end_date",
                        "input_type": TaskInputTypeChoices.DATETIME,
                        "description": "Goal period end.",
                        "order": 4,
                        "is_required": True,
                    },
                    {
                        "name": "Primary Business Metric",
                        "key": "primary_metric",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "North-star metric.",
                        "options": [
                            {"value": "revenue", "label": "Revenue"},
                            {"value": "mqls", "label": "MQLs"},
                            {"value": "pipeline", "label": "Pipeline"},
                            {"value": "roi", "label": "Marketing ROI"},
                        ],
                        "order": 5,
                        "is_required": True,
                    },
                    {
                        "name": "Current Metric Baseline",
                        "key": "baseline_value",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Current value.",
                        "order": 6,
                        "is_required": True,
                    },
                    {
                        "name": "Target Metric Value",
                        "key": "target_value",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Desired value.",
                        "order": 7,
                        "is_required": True,
                    },
                    {
                        "name": "Budget Ceiling (USD)",
                        "key": "budget_ceiling",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Maximum spend allowed.",
                        "order": 8,
                        "is_required": False,
                    },
                    {
                        "name": "Key Channels in Scope",
                        "key": "channels_in_scope",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Comma-separated channels.",
                        "order": 9,
                        "is_required": False,
                    },
                    {
                        "name": "Risk Appetite",
                        "key": "risk_appetite",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "Aggressiveness.",
                        "options": [
                            {"value": "low", "label": "Low"},
                            {"value": "moderate", "label": "Moderate"},
                            {"value": "high", "label": "High"},
                        ],
                        "order": 10,
                        "is_required": False,
                    },
                ],
                "outputs": [
                    {
                        "name": "Goal Summary",
                        "key": "goal_summary",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "One-paragraph overview.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "SMART Goals List",
                        "key": "smart_goals",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Each goal phrased in SMART format.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Channel KPI Map",
                        "key": "channel_kpis",
                        "field_type": TaskOutputFieldTypeChoices.DICT,
                        "description": "Channel → KPI target.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Funnel Alignment Notes",
                        "key": "funnel_notes",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "How goals align with funnel stages.",
                        "order": 4,
                        "is_required": False,
                    },
                    {
                        "name": "Owner Assignments",
                        "key": "owner_assignments",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Responsible people per goal.",
                        "order": 5,
                        "is_required": True,
                    },
                    {
                        "name": "Success Metrics",
                        "key": "success_metrics",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Quantitative metrics to track.",
                        "order": 6,
                        "is_required": True,
                    },
                    {
                        "name": "Risk & Assumptions",
                        "key": "risk_assumptions",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Key risks and assumptions.",
                        "order": 7,
                        "is_required": False,
                    },
                    {
                        "name": "Implementation Roadmap",
                        "key": "implementation_roadmap",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Phases and milestone dates.",
                        "order": 8,
                        "is_required": True,
                    },
                ],
            },

            # 2. --------------------------------------------- Allocate Budgets by ROI
            {
                "key": "allocate_budgets_by_roi",
                "output_schema_name": "ROI-Based Budget Allocation",
                "output_schema_description": (
                    "Optimized spend distribution by channel with rationale and risk profile."
                ),
                "inputs": [
                    {
                        "name": "Total Marketing Budget (USD)",
                        "key": "total_budget",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Budget to allocate.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Historical ROAS CSV",
                        "key": "roas_dataset",
                        "input_type": TaskInputTypeChoices.FILE,
                        "description": "CSV with channel, spend, revenue.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Look-back Period (Months)",
                        "key": "lookback_months",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Months of data to analyze.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Minimum ROAS Threshold",
                        "key": "min_roas",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Channels below this may be cut.",
                        "order": 4,
                        "is_required": False,
                    },
                    {
                        "name": "Growth Priorities",
                        "key": "growth_priorities",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Comma-separated priorities (e.g., brand, lead gen).",
                        "order": 5,
                        "is_required": False,
                    },
                    {
                        "name": "Risk Tolerance",
                        "key": "risk_tolerance",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "Budget aggressiveness.",
                        "options": [
                            {"value": "conservative", "label": "Conservative"},
                            {"value": "balanced", "label": "Balanced"},
                            {"value": "aggressive", "label": "Aggressive"},
                        ],
                        "order": 6,
                        "is_required": False,
                    },
                ],
                "outputs": [
                    {
                        "name": "Allocation Table",
                        "key": "allocation_table",
                        "field_type": TaskOutputFieldTypeChoices.DICT,
                        "description": "Channel → new budget & % change.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Reallocation Chart URL",
                        "key": "chart_url",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Link to chart image.",
                        "order": 2,
                        "is_required": False,
                    },
                    {
                        "name": "Rationale Summary",
                        "key": "rationale_summary",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Why the allocation makes sense.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Risk Assessment",
                        "key": "risk_assessment",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Downsides and mitigations.",
                        "order": 4,
                        "is_required": False,
                    },
                    {
                        "name": "Expected ROI Lift (%)",
                        "key": "expected_roi_lift",
                        "field_type": TaskOutputFieldTypeChoices.FLOAT,
                        "description": "Projected improvement vs baseline.",
                        "order": 5,
                        "is_required": True,
                    },
                ],
            },

            # 3. ------------------------------------------- Unlock Customer Segments
            {
                "key": "unlock_customer_segments",
                "output_schema_name": "High-Potential Segment Blueprint",
                "output_schema_description": (
                    "Detailed profiles and go-to-market plans for untapped segments."
                ),
                "inputs": [
                    {
                        "name": "Market Region Focus",
                        "key": "market_region",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Country/region of interest.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Existing Segment Data CSV",
                        "key": "segment_dataset",
                        "input_type": TaskInputTypeChoices.FILE,
                        "description": "CRM export of current segments.",
                        "order": 2,
                        "is_required": False,
                    },
                    {
                        "name": "Max New Segments",
                        "key": "max_segments",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Limit suggestions (e.g., 3).",
                        "order": 3,
                        "is_required": False,
                    },
                    {
                        "name": "Minimum Revenue Potential",
                        "key": "min_revenue_potential",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Annual threshold (USD).",
                        "order": 4,
                        "is_required": False,
                    },
                    {
                        "name": "Competitor Clues",
                        "key": "competitor_clues",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Notes on competitor wins.",
                        "order": 5,
                        "is_required": False,
                    },
                ],
                "outputs": [
                    {
                        "name": "New Segments",
                        "key": "new_segments",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Names of recommended segments.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Segment Profiles",
                        "key": "segment_profiles",
                        "field_type": TaskOutputFieldTypeChoices.DICT,
                        "description": "Segment → traits map.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Entry Strategies",
                        "key": "entry_strategies",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Tactics to enter each segment.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Testing Roadmap",
                        "key": "testing_roadmap",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "3-phase test plan with KPIs.",
                        "order": 4,
                        "is_required": False,
                    },
                    {
                        "name": "Projected Revenue (USD)",
                        "key": "projected_revenue",
                        "field_type": TaskOutputFieldTypeChoices.FLOAT,
                        "description": "Combined annual potential.",
                        "order": 5,
                        "is_required": False,
                    },
                    {
                        "name": "Primary Channels",
                        "key": "primary_channels",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Best channels per segment.",
                        "order": 6,
                        "is_required": True,
                    },
                ],
            },

            # 4. --------------------------------------- Design Integrated Campaigns
            {
                "key": "design_integrated_campaigns",
                "output_schema_name": "Cross-Channel Campaign Playbook",
                "output_schema_description": (
                    "Sequenced, multi-channel campaign plan with measurement."
                ),
                "inputs": [
                    {
                        "name": "Campaign Objective",
                        "key": "campaign_objective",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Single-sentence business goal.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Target Audience",
                        "key": "target_audience",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Persona focus.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Budget Limit (USD)",
                        "key": "budget_limit",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "Max spend.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Key Channels",
                        "key": "key_channels",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Comma-separated channels.",
                        "order": 4,
                        "is_required": True,
                    },
                    {
                        "name": "Launch Date",
                        "key": "launch_date",
                        "input_type": TaskInputTypeChoices.DATETIME,
                        "description": "Planned start date.",
                        "order": 5,
                        "is_required": True,
                    },
                    {
                        "name": "End Date",
                        "key": "end_date",
                        "input_type": TaskInputTypeChoices.DATETIME,
                        "description": "Planned end date.",
                        "order": 6,
                        "is_required": False,
                    },
                    {
                        "name": "Brand Theme",
                        "key": "brand_theme",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Narrative or hook.",
                        "order": 7,
                        "is_required": False,
                    },
                    {
                        "name": "Primary Offer/CTA",
                        "key": "primary_offer",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Main incentive.",
                        "order": 8,
                        "is_required": False,
                    },
                ],
                "outputs": [
                    {
                        "name": "Campaign Summary",
                        "key": "campaign_summary",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Elevator pitch.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Channel Role Map",
                        "key": "channel_role_map",
                        "field_type": TaskOutputFieldTypeChoices.DICT,
                        "description": "Channel → role in funnel.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Messaging Highlights",
                        "key": "messaging_highlights",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Key messages & value props.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Timeline Milestones",
                        "key": "timeline_milestones",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Key dates & deliverables.",
                        "order": 4,
                        "is_required": True,
                    },
                    {
                        "name": "Measurement Plan",
                        "key": "measurement_plan",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "KPIs & tracking methods.",
                        "order": 5,
                        "is_required": True,
                    },
                    {
                        "name": "Risk Notes",
                        "key": "risk_notes",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Blockers & mitigations.",
                        "order": 6,
                        "is_required": False,
                    },
                ],
            },

            # 5. ------------------------------------------- Define Brand Positioning
            {
                "key": "define_brand_positioning",
                "output_schema_name": "Brand Positioning Guide",
                "output_schema_description": (
                    "Unified positioning, tone, and messaging frameworks."
                ),
                "inputs": [
                    {
                        "name": "Brand Name",
                        "key": "brand_name",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Official brand name.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Core Value Proposition",
                        "key": "core_value_prop",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Primary promise.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Primary Personas",
                        "key": "primary_personas",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Comma-separated personas.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Tone Preference",
                        "key": "tone_preference",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "Brand voice style.",
                        "options": [
                            {"value": "formal", "label": "Formal"},
                            {"value": "friendly", "label": "Friendly"},
                            {"value": "authoritative", "label": "Authoritative"},
                            {"value": "playful", "label": "Playful"},
                        ],
                        "order": 4,
                        "is_required": False,
                    },
                    {
                        "name": "Competitor List",
                        "key": "competitor_list",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Comma-separated competitors.",
                        "order": 5,
                        "is_required": False,
                    },
                    {
                        "name": "Unique Differentiators",
                        "key": "unique_diff",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Bulleted differentiators.",
                        "order": 6,
                        "is_required": False,
                    },
                ],
                "outputs": [
                    {
                        "name": "Positioning Statement",
                        "key": "positioning_statement",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Single-sentence position.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Messaging Matrix",
                        "key": "messaging_matrix",
                        "field_type": TaskOutputFieldTypeChoices.DICT,
                        "description": "Persona → messages.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Value Prop Ladder",
                        "key": "value_prop_ladder",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Hierarchy of benefits.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Tone Guidelines",
                        "key": "tone_guidelines",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Voice & style rules.",
                        "order": 4,
                        "is_required": True,
                    },
                    {
                        "name": "Do's & Don'ts",
                        "key": "dos_and_donts",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Approved and banned language.",
                        "order": 5,
                        "is_required": False,
                    },
                    {
                        "name": "Persona-Specific Hooks",
                        "key": "persona_hooks",
                        "field_type": TaskOutputFieldTypeChoices.DICT,
                        "description": "Persona → hook examples.",
                        "order": 6,
                        "is_required": False,
                    },
                ],
            },

            # 6. -------------------------------------- Identify Strategic Partnerships
            {
                "key": "identify_strategic_partnerships",
                "output_schema_name": "Strategic Partnership Plan",
                "output_schema_description": (
                    "Target partners, collaboration ideas, and outreach framework."
                ),
                "inputs": [
                    {
                        "name": "Core Offering",
                        "key": "core_offering",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Primary product/service.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Target Industry Segments",
                        "key": "target_industries",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Industries for partners.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Partnership Type Interest",
                        "key": "partnership_type",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "Preferred collaboration form.",
                        "options": [
                            {"value": "co_marketing", "label": "Co-marketing"},
                            {"value": "integration", "label": "Product Integration"},
                            {"value": "reseller", "label": "Reseller"},
                            {"value": "affiliate", "label": "Affiliate"},
                        ],
                        "order": 3,
                        "is_required": False,
                    },
                    {
                        "name": "Existing Partners",
                        "key": "existing_partners",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Current partner list.",
                        "order": 4,
                        "is_required": False,
                    },
                    {
                        "name": "Desired Outcomes",
                        "key": "desired_outcomes",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Goals (reach, revenue).",
                        "order": 5,
                        "is_required": False,
                    },
                    {
                        "name": "Resource Commitment",
                        "key": "resource_commitment",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "Capacity level.",
                        "options": [
                            {"value": "low", "label": "Low"},
                            {"value": "medium", "label": "Medium"},
                            {"value": "high", "label": "High"},
                        ],
                        "order": 6,
                        "is_required": False,
                    },
                ],
                "outputs": [
                    {
                        "name": "Recommended Partners",
                        "key": "recommended_partners",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Company names.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Partnership Types",
                        "key": "partnership_types",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Type per partner.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Value Overlap Summary",
                        "key": "value_overlap",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Mutual value rationale.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Collaboration Ideas",
                        "key": "collab_ideas",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Co-marketing/product ideas.",
                        "order": 4,
                        "is_required": True,
                    },
                    {
                        "name": "Outreach Framework",
                        "key": "outreach_framework",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Email & meeting flow.",
                        "order": 5,
                        "is_required": True,
                    },
                    {
                        "name": "Risk & Reward Assessment",
                        "key": "risk_reward",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Upsides vs downsides.",
                        "order": 6,
                        "is_required": False,
                    },
                ],
            },

            # 7. -------------------------------------------------- Set Quarterly Themes
            {
                "key": "set_quarterly_themes",
                "output_schema_name": "Quarterly Theme Calendar",
                "output_schema_description": (
                    "Narrative themes, keywords, and rollout strategy for each quarter."
                ),
                "inputs": [
                    {
                        "name": "Fiscal Year",
                        "key": "fiscal_year",
                        "input_type": TaskInputTypeChoices.NUMBER,
                        "description": "e.g., 2025.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Quarter",
                        "key": "quarter",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "Quarter to define.",
                        "options": [
                            {"value": "Q1", "label": "Q1"},
                            {"value": "Q2", "label": "Q2"},
                            {"value": "Q3", "label": "Q3"},
                            {"value": "Q4", "label": "Q4"},
                        ],
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Brand Objectives",
                        "key": "brand_objectives",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Key business goals.",
                        "order": 3,
                        "is_required": True,
                    },
                    {
                        "name": "Primary Audience",
                        "key": "primary_audience",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Persona focus.",
                        "order": 4,
                        "is_required": True,
                    },
                    {
                        "name": "Keyword Focus List",
                        "key": "keyword_focus",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Comma-separated keywords.",
                        "order": 5,
                        "is_required": False,
                    },
                    {
                        "name": "Emotional Tone",
                        "key": "emotional_tone",
                        "input_type": TaskInputTypeChoices.SELECT,
                        "description": "Dominant emotional tag.",
                        "options": [
                            {"value": "inspirational", "label": "Inspirational"},
                            {"value": "educational", "label": "Educational"},
                            {"value": "urgent", "label": "Urgent"},
                            {"value": "celebratory", "label": "Celebratory"},
                        ],
                        "order": 6,
                        "is_required": False,
                    },
                    {
                        "name": "Core Product Focus",
                        "key": "core_product",
                        "input_type": TaskInputTypeChoices.TEXT,
                        "description": "Product/feature spotlight.",
                        "order": 7,
                        "is_required": False,
                    },
                ],
                "outputs": [
                    {
                        "name": "Theme Statement",
                        "key": "theme_statement",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Headline narrative.",
                        "order": 1,
                        "is_required": True,
                    },
                    {
                        "name": "Target Personas",
                        "key": "target_personas",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Personas emphasized.",
                        "order": 2,
                        "is_required": True,
                    },
                    {
                        "name": "Keyword Set",
                        "key": "keyword_set",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "SEO/SEM keywords.",
                        "order": 3,
                        "is_required": False,
                    },
                    {
                        "name": "Emotional Tags",
                        "key": "emotional_tags",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Tone descriptors.",
                        "order": 4,
                        "is_required": False,
                    },
                    {
                        "name": "Rollout Strategy",
                        "key": "rollout_strategy",
                        "field_type": TaskOutputFieldTypeChoices.STRING,
                        "description": "Channel & timing overview.",
                        "order": 5,
                        "is_required": True,
                    },
                    {
                        "name": "Content Angle Ideas",
                        "key": "content_angles",
                        "field_type": TaskOutputFieldTypeChoices.LIST_STRING,
                        "description": "Suggested hooks & angles.",
                        "order": 6,
                        "is_required": False,
                    },
                ],
            }
        ]


        total = 0
        for task_def in TASK_SCHEMAS:
            task = Task.objects.filter(key=task_def["key"]).first()
            if not task:
                self.stdout.write(self.style.ERROR(f"❌ Task not found: {task_def['key']}"))
                continue

            # Clear previous inputs and output schema
            TaskInput.objects.filter(task=task).delete()
            TaskOutputSchemaField.objects.filter(task_output_schema__task=task).delete()
            TaskOutputSchema.objects.filter(task=task).delete()

            # Create inputs
            for order, input_field in enumerate(task_def["inputs"]):
                TaskInput.objects.create(
                    task=task,
                    name=input_field["name"],
                    key=input_field["key"],
                    input_type=input_field["input_type"],
                    description=input_field["description"],
                    order=order,
                    options=input_field.get("options", []),
                    is_required=input_field.get("is_required", True),
                )

            # Create output schema
            output_schema = TaskOutputSchema.objects.create(
                task=task,
                name=f"{task.name} Output",
                description=f"Generated structured blog outline for {task.name}"
            )
            for order, field in enumerate(task_def["outputs"]):
                TaskOutputSchemaField.objects.create(
                    task_output_schema=output_schema,
                    name=field["name"],
                    key=field["key"],
                    field_type=field["field_type"],
                    description=field["description"],
                    order=order,
                    is_required=field.get("is_required", True),
                )

            total += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Synced inputs/outputs for task: {task.key} - total => {total}"))

        self.stdout.write(self.style.SUCCESS("🎯 Task schema sync complete."))
