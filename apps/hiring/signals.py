import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from apps.hiring.models import Resume, JobApplication, Job
from apps.hiring.tasks import (
    process_parsed_resume,
    process_job_fit_scoring,
    process_job_description_parsing,
)

logger = logging.getLogger(__name__)
logger.info("Hiring signals module loaded successfully!")


@receiver(post_save, sender=Resume)
def trigger_resume_parse_task(sender, instance, created, **kwargs):
    if not instance.file:
        return

    if created:
        transaction.on_commit(lambda: process_parsed_resume.delay(instance.id))
        logger.info(f"Resume {instance.id} task enqueued after commit")


@receiver(post_save, sender=Job)
def trigger_job_description_parsing(sender, instance, created, **kwargs):
    """
    Trigger job description parsing after commit, if description exists.
    Prevents duplicate processing for the same job.
    """
    if not instance.description:
        logger.debug(f"Job {instance.id} has no description. Skipping parsing.")
        return
    
    # Check if parsing was already attempted or completed
    parsed_data = getattr(instance, 'parsed_detailed', None)
    if parsed_data and isinstance(parsed_data, dict):
        confidence = parsed_data.get('parsing_confidence', 0)
        if confidence > 0.3:  # Adjust threshold as needed
            logger.debug(f"Job {instance.id} already has parsed data with confidence {confidence}. Skipping.")
            return
        
        error = parsed_data.get('error')
        if error and 'timeout' in error.lower():
            logger.info(f"Job {instance.id} had previous timeout error, retrying...")
        else:
            logger.debug(f"Job {instance.id} has existing parsing data. Skipping.")
            return

    def enqueue_task():
        try:
            logger.info(f"Queueing job description parsing task for Job {instance.id}")
            process_job_description_parsing.delay(instance.id)
        except Exception as e:
            logger.exception(f"Failed to enqueue job description parsing for Job {instance.id}: {e}")

    transaction.on_commit(enqueue_task)


@receiver(post_save, sender=JobApplication)
def trigger_job_application_task(sender, instance, created, **kwargs):
    """
    Trigger job fit scoring after commit, only if a resume is attached.
    """
    if not instance.resume:
        logger.debug(f"JobApplication {instance.id} saved without resume. Skipping fit scoring.")
        return

    def enqueue_task():
        try:
            logger.info(f"Queueing job fit scoring task for JobApplication {instance.id}")
            process_job_fit_scoring.delay(instance.id)
        except Exception as e:
            logger.exception(f"Failed to enqueue job fit scoring for JobApplication {instance.id}: {e}")

    transaction.on_commit(enqueue_task)
