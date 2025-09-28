from celery import shared_task
from django.utils import timezone
from django.conf import settings
from apps.depts.services.simplified_emergency_pipeline import SimplifiedEmergencyPipeline, EmergencyRequest
from apps.depts.models import CitizenRequest, ActionLog, Location, City
import logging

from call_agent import EmergencyCallAgent

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_emergency_request_task(self, request_data):
    """
    Celery task to process emergency requests asynchronously without DB saving
    """
    try:
        logger.info(f"Starting emergency request processing")
        logger.info(f"Request data: {request_data}")

        pipeline = SimplifiedEmergencyPipeline()

        emergency_request = EmergencyRequest(**request_data)
        logger.info(f"Emergency request: {emergency_request}")
        result = pipeline.process_emergency_request(emergency_request)

        logger.info(f"Emergency request processing completed: {result}")

        return {
            'success': True,
            'message': 'Emergency request processed successfully'
        }

    except Exception as e:
        logger.error(f"Error in process_emergency_request_task: {str(e)}")

        # Retry the task after 30 seconds
        raise self.retry(countdown=30, exc=e)


@shared_task
def make_emergency_call_task(phone_number: str, call_reason: str, context_data: dict):
    """
    Celery task specifically for making emergency calls
    """
    try:

        logger.info(f"Making emergency call to {phone_number} for {call_reason}")

        agent = EmergencyCallAgent()
        result = agent.make_emergency_call(
            phone_number=phone_number,
            call_reason=call_reason,
            additional_context=context_data
        )

        logger.info(f"Emergency call result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in make_emergency_call_task: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def follow_up_emergency_task(citizen_request_id: int):
    """
    Celery task for follow-up actions on emergency requests
    """
    try:
        citizen_request = CitizenRequest.objects.get(id=citizen_request_id)
        logger.info(f"Performing follow-up for emergency request: {citizen_request.case_code}")

        # Implement follow-up logic here
        # For example: check status, make additional calls, send notifications, etc.

        ActionLog.objects.create(
            citizen_request=citizen_request,
            action_type='FOLLOW_UP_COMPLETED',
            description='Automatic follow-up completed',
            success=True
        )

        return {'success': True, 'message': 'Follow-up completed'}

    except Exception as e:
        logger.error(f"Error in follow_up_emergency_task: {str(e)}")
        return {'success': False, 'error': str(e)}