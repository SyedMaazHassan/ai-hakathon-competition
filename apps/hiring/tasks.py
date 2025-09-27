from celery import shared_task
import logging

from apps.hiring.models import Resume
from apps.ai_agents.services.gpt_pdf_parser import GPTResumeParser
from apps.ai_agents.services.job_fit_report_agent import JobFitReportAgent
from apps.hiring.models import JobApplication
from apps.ai_agents.services.job_description_parser_agent import JobDescriptionParserAgent

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_parsed_resume(self, resume_id):
    logger.info(f"Processing Resume {resume_id}")
    resume = Resume.objects.filter(id=resume_id).first()
    if not resume:
        logger.error(f"Resume not found for {resume_id}")
        return

    resume_file_path = resume.file.path
    parser = GPTResumeParser()
    parser.save_analysis_in_db(resume_file_path, resume)
    logger.info(f"Parsed Resume Json Saved For {resume_id}")
    logger.info(f"Resume {resume.id} metadata after parsing: {resume.metadata}")
    return {"resume_id": resume_id}


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def process_job_fit_scoring(self, application_id: int):
    """
    Generate Job Fit Report for a JobApplication and persist it.
    Retries until both job + resume are parsed.
    """
    logger.info(f"Processing Job Fit Report for application {application_id}")
    application = (
        JobApplication.objects
        .filter(id=application_id)
        .select_related("job", "resume")
        .first()
    )
    if not application:
        logger.error(f"JobApplication not found for id={application_id}")
        return {"status": "not_found"}

    # Ensure job is parsed
    if not application.job.parsed_detailed:
        logger.info(f"Job {application.job.id} not parsed yet → queueing parsing task")
        process_job_description_parsing.delay(application.job.id)
        raise self.retry(exc=Exception("Job not parsed yet"))

    # Ensure resume is parsed
    if not application.resume.metadata:
        logger.info(f"Resume {application.resume.id} not parsed yet → queueing parsing task")
        process_parsed_resume.delay(application.resume.id)
        raise self.retry(exc=Exception("Resume not parsed yet"))

    # Check if Job Fit Report already exists
    if application.job_fit_report:
        logger.info(f"Job Fit Report already exists for application {application_id}, skipping generation.")
        return {"application_id": application_id, "status": "skipped", "report": application.job_fit_report}

    # Both available then generate fit report
    try:
        agent = JobFitReportAgent()
        report = agent.save_report_in_db(application)
        logger.info(f"Saved Job Fit Report for application {application_id}")
        return {"application_id": application_id, "status": "completed", "report": report}
    except Exception as e:
        logger.exception(f"Failed to generate Job Fit Report for application {application_id}: {e}")
        raise self.retry(exc=e, countdown=60)

