import json
import logging
from pathlib import Path

import pdfplumber
from pydantic import ValidationError, BaseModel

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent
from agno.media import File

from apps.hiring.models import Resume
from apps.hiring.pydantic_models.pdf_parser_pydantic import ParsedResume
from config import settings
import os
import tempfile

logger = logging.getLogger(__name__)


class GPTResumeParser:
    def __init__(self):
        self.model_id = getattr(settings, 'OPENAI_MODEL_ID', 'gpt-4o')

        # Agent configuration
        self.AGENT_NAME = "Resume Parser Agent"
        self.AGENT_ROLE = (
        "You are a precise resume parser. Extract EXACT facts from the resume/CV "
        "and return a JSON object matching the ParsedResume schema."
    )
        self.AGENT_DESCRIPTION = dedent(
        "Parse contact info, personal info, social links, skills, languages, education, "
        "work experience, projects, certifications, awards, publications, volunteer experience, "
        "references, and metadata. Do not infer or invent."
    )
        self.AGENT_INSTRUCTIONS =[
        # OUTPUT
        "Return ONLY valid JSON for the ParsedResume schema—no prose, no markdown, no comments.",
        "If a field is unknown or not explicitly present, set it to null (for scalars) or [] (for lists). Do NOT guess.",

        # NORMALIZATION
        "Emails: trim whitespace and strip any leading 'mailto:'; if invalid after trimming, set to null.",
        "Apply the same email trimming/validation to professional_references[].email.",
        "Normalize skills/tools: extract verbatim mentions into the appropriate places (technical_skills[].name and work_experience[].technologies_used / projects[].technologies).",
        "Also populate normalized_skills and normalized_tools with canonicalized, LOWERCASED, trimmed, de-duplicated forms (e.g., 'kubernotes'→'kubernetes', 'postgres'→'postgresql').",
        "Lowercase, trim, and case-insensitively de-duplicate normalized_skills, normalized_tools, and normalized_titles.",
        "If a skill line includes specific named technologies in parentheses/notes (e.g., 'relational databases (PostgreSQL, MySQL)'), keep the capability as a Skill in technical_skills (e.g., 'relational databases'), and add the named technologies to normalized_tools; when the context is clear, also add them to the nearest relevant work_experience[].technologies_used or projects[].technologies.",
        "Do NOT create job-style requirement groups or required/preferred tool buckets—those do not exist in the resume schema.",
        "Normalize titles: convert job titles to lowercase canonical forms and populate normalized_titles (e.g., 'Sr. Software Eng.' → 'senior software engineer').",

        # LANGUAGE / LEVEL MAPPING
        "Languages: include Language entries when listed. Set 'proficiency' only if explicitly stated or clearly implied; map 'fluent'/C1/C2→'advanced', B2→'intermediate'; otherwise leave 'proficiency' null.",
        "Map emphasis words ('extensively used', 'expertise in', 'hands-on', 'proficient with') to Skill.level as 'advanced' or 'expert' only when the claim is explicit; otherwise leave null.",
        "career_level_enum: map to a valid SeniorityLevel when the resume clearly implies it; otherwise leave null.",

        # EDUCATION-SPECIFIC GUARDRAILS
        "Set education[].gpa only when clearly on a 4.0 scale; if another scale is detected (e.g., 10.0, 5.0), leave gpa null and store a note in extra_information['gpa_note'] (e.g., 'reported as 8.7/10').",

        # DATES
        "For any date fields, use DateModel and fill only what's present. Examples: year → {'year': 2021, 'original': '2021 – Present'}; month+year → {'year': 2021, 'month': 5, 'original': 'May 2021'}; full date → include day.",
        "If a role is current (e.g., 'Present'), set end_date = null and is_current = true.",
        "Never invent missing components. Do not coerce partial dates into YYYY-MM-DD.",

        # DURATION / EXPERIENCE
        "duration_months: if BOTH start and end have at least year and month, compute month-granularity duration; otherwise set null.",
        "total_years_experience: compute ONLY if all work experiences have computable start and end (or is_current) dates and time intervals are non-overlapping; otherwise set null. Do not estimate.",

        # ENUMS & HYGIENE
        "Enums (SkillLevel, EducationLevel, EmploymentType, WorkLocationType, SeniorityLevel): use only allowed enum values; map common synonyms to valid enums ('FT'→full_time, 'Contractor'→contract); if mapping is unclear, set null.",
        "Phone numbers: normalize to digits with an optional leading '+'.",
        "URLs: return the canonical URL string as seen (trim whitespace only).",
        "Split bullet-like lines into list items where appropriate (responsibilities, achievements, etc.) without altering the wording.",
        "Maintain the resume’s implied chronological order for experiences/education.",
        "Trim whitespace on all scalars; if empty after trimming, set null. For lists, dedupe case-insensitively; return [] if empty.",

        # DERIVED SIGNALS (for scoring)
        "Populate derived_skills_matrix when any signal exists: key = normalized skill/tool; value = { 'years': float|null, 'level': SkillLevel|null, 'category': str|null }. Include an entry only if at least one of these can be determined; otherwise leave derived_skills_matrix as {}.",
        "Only include keys in derived_skills_matrix that also appear in normalized_skills or normalized_tools (keep them in sync).",

        # WORK PREFERENCES / AUTH
        "If present, fill work_preferences (preferred_work_location_type, willing_to_relocate, max_onsite_radius_km, travel_preference_pct, time_zone, availability_date).",
        "If present, fill compensation_expectation (currency, desired_min, desired_max, period, flexibility_note).",
        "Authorization: fill personal_info.work_authorization verbatim; for visa_support_needed and security_clearance use their enums if provided.",

        # PROVENANCE
        # "Populate field_sources as a mapping from field path to the source location/phrase in the resume. Example: personal_info.full_name → 'Header, line 1'; work_experience[0].company → 'Page 1: SW Global Limited'.",

        # METADATA
        "Set parsing_confidence in [0,1] with rubric: 0.95–1.0 all sections confidently mapped; 0.7–0.94 mostly mapped with some nulls; 0.4–0.69 many gaps; <0.4 severe ambiguity.",

        # SAFETY
        "Never fabricate institutions, companies, dates, roles, certifications, or achievements.",
        "If the resume has contradictory or malformed data, set the affected fields to null and add an explanation in extra_information with prefix 'conflict_note: ...'.",

        # FINAL VALIDATION
        "Before returning, validate that the JSON parses, enums are valid, and if both dates include at least a year (and month when present) then assert end_date >= start_date; otherwise skip the comparison."
    ]

        self.agent = Agent(
            name=self.AGENT_NAME,
            model=OpenAIChat(id=self.model_id, temperature=0.0, top_p=0.1),
            role=self.AGENT_ROLE,
            description=self.AGENT_DESCRIPTION,
            instructions=self.AGENT_INSTRUCTIONS,
            markdown=False,
            output_schema=ParsedResume,
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        text_content = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    if page.extract_text():
                        text_content += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
        return text_content

    def parse_file_with_agent(self, pdf_path: str) -> dict:
        """Parse PDF file using the agent"""
        try:
            file_obj = File(filepath=str(pdf_path))
            response = self.agent.run("Analyze this document", files=[file_obj])

            if hasattr(response, 'content') and response.content:
                content = response.content
                if isinstance(content, BaseModel):
                    return content.model_dump()
                if isinstance(content, dict):
                    return content
                text = str(content or '').strip()
                if text.startswith('```'):
                    text = text.strip('`')
                    if text.lower().startswith('json'):
                        text = text[4:].strip()
                return json.loads(text)
            return {}
        except Exception as e:
            logger.error(f"Error parsing file with agent: {e}")
            raise

    def parse_pdf(self, pdf_path: str) -> ParsedResume:
        """Parse PDF and return ParsedResume object"""
        gpt_output = self.parse_file_with_agent(pdf_path)
        try:
            return ParsedResume(**gpt_output)
        except ValidationError as e:
            logger.error(f"Pydantic validation failed: {e}")
            raise ValueError(f"Pydantic validation failed: {str(e)}")

    def parse_pdf_to_dict(self, pdf_path: str) -> dict:
        """Parse PDF and return as a simple dictionary for easier use"""
        resume = self.parse_pdf(pdf_path)
        return json.loads(resume.model_dump_json())

    def parse_uploaded_file_to_dict(self, file_obj) -> dict:
        """
        Accept a Django UploadedFile/FileField or any file-like object,
        read the PDF content, and return structured JSON.
        """
        # If file has a filesystem path already (e.g., FileField), use it directly
        file_path = getattr(getattr(file_obj, 'file', file_obj), 'name', None)
        if file_path and os.path.exists(file_path):
            return self.parse_pdf_to_dict(file_path)

        # Otherwise, persist temporarily then parse
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file_obj.read())
            tmp.flush()
            temp_path = tmp.name

        try:
            return self.parse_pdf_to_dict(temp_path)
        finally:
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Could not  remove temp file: {e}")

    def save_analysis_in_db(self, pdf_path, resume_instance):
        """
        Save the JSON analysis of PDF Resume in the Database Model
        """
        if not resume_instance:
            logger.error("Resume instance not provided")
            return False

        try:
            resume_analysis = self.parse_pdf_to_dict(pdf_path)

            # Optionally store raw text for reference
            try:
                resume_text = self.extract_text_from_pdf(pdf_path).strip()
            except Exception as e:
                logger.warning(f"Could not extract text from PDF: {e}")
                resume_text = None

            # Save to database
            resume_instance.parsed_text = resume_text
            resume_instance.metadata = resume_analysis
            resume_instance.save()

            logger.info(f"Successfully saved analysis for resume ID: {resume_instance.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save analysis in DB: {e}")
            return False

    def run_example(self, resume_file_path):
        """Run parsing example"""
        file_path = Path(resume_file_path)
        response = self.agent.run(
            "Analyze this document",
            files=[File(filepath=file_path)]
        )
        if response and hasattr(response, 'content'):
            return response.content.model_dump_json(indent=2)
        return None