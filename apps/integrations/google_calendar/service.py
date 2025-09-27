from .client import GoogleCalendarClient
from datetime import datetime, timedelta
from django.utils import timezone

class GoogleCalendarService:
    def __init__(self, user):
        self.client = GoogleCalendarClient(user)

    def list_user_calendars(self):
        """List all calendars for the user"""
        params = {
            "maxResults": 100,
            "showDeleted": False,
            "showHidden": False
        }
        result = self.client.list_calendars(params=params)

        if result["success"]:
            calendars = result["data"].get("items", [])
            # Add useful metadata
            for calendar in calendars:
                calendar["isPrimary"] = calendar.get("primary", False)
                calendar["accessRole"] = calendar.get("accessRole", "reader")
            result["data"]["calendars"] = calendars

        return result

    def list_upcoming_events(self, calendar_id='primary', days_ahead=30):
        """List upcoming events for the next N days"""
        now = timezone.now()
        time_max = now + timedelta(days=days_ahead)

        params = {
            "timeMin": now.isoformat(),
            "timeMax": time_max.isoformat(),
            "maxResults": 100,
            "singleEvents": True,
            "orderBy": "startTime"
        }

        result = self.client.list_events(calendar_id=calendar_id, params=params)

        if result["success"]:
            events = result["data"].get("items", [])
            # Add useful metadata
            for event in events:
                start = event.get("start", {})
                if "dateTime" in start:
                    event["startDateTime"] = start["dateTime"]
                elif "date" in start:
                    event["startDate"] = start["date"]
                    event["isAllDay"] = True
            result["data"]["events"] = events

        return result

    def create_simple_event(self, title, start_datetime, end_datetime,
                           description="", calendar_id='primary', timezone_str=None):
        """Create a basic calendar event"""
        if timezone_str is None:
            timezone_str = str(timezone.get_current_timezone())

        event_data = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_datetime.isoformat(),
                "timeZone": timezone_str,
            },
            "end": {
                "dateTime": end_datetime.isoformat(),
                "timeZone": timezone_str,
            }
        }

        return self.client.create_event(calendar_id=calendar_id, event_data=event_data)

    def create_meeting_event(self, title, start_datetime, end_datetime,
                           attendees=None, location="", description="",
                           calendar_id='primary'):
        """Create a meeting event with attendees"""
        event_data = {
            "summary": title,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_datetime.isoformat(),
                "timeZone": str(timezone.get_current_timezone()),
            },
            "end": {
                "dateTime": end_datetime.isoformat(),
                "timeZone": str(timezone.get_current_timezone()),
            },
            "attendees": [{"email": email} for email in (attendees or [])],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},  # 1 day before
                    {"method": "popup", "minutes": 10},       # 10 minutes before
                ],
            },
        }

        return self.client.create_event(calendar_id=calendar_id, event_data=event_data)

    def get_event_details(self, event_id, calendar_id='primary'):
        """Get detailed information about a specific event"""
        return self.client.get_event(calendar_id=calendar_id, event_id=event_id)

    def update_event(self, event_id, updates, calendar_id='primary'):
        """Update an existing event"""
        # First get the current event
        current_event_result = self.client.get_event(calendar_id=calendar_id, event_id=event_id)

        if not current_event_result["success"]:
            return current_event_result

        current_event = current_event_result["data"]

        # Update with new data
        current_event.update(updates)

        return self.client.update_event(calendar_id=calendar_id, event_id=event_id, event_data=current_event)

    def delete_event(self, event_id, calendar_id='primary'):
        """Delete an event"""
        return self.client.delete_event(calendar_id=calendar_id, event_id=event_id)