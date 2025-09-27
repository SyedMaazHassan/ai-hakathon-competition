from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .oauth import GoogleDriveOAuth
import logging

logger = logging.getLogger(__name__)

class GoogleDriveClient:
    def __init__(self, user):
        self.user = user
        self.oauth = GoogleDriveOAuth(user)
        self.credentials = self.oauth.get_valid_credentials()
        self.service = build("drive", "v3", credentials=self.credentials)

    def list_files(self, params=None):
        try:
            response = self.service.files().list(**(params or {})).execute()
            return {"success": True, "data": response}
        except HttpError as e:
            logger.error(f"[GoogleDrive] list_files failed for {self.user.email}: {e}")
            return {"success": False, "error": str(e)}

    def get_file(self, file_id, params=None):
        try:
            response = self.service.files().get(fileId=file_id, **(params or {})).execute()
            return {"success": True, "data": response}
        except HttpError as e:
            logger.error(f"[GoogleDrive] get_file failed for {self.user.email}, ID: {file_id}: {e}")
            return {"success": False, "error": str(e)}
