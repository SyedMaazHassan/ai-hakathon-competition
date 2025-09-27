import json
import re
from typing import Optional
from textwrap import dedent
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.exceptions import ModelProviderError
from openai import APITimeoutError

from apps.hiring.pydantic_models.job_description import ParsedJob
from config import settings
from apps.hiring.models import Job

logger = logging.getLogger(__name__)


class JobDescriptionParserAgent:
    """
    Parses unstructured job descriptions into structured JSON using Agno with a Pydantic response model.
    Saves the generated JSON in the database.
    """

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or getattr(settings, 'OPENAI_MODEL_ID', 'gpt-4o')

        # Configure timeout settings - increased for full descriptions
        self.timeout = getattr(settings, 'OPENAI_TIMEOUT', 120.0)  # Increased to 120 seconds for full descriptions
        self.max_retries = getattr(settings, 'OPENAI_MAX_RETRIES', 3)

        self.agent = Agent(
            name="Job Parser Agent",
            model=OpenAIChat(
                id=self.model_id,
                temperature=0.0,
                top_p=0.1,
                timeout=self.timeout  # Set timeout for the model
            ),
            role=dedent(
        "You are a precise job parser. Extract EXACT facts from the job description "
        "and return a JSON object matching the ParsedJob schema."
    ),
            description=dedent(
        "Parse job descriptions into the ParsedJob schema. Capture title, company, metadata, skills, tools, "
        "requirements, responsibilities, education, experience, languages, authorizations, compensation, "
        "outcomes/KPIs, perks. Do not infer or invent values. "
        "When both structured job fields and raw JD text are provided, prefer structured values and only use "
        "the JD to supplement missing fields."
    ),
            instructions=[
        # OUTPUT FORMAT
        "Return ONLY valid JSON matching the ParsedJob schema exactly—no prose, markdown, or comments.",
        "If a field is unknown or not explicitly present, set it to null (for scalars) or [] (for lists). Never guess.",
        "Keys and enum values MUST match the schema exactly (use 'other'/'not_specified' only where those enums support them).",

        # INPUT PRECEDENCE
        "If structured job fields are provided alongside JD text, prefer the structured values and use the JD only to fill missing fields.",

        # DATE HANDLING
        "For posted_at, updated_at, application_deadline use DateModel with only available parts.",
        "Examples: year → {'year': 2024, 'original': '2024'}; month+year → {'year': 2024, 'month': 5, 'original': 'May 2024'}; full date → include day.",
        "Never coerce partial dates into YYYY-MM-DD.",

        # FIELD PROCESSING
        "URLs: return exactly as written after trimming whitespace.",
        "Emails: trim whitespace and strip any leading 'mailto:'; if invalid after trimming, set to null.",

        "EXTRACT TOOLS FROM NOTES: When skills have specific tools in notes/parentheses, extract each tool as a separate entry:",
        "- 'relational databases (PostgreSQL, MySQL)' → add capability to *_skills (e.g., 'relational databases') AND add 'PostgreSQL' and 'MySQL' to *_tools",
        "- 'cloud platforms (AWS, GCP, or Azure)' → add capability to *_skills and 'AWS', 'GCP', 'Azure' to *_tools; also add a requirement_group with logic='any_of'",
        "- Keep the general capability in *_skills and the named technologies in *_tools (no cross-placement).",

        "SKILLS VS TOOLS CLARIFICATION: When extracting from notes fields:",
        "- Extract specific tool names as separate tool requirements in *_tools.",
        "- Keep the broader capability as a skill in *_skills.",
        "- Do NOT place named technologies (e.g., 'PostgreSQL', 'Kubernetes') in *_skills, and do NOT place capabilities (e.g., 'database design') in *_tools.",
        "- Example: 'relational databases (PostgreSQL, MySQL)' → Skill: 'relational databases'; Tools: 'PostgreSQL', 'MySQL'.",

        "When multiple similar tools are listed (e.g., PostgreSQL, MySQL), determine if it's AND/OR:",
        "- If they're alternatives → create requirement_group with logic='any_of'.",
        "- If both are truly required → keep separate entries (and you may also use logic='all_of' when the JD states it).",

        "Skills/tools: extract verbatim into required_skills/preferred_skills and required_tools/preferred_tools, following the above rules.",
        "DO NOT repeat the same named technology in both *_skills and *_tools.",
        "Normalization: populate normalized_skills/normalized_tools with canonicalized, LOWERCASED, trimmed, de-duplicated forms (e.g., 'postgres'→'postgresql', 'k8s'→'kubernetes').",
        "Proficiency/years: set level, min_years, preferred_years ONLY when explicitly stated.",
        "Enums: map common synonyms ('FT'→'full_time', 'Remote'→'remote', 'Contract'→'contract'); when unclear, use allowed enum fallbacks.",

        # CORE STRUCTURE
        "Essential fields: title, alternative_titles, seniority, employment_type, work_location_type.",
        "Company: Populate name, website, industry, size, about, locations only from explicit mentions.",
        "Posting: Populate source, source_url, dates, requisition_id, ats_board, contact_email when available.",
        "Application: Populate apply_url, instructions, screening_questions, interview_stages if specified.",

        # CONTENT SECTIONS
        "Responsibilities: split bullet/line items into responsibilities and day_to_day lists without rewording.",
        "Outcomes: when OKRs/KPIs or deliverables are present, create outcomes entries (description plus optional metric_key/target_value/timeframe).",

        # REQUIREMENTS MAPPING
        "Must-have sections → required_skills/tools with priority='must_have'.",
        "Preferred/Nice-to-have sections → preferred_skills/tools with priority='nice_to_have'.",
        "For grouped logic (e.g., 'React AND TypeScript' or 'Any 2 of AWS/GCP/Azure'), add requirement_groups with logic in {'all_of','any_of','min_count'}; when logic='min_count', set min_count as stated; list each atomic item as a SkillRequirement.",

        # SPECIFIC REQUIREMENTS
        "Experience: fill ExperienceRequirement (min_years_total, preferred_years_total, min_years_in_role, role_keywords, industries). Set equivalency_allowed=True only if JD implies it ('or equivalent experience').",
        "Education: fill EducationRequirement (levels, fields_of_study); set alternatives_allowed=True only if JD explicitly says 'or equivalent experience'; add certifications_as_alternative when stated.",
        "Authorization: populate AuthorizationRequirement (work_authorization, visa_support, security_clearance) only on explicit mentions.",
        "Location: populate LocationRequirement (work_location_type, city/state/country, onsite_radius_km, relocation, travel_percentage) when specified.",

        "role_keywords: pick from job title and description; prefer lowercase for consistency.",
        "Languages: when a language is listed, include a LanguageRequirement entry. Set 'proficiency' only if explicitly stated or clearly implied; map 'fluent'/C1/C2→'advanced', B2→'intermediate'; otherwise leave 'proficiency' null.",

        # COMPENSATION & BENEFITS
        "Salary: when ranges are given, set compensation.currency, min_amount, max_amount, and period (hourly/daily/weekly/monthly/yearly). Infer period only from explicit keywords (e.g., 'per hour', 'annual').",
        "Additional comp: populate equity, bonus when explicitly listed.",
        "Benefits/perks: populate benefits/perks arrays only from explicit mentions.",

        # METADATA
        "Keywords: capture relevant keywords and role_taxonomy codes when present.",
        "Priority defaults: use 'must_have' for items in strict requirement sections; 'nice_to_have' for preferred sections.",
        "Leave weight fields null unless explicitly provided.",

        # DATA QUALITY
        "Trim all scalars; convert empty strings to null. Dedupe lists case-insensitively; use [] for empty lists.",
        "Drop list entries lacking required text (e.g., SkillRequirement without a name).",
        "Keep responsibilities/day_to_day/outcomes as plain text lists; do not merge or rewrite.",

        # TRACEABILITY
        # "Populate 'field_sources' as a mapping from field path to source snippet (e.g., required_skills[0].name → 'Qualifications: Python (5+ years)').",
        # "Keep 'field_sources' as verbatim snippets of the specific field (short, sourcey), not whole lines with extra words.",
        # "For contradictory data (e.g., two different salary ranges), set the affected field(s) to null and add a short 'conflict_note' entry under field_sources (e.g., field_sources._conflicts += ['salary ranges differ in two sections']).",
        "Set parsing_confidence in [0,1] using: 0.95–1.00 precise; 0.70–0.94 mostly mapped; 0.40–0.69 many gaps; <0.40 severe ambiguity.",

        # SAFETY & ACCURACY
        "Never invent company names, dates, salaries, requirements, or outcomes.",
        "Ensure consistency (e.g., if 'remote' is mentioned, work_location_type should be 'remote' or 'hybrid' accordingly).",

        # FINAL VALIDATION
        "Ensure the output is valid, parseable JSON that matches the ParsedJob schema.",
        "Double-check that no explicit requirements, skills, or compensation details were missed."
    ],
            markdown=False,
            output_schema=ParsedJob,
        )

    def build_prompt(self, description_text: str) -> str:
        # Log the description length for monitoring
        logger.info(f"Processing job description of length: {len(description_text)} characters")
        
        if len(description_text) > 50000:
            logger.warning(f"Very long job description: {len(description_text)} characters")

        return dedent(f"""
        Analyze this job description and extract structured information as JSON.

        IMPORTANT: 
        - Extract key information from the job description concisely
        - Return ONLY valid, complete JSON for the JobDescriptionData schema
        - Keep responses under 10,000 characters total
        - Focus on the most important details: title, company, location, salary, requirements, skills, benefits

        Job Description:
        {description_text}

        Return ONLY valid JSON with key information extracted from the description.
        """)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=8, max=30),  # Longer waits for full descriptions
        retry=retry_if_exception_type((APITimeoutError, ModelProviderError)),
        reraise=True
    )
    def _call_agent_with_retry(self, prompt: str):
        """Call the agent with retry logic for timeouts."""
        logger.info(f"Calling agent with prompt length: {len(prompt)}")
        return self.agent.run(prompt)

    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text that might contain markdown code blocks or other formatting."""
        text = text.strip()

        # Try to extract JSON from markdown code blocks
        if text.startswith('```'):
            # Remove the code block markers
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

        return text.strip()

    def _repair_truncated_json(self, json_string: str) -> str:
        """Attempt to repair truncated JSON by completing the structure."""
        # Count open and close braces to check balance
        open_braces = json_string.count('{')
        close_braces = json_string.count('}')

        # If we have more open braces, add closing braces
        if open_braces > close_braces:
            json_string += '}' * (open_braces - close_braces)

        # Check for unterminated strings
        lines = json_string.split('\n')
        for i, line in enumerate(lines):
            # Count quotes in each line
            quotes = line.count('"')
            if quotes % 2 != 0:  # Odd number of quotes means unterminated string
                # Try to find where the string should end
                if i < len(lines) - 1:
                    # Look for the next line that might complete the string
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if '"' in lines[j]:
                            # Assume the string continues to the next quote
                            break
                    else:
                        # No closing quote found, add one
                        lines[i] = line + '"'

        json_string = '\n'.join(lines)

        # Final check: ensure it ends with a closing brace
        if not json_string.strip().endswith('}'):
            # Find the last complete object
            last_brace = json_string.rfind('}')
            if last_brace != -1:
                json_string = json_string[:last_brace + 1]
            else:
                # If no closing brace found anywhere, add one
                json_string = json_string.rstrip() + '}'

        return json_string

    def _parse_with_fallback(self, json_text: str) -> ParsedJob:
        """Multiple attempts to parse JSON with increasingly aggressive repairs."""
        attempts = [
            # Attempt 1: Direct parse
            lambda: json.loads(json_text),

            # Attempt 2: Basic repair
            lambda: json.loads(self._repair_truncated_json(json_text)),

            # Attempt 3: Extract JSON object with regex
            lambda: json.loads(re.search(r'\{.*\}', json_text, re.DOTALL).group()),

            # Attempt 4: Manual repair for common truncation patterns
            lambda: self._manual_json_repair(json_text)
        ]

        for i, attempt in enumerate(attempts):
            try:
                data = attempt()
                return ParsedJob(**data)
            except (json.JSONDecodeError, AttributeError, ValueError) as e:
                logger.warning(f"Parse attempt {i + 1} failed: {e}")
                if i == len(attempts) - 1:  # Last attempt
                    raise ValueError(f"All JSON parsing attempts failed: {e}")

    def _manual_json_repair(self, json_text: str) -> dict:
        """Manual JSON repair for severely truncated responses."""
        if not json_text.strip().startswith('{'):
            json_text = '{' + json_text

        if not json_text.strip().endswith('}'):
            json_text = json_text + '}'

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return {
                "title": "Unknown",
                "parsing_confidence": 0.1,
                "error": "JSON parsing failed due to truncation"
            }

    def parse(self, description_text: str) -> ParsedJob:
        """Parse job description text into structured data."""
        prompt = self.build_prompt(description_text)

        try:
            result = self._call_agent_with_retry(prompt)
            content = result.content

            if isinstance(content, ParsedJob):
                return content

            if isinstance(content, dict):
                return ParsedJob(**content)

            text = str(content or '').strip()

            json_text = self._extract_json_from_text(text)

            return self._parse_with_fallback(json_text)

        except (APITimeoutError, ModelProviderError) as e:
            logger.error(f"OpenAI API timeout after multiple retries: {e}")
            return self._create_fallback_response(description_text, str(e))
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}")
            # Return a fallback response instead of raising an exception
            return self._create_fallback_response(description_text, str(e))

    def _create_fallback_response(self, description_text: str, error_message: str) -> ParsedJob:
        """Create a fallback response when parsing fails completely."""
        # Try to extract basic information from the description text
        title = "Unknown Position"
        if description_text:
            # Simple regex to extract potential job title
            import re
            title_match = re.search(r'(?:job|position|role|title)[:\s]+([^\n\r]+)', description_text, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()[:100]  # Limit length
        
        return ParsedJob(
            title=title,
            parsing_confidence=0.1,
            metadata={
                "notes": f"Parsing failed due to API timeout/error: {error_message}",
                "fallback_used": True,
                "original_text_length": len(description_text)
            }
        )

    def save_parsed_in_db(self, job: Job) -> dict:
        """
        Parse the job's description and persist structured JSON into `parsed_detailed`.
        Returns the saved dict.
        """
        if not isinstance(job, Job):
            raise ValueError("A valid Job instance is required")

        try:
            # Parse the job description
            parsed = self.parse(job.description or "")
            data = parsed.model_dump()

            # Save to database
            job.parsed_detailed = data
            job.save(update_fields=["parsed_detailed", "updated_at"])

            logger.info(f"Successfully parsed and saved job description for job {job.id}")
            return data
        except Exception as e:
            logger.error(f"Failed to parse and save job description for job {job.id}: {e}")
            # Save error information to the database with fallback data
            fallback_data = {
                "title": "Parsing Failed",
                "parsing_confidence": 0.0,
                "error": str(e),
                "status": "failed",
                "metadata": {
                    "notes": f"Parsing failed: {str(e)}",
                    "fallback_used": True,
                    "original_description_length": len(job.description or "")
                }
            }
            job.parsed_detailed = fallback_data
            job.save(update_fields=["parsed_detailed", "updated_at"])
            
            logger.warning(f"Returning fallback data for job {job.id} due to parsing failure")
            return fallback_data