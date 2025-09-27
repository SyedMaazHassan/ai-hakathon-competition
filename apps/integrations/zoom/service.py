import os
import uuid
import shutil
import logging
from datetime import datetime

import requests
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils import timezone

from apps.integrations.zoom.client import ZoomClient
from apps.report_management.models import Transcript
from apps.report_management.helpers.report_choices import PlatformChoices
import json

logger = logging.getLogger(__name__)


class ZoomService:
    """
    Handles business logic for Zoom transcripts:
    - Fetching meetings
    - Downloading transcripts
    - Saving & cleaning transcript
    """

    def __init__(self, user):
        self.user = user
        self.client = ZoomClient(user)
        self.temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_transcripts')
        os.makedirs(self.temp_dir, exist_ok=True)

    def get_transcripts(self):
        from apps.integrations.zoom.constants import ZOOM_RECORDING_URL
        query_params = {
            "from": (datetime.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d'),
            "to": datetime.now().strftime('%Y-%m-%d'),
            "page_size": 300,
        }
        ZOOM_RECORDING_URL = f"{ZOOM_RECORDING_URL}?{requests.compat.urlencode(query_params)}"
        data = self.client.request("GET", ZOOM_RECORDING_URL)
        print(json.dumps(data, indent=2))
        return [
            {
                "meeting_id": m["id"],
                "topic": m.get("topic"),
                "start_time": m.get("start_time"),
                "download_url": f["download_url"]
            }
            for m in data.get("meetings", [])
            for f in m.get("recording_files", [])
            if f.get("file_type") == "TRANSCRIPT"
        ]

    def download_file_from_url(self, url, headers=None):
        headers = headers or {}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to download file. Status: {response.status_code} | URL: {url}")
            return None
        return response.content

    def _clean_transcript(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return "\n".join([
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.strip().isdigit() and '-->' not in line and line.strip() != 'WEBVTT'
            ])

    def _save_transcript_from_path(self, path, filename, topic, url, zoom_id):
        cleaned_text = self._clean_transcript(path)
        with open(path, 'rb') as f:
            transcript = Transcript.objects.create(
                title=topic or slugify(filename),
                text=cleaned_text,
                url=url,
                platform=PlatformChoices.ZOOM,
                zoom_id=zoom_id,
                user=self.user
            )
            transcript.file.save(filename, File(f), save=True)
        return transcript

    def _save_transcript_from_bytes(self, file_bytes, filename, topic, url, zoom_id):
        path = os.path.join(self.temp_dir, filename)
        with open(path, "wb") as f:
            f.write(file_bytes)
        return self._save_transcript_from_path(path, filename, topic, url, zoom_id)

    def fetch_and_save_transcripts(self):
        saved_transcripts = []
        transcripts = self.get_transcripts()

        for data in transcripts:
            meeting_id = data["meeting_id"]
            if Transcript.objects.filter(zoom_id=meeting_id).exists():
                continue

            try:
                filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.vtt"
                file_bytes = self.download_file_from_url(data["download_url"],
                    self.client.oauth._get_auth_headers(self.client.access_token)
                )
                if not file_bytes:
                    continue

                transcript = self._save_transcript_from_bytes(
                    file_bytes=file_bytes,
                    filename=filename,
                    topic=data["topic"],
                    url=data["download_url"],
                    zoom_id=meeting_id
                )
                saved_transcripts.append({
                    "title": transcript.title,
                    "created_at": transcript.created_at,
                    "meeting_id": meeting_id,
                    "id": transcript.id
                })
            except Exception as e:
                logger.warning(f"Failed to save transcript for meeting {meeting_id}: {str(e)}")
                continue

        return saved_transcripts

    def process_transcript_from_webhook(self, meeting_data, download_token):
        meeting_id = meeting_data.get("id")
        topic = meeting_data.get("topic", "No Topic")
        files = meeting_data.get("recording_files", [])

        for f in files:
            if f.get("file_type") != "TRANSCRIPT":
                continue

            download_url = f.get("download_url")
            file_ext = f.get("file_extension", "vtt")
            filename = f"transcript_{meeting_id}.{file_ext}"

            logger.info(f"Attempting to download transcript for meeting {meeting_id}")

            file_bytes = self.download_file_from_url(download_url, headers={"Authorization": f"Bearer {download_token}"})
            if not file_bytes:
                continue

            transcript_obj, created = Transcript.objects.get_or_create(
                zoom_id=meeting_id,
                defaults={
                    "title": topic,
                    "url": download_url,
                    "platform": PlatformChoices.ZOOM,
                    "created_at": timezone.now(),
                    "user": self.user
                }
            )

            if not created:
                logger.info(f"Transcript already exists for meeting ID {meeting_id}")
                return

            transcript_obj.file.save(filename, ContentFile(file_bytes))
            transcript_obj.save()

            logger.info(f"Successfully saved transcript for meeting ID {meeting_id} as {transcript_obj.id}")
