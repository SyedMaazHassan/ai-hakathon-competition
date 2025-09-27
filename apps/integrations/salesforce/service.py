import logging

from apps.authentication.models import Client
from apps.integrations.salesforce.client import SalesforceClient
from apps.sale_rooms.models import ClientContact

logger = logging.getLogger(__name__)


class SalesforceService:
    """
    Business logic for Salesforce interaction.
    Uses SalesforceClient to make API calls.
    """

    def __init__(self, user):
        self.user = user
        self.client = SalesforceClient(user)

    def fetch_contacts(self):
        path = "/services/data/v58.0/query/"
        query = "SELECT Id, FirstName, LastName, Phone, Title, Email FROM Contact LIMIT 100"
        params = {"q": query}

        try:
            response = self.client.request("GET", path, params=params)
            return response.json().get("records", [])
        except Exception:
            logger.exception("Salesforce contact fetch failed for user %s", self.user)
            raise Exception("Failed to fetch contacts from Salesforce.")


    def import_contacts_to_db(self, user, contacts):
        saved_data = []

        for contact in contacts:
            first_name = contact.get("FirstName") or ""
            last_name = contact.get("LastName") or ""
            email = contact.get("Email") or ""
            title = contact.get("Title") or "No title"
            salesforce_id = contact.get("Id")

            if not email:
                continue

            domain = email.split("@")[1]
            client_name = domain.split(".")[0].capitalize()

            client_obj, _ = Client.objects.get_or_create(
                name=client_name,
                defaults={"user": user}
            )

            if client_obj.user is None:
                client_obj.user = user
                client_obj.save()

            contact_obj, created = ClientContact.objects.update_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "salesforce_id": salesforce_id,
                    "client": client_obj,
                    "notes": title,
                }
            )
            saved_data.append(contact_obj)

        return saved_data

    def create_or_update_contact(self, contact_obj):
        path = "/services/data/v58.0/sobjects/Contact"
        payload = {
            "FirstName": contact_obj.first_name or "",
            "LastName": contact_obj.last_name or "Unknown",
            "Email": contact_obj.email,
            "Title": contact_obj.notes or "",
        }

        try:
            if contact_obj.salesforce_id:
                update_path = f"{path}/{contact_obj.salesforce_id}"
                self.client.request("PATCH", update_path, json=payload)
            else:
                response = self.client.request("POST", path, json=payload)
                if response.status_code == 201:
                    contact_obj.salesforce_id = response.json().get("id")
                    contact_obj.save()
                    return

        except Exception as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code in [300, 400]:
                    resolved_id = self._resolve_duplicate_contact(e.response.json(), payload)
                    if resolved_id:
                        contact_obj.salesforce_id = resolved_id
                        contact_obj.save()
                        return
            logger.exception("Salesforce contact sync failed for user %s", self.user)
            raise Exception("Failed to sync contact with Salesforce.")

    def _resolve_duplicate_contact(self, error_json, payload):
        for error in error_json:
            if error.get("errorCode") != "DUPLICATES_DETECTED":
                continue

            match_results = error.get("duplicateResult", {}).get("matchResults", [{}])
            if not match_results:
                continue

            match_records = match_results[0].get("matchRecords", [])
            if not match_records:
                continue

            existing_id = match_records[0].get("record", {}).get("Id")
            if not existing_id:
                continue

            try:
                path = f"/services/data/v58.0/sobjects/Contact/{existing_id}"
                response = self.client.request("PATCH", path, json=payload)
                if response.status_code in [200, 204]:
                    return existing_id
            except Exception:
                logger.error("Failed to update duplicate contact for user %s", self.user)

        return None
