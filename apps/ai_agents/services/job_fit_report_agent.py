import json
from typing import Optional, Dict, Any, List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from textwrap import dedent
from apps.hiring.pydantic_models.job_fit_report import JobFitReport
from apps.hiring.models import JobApplication
from config import settings


class JobFitReportAgent:
    """
    Generates a structured Job Fit Report using Agno Agent with a Pydantic response model.
    """
    AGENT_NAME = "Job Fit Report Generator"
    AGENT_ROLE = dedent("""\
        You are Job Fit Report Generator, a highly experienced Hiring Manager AI Agent.
        Your role is to evaluate candidate resumes against specific job postings and 
        produce structured, decision-ready Job Fit Reports. You apply strict, fair 
        evaluation criteria based on job requirements and candidate qualifications.
    """)
    AGENT_DESCRIPTION = dedent("""
        This agent reads candidate resume metadata together with detailed job information
        and outputs a structured Job Fit Report using the JobFitReport schema. It must be 
        concise, business-ready, and aligned with hiring best practices.
    """)
    AGENT_INSTRUCTIONS = [
        # Scoring framework
        "Use a 0–100 overall fit score. 70–79 = borderline, 80–89 = strong, 90–100 = outstanding.",
        "STRICT REQUIREMENT ENFORCEMENT: Required qualifications are non-negotiable. Missing multiple required items → score ≤ 60.",
        "If a single critical required qualification is missing, cap score at 70.",
        "Weigh qualifications by their importance; required items and core responsibilities have highest priority.",

        # Evidence-driven matching
        "Match resume qualifications and experiences explicitly to job requirements/responsibilities with clear bullets.",
        "Be specific and avoid generic filler. Include only relevant highlights and gaps.",

        # Output hygiene
        "Return ONLY valid JSON for the JobFitReport schema (no extra text or markdown).",
        "Keep language concise, professional, and decision-ready. No fluff. No repetition.",

        # Safety and realism
        "Do not fabricate qualifications, projects, or responsibilities. Keep numbers realistic.",
        "If information is unclear, prefer not to infer; focus on what is evidenced in resume/job context.",
    ]

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or getattr(settings, 'OPENAI_MODEL_ID', 'gpt-4o')

        self.agent = Agent(
            model=OpenAIChat(id=self.model_id),
            telemetry=False,
            markdown=False,
            output_schema=JobFitReport,
            debug_mode=False,
            name=self.AGENT_NAME,
            role=self.AGENT_ROLE,
            description=self.AGENT_DESCRIPTION,
            instructions=self.AGENT_INSTRUCTIONS,
        )

    def _serialize_job(self, application: JobApplication) -> Dict[str, Any]:
        job = application.job
        return {
            "parsed_detailed": job.parsed_detailed,
        }

    def build_prompt(self, application: JobApplication, resume_json: Dict[str, Any]) -> str:
        job_payload = self._serialize_job(application)
        job_json = json.dumps(job_payload)
        resume_str = json.dumps(resume_json)
        print("resume_str", resume_str)
        print("job_json", job_json)

        return f"""
                You are an experienced Hiring Manager. Create a professional, decision-ready Job Fit Report strictly adhering to the provided response schema.

                Inputs:
                - Candidate resume metadata:
                ```json
                {resume_str}
                ```
                - Job details:
                ```json
                {job_json}
                ```

                Scoring & Decision Guidelines:
                Use a 0–100 fit score. Interpret ranges as: 70–79 = borderline, 80–89 = strong, 90–100 = outstanding.
                STRICT REQUIREMENT ENFORCEMENT: Required qualifications are non-negotiable.
                If multiple required qualifications are missing, score must drop significantly (≤60).
                Missing a single critical qualification cannot exceed 70.
                Partial matches on required qualifications should be penalized appropriately.
                Weigh qualifications by their importance; responsibilities and required items have the highest priority.
                Only after required qualifications are satisfied, consider secondary items, responsibilities alignment, and experience depth.

                Keep phrasing concise, professional, and decision-ready. No fluff. No repetition.

                Output Rules:

                Return ONLY valid JSON matching the response schema you were given (no extra text).
                Be specific in lists (skills, highlights, projects). Avoid generic filler.
                Keep numbers realistic; do not fabricate unverifiable claims.
        """

    def generate(self, application: JobApplication) -> JobFitReport:
        resume_json = application.resume.metadata or {}
        prompt = self.build_prompt(application, resume_json)
        result = self.agent.run(prompt)
        content = result.content

        if isinstance(content, JobFitReport):
            return content

        if isinstance(content, dict):
            return JobFitReport(**content)

        if isinstance(content, str):
            text = content.strip()
            if text.startswith('```'):
                text = text.strip('`')
                if text.lower().startswith('json'):
                    text = text[4:].strip()
            return JobFitReport(**json.loads(text))

        raise ValueError("Empty or invalid response from JobFitReportAgent")

    def save_report_in_db(self, application: JobApplication) -> Dict[str, Any]:
        """
        Generate and persist the Job Fit Report on the provided JobApplication.
        Returns the saved JSON (as dict).
        """
        if not application:
            raise ValueError("JobApplication instance is required")
        report = self.generate(application)
        report_dict = report.model_dump()

        application.job_fit_report = report_dict
        application.save(update_fields=["job_fit_report", "updated_at"])

        return report_dict