from celery import shared_task
import logging
from apps.ai_agents.services.job_description_parser_agent import JobDescriptionParserAgent
from apps.jobs.models import Job

logger = logging.getLogger(__name__)


@shared_task
def process_job_description_parsing(job_id: int):
    """
    Parse a Job's description and persist structured JSON to `parsed_detailed`.
    """
    logger.info(f"Processing Job Description parsing for job {job_id}")
    job = Job.objects.filter(id=job_id).first()
    if not job:
        logger.error(f"Job not found for id={job_id}")
        return

    try:
        agent = JobDescriptionParserAgent()
        result = agent.save_parsed_in_db(job)

        # Check if the result contains fallback data
        if result.get("status") == "failed" or result.get("parsing_confidence", 1.0) < 0.5:
            logger.warning(f"Job description parsing completed with low confidence or fallback data for job {job_id}")
            return {"job_id": job_id, "status": "completed_with_fallback",
                    "confidence": result.get("parsing_confidence", 0.0)}
        else:
            logger.info(f"Successfully saved parsed job description for job {job_id}")
            return {"job_id": job_id, "status": "completed", "confidence": result.get("parsing_confidence", 1.0)}
    except Exception as e:
        logger.exception(f"Failed to parse job description for job {job_id}: {e}")
        return {"job_id": job_id, "status": "failed", "error": str(e)}