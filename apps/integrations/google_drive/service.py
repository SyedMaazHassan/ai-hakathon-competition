from .client import GoogleDriveClient

class GoogleDriveService:
    def __init__(self, user):
        self.client = GoogleDriveClient(user)

    def list_user_files(self):
        params = {
            "pageSize": 100,
            "fields": "nextPageToken, files(id, name, mimeType, thumbnailLink)",
            "q": "trashed=false"
        }

        result = self.client.list_files(params=params)

        if result["success"]:
            files = result["data"].get("files", [])
            for file in files:
                file["previewUrl"] = f"https://drive.google.com/file/d/{file['id']}/preview"
            result["data"]["files"] = files

        return result

    def get_file_by_id(self, file_id):
        params = {
            "fields": "id, name, mimeType, thumbnailLink, size, createdTime, modifiedTime"
        }
        return self.client.get_file(file_id=file_id, params=params)
