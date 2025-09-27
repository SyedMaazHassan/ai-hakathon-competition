"""
Calendar Action Service - Google Calendar integration wrapper
Plug & play with TriggerOrchestrator CalendarBookingAction
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.integrations.google_calendar.service import GoogleCalendarService
from datetime import datetime, timedelta
from django.utils import timezone
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class CalendarActionService:
    """
    Calendar booking service using existing Google Calendar integration
    """

    def __init__(self, user=None):
        # For demo purposes, we'll use a system user or mock user
        self.user = user
        if user:
            self.calendar_service = GoogleCalendarService(user)
        else:
            self.calendar_service = None

    def execute_calendar_action(self, calendar_action) -> Dict[str, Any]:
        """
        Execute calendar booking action from TriggerOrchestrator

        Args:
            calendar_action: CalendarBookingAction object

        Returns:
            Dict with execution result
        """
        try:
            if not self.calendar_service:
                # Mock booking for demo
                return self._mock_calendar_booking(calendar_action)

            # Parse preferred time slots and create actual booking
            start_time, end_time = self._parse_time_slots(
                calendar_action.preferred_time_slots[0] if calendar_action.preferred_time_slots else "Next business day 9-11 AM"
            )

            # Create calendar event
            result = self.calendar_service.create_meeting_event(
                title=calendar_action.appointment_title,
                start_datetime=start_time,
                end_datetime=end_time,
                attendees=calendar_action.attendee_emails,
                description=calendar_action.appointment_description,
                location="To be confirmed by department"
            )

            if result["success"]:
                event_data = result.get("data", {})
                return {
                    "success": True,
                    "status": "scheduled",
                    "action_type": calendar_action.action_type.value,
                    "event_id": event_data.get("id"),
                    "appointment_title": calendar_action.appointment_title,
                    "start_time": start_time.isoformat(),
                    "duration_minutes": calendar_action.duration_minutes,
                    "attendees": calendar_action.attendee_emails,
                    "calendar_link": event_data.get("htmlLink")
                }
            else:
                return {
                    "success": False,
                    "status": "failed",
                    "action_type": calendar_action.action_type.value,
                    "error": result.get("error", "Calendar booking failed")
                }

        except Exception as e:
            logger.error(f"Calendar booking failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "action_type": calendar_action.action_type.value,
                "error": str(e)
            }

    def _mock_calendar_booking(self, calendar_action) -> Dict[str, Any]:
        """
        Mock calendar booking for testing/demo
        """
        logger.info(f"MOCK CALENDAR BOOKING: {calendar_action.appointment_title}")

        # Generate mock times
        start_time = timezone.now() + timedelta(days=1, hours=9)  # Next day 9 AM
        end_time = start_time + timedelta(minutes=calendar_action.duration_minutes)

        return {
            "success": True,
            "status": "mock_scheduled",
            "action_type": calendar_action.action_type.value,
            "event_id": f"mock_event_{hash(calendar_action.appointment_title)}",
            "appointment_title": calendar_action.appointment_title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": calendar_action.duration_minutes,
            "attendees": calendar_action.attendee_emails,
            "preferred_slots": calendar_action.preferred_time_slots,
            "note": "MOCK BOOKING - Google Calendar not configured"
        }

    def _parse_time_slots(self, time_slot_str: str) -> tuple:
        """
        Parse time slot strings to datetime objects
        """
        try:
            # Simple parsing for demo
            now = timezone.now()

            if "next business day" in time_slot_str.lower():
                # Find next business day
                days_ahead = 1
                target_date = now + timedelta(days=days_ahead)
                while target_date.weekday() >= 5:  # Skip weekends
                    target_date += timedelta(days=1)

                # Parse time range (e.g., "9-11 AM")
                if "9-11 am" in time_slot_str.lower():
                    start_time = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
                    end_time = target_date.replace(hour=11, minute=0, second=0, microsecond=0)
                elif "2-4 pm" in time_slot_str.lower():
                    start_time = target_date.replace(hour=14, minute=0, second=0, microsecond=0)
                    end_time = target_date.replace(hour=16, minute=0, second=0, microsecond=0)
                else:
                    # Default to 9-10 AM
                    start_time = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
                    end_time = target_date.replace(hour=10, minute=0, second=0, microsecond=0)

                return start_time, end_time
            else:
                # Default to tomorrow 9-10 AM
                tomorrow = now + timedelta(days=1)
                start_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
                end_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
                return start_time, end_time

        except Exception as e:
            logger.error(f"Failed to parse time slot: {e}")
            # Fallback to tomorrow 9-10 AM
            tomorrow = timezone.now() + timedelta(days=1)
            start_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
            end_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
            return start_time, end_time

    def get_booking_status(self, event_id: str) -> Dict[str, Any]:
        """
        Check status of calendar booking
        """
        try:
            if not self.calendar_service or event_id.startswith("mock_"):
                return {
                    "success": True,
                    "event_id": event_id,
                    "status": "mock_confirmed",
                    "note": "Mock booking status"
                }

            result = self.calendar_service.get_event_details(event_id)
            if result["success"]:
                event_data = result["data"]
                return {
                    "success": True,
                    "event_id": event_id,
                    "status": event_data.get("status"),
                    "attendees": event_data.get("attendees", []),
                    "start": event_data.get("start"),
                    "end": event_data.get("end")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error")
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def cancel_booking(self, event_id: str) -> Dict[str, Any]:
        """
        Cancel calendar booking
        """
        try:
            if not self.calendar_service or event_id.startswith("mock_"):
                return {
                    "success": True,
                    "event_id": event_id,
                    "status": "mock_cancelled"
                }

            result = self.calendar_service.delete_event(event_id)
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Convenience function for TriggerOrchestrator
def execute_calendar_action(calendar_action, user=None) -> Dict[str, Any]:
    """
    Execute calendar booking action - main entry point
    """
    service = CalendarActionService(user)
    return service.execute_calendar_action(calendar_action)