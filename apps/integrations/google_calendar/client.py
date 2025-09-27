from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .oauth import GoogleCalendarOAuth
import logging

logger = logging.getLogger(__name__)

class GoogleCalendarClient:
    def __init__(self, user):
        self.user = user
        self.oauth = GoogleCalendarOAuth(user)
        self.credentials = self.oauth.get_valid_credentials()
        self.service = build("calendar", "v3", credentials=self.credentials)

    def list_calendars(self, params=None):
        try:
            response = self.service.calendarList().list(**(params or {})).execute()
            return {"success": True, "data": response}
        except HttpError as e:
            logger.error(f"[GoogleCalendar] list_calendars failed for {self.user.email}: {e}")
            return {"success": False, "error": str(e)}

    def list_events(self, calendar_id='primary', params=None):
        try:
            response = self.service.events().list(calendarId=calendar_id, **(params or {})).execute()
            return {"success": True, "data": response}
        except HttpError as e:
            logger.error(f"[GoogleCalendar] list_events failed for {self.user.email}, Calendar: {calendar_id}: {e}")
            return {"success": False, "error": str(e)}

    def create_event(self, calendar_id='primary', event_data=None):
        try:
            response = self.service.events().insert(calendarId=calendar_id, body=event_data).execute()
            return {"success": True, "data": response}
        except HttpError as e:
            logger.error(f"[GoogleCalendar] create_event failed for {self.user.email}, Calendar: {calendar_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_event(self, calendar_id='primary', event_id=None, params=None):
        try:
            response = self.service.events().get(calendarId=calendar_id, eventId=event_id, **(params or {})).execute()
            return {"success": True, "data": response}
        except HttpError as e:
            logger.error(f"[GoogleCalendar] get_event failed for {self.user.email}, Event: {event_id}: {e}")
            return {"success": False, "error": str(e)}

    def update_event(self, calendar_id='primary', event_id=None, event_data=None):
        try:
            response = self.service.events().update(calendarId=calendar_id, eventId=event_id, body=event_data).execute()
            return {"success": True, "data": response}
        except HttpError as e:
            logger.error(f"[GoogleCalendar] update_event failed for {self.user.email}, Event: {event_id}: {e}")
            return {"success": False, "error": str(e)}

    def delete_event(self, calendar_id='primary', event_id=None):
        try:
            self.service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            return {"success": True, "data": {"message": "Event deleted successfully"}}
        except HttpError as e:
            logger.error(f"[GoogleCalendar] delete_event failed for {self.user.email}, Event: {event_id}: {e}")
            return {"success": False, "error": str(e)}