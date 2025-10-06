import os
import base64
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailIntegration:
    """Gmail API integration for AgentAru"""

    def __init__(self, credentials_path: str = "credentials.json"):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path("token.json")
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(self.token_path), SCOPES
                )
            except Exception as e:
                logger.error(f"Failed to load token: {e}")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}")
                    creds = None

            if not creds:
                if not self.credentials_path.exists():
                    logger.warning(
                        "Gmail credentials not found. Email features will be unavailable."
                    )
                    return

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        try:
            self.service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail service authenticated successfully")
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")

    def read_emails(
        self, max_results: int = 10, query: str = None, label: str = "INBOX"
    ) -> List[Dict[str, Any]]:
        """Read emails from Gmail"""

        if not self.service:
            return []

        try:
            # Build query
            q = query if query else f"label:{label}"

            # Get message IDs
            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=q, maxResults=max_results)
                .execute()
            )

            messages = results.get("messages", [])

            # Fetch full message details
            emails = []
            for msg in messages:
                email_data = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="full")
                    .execute()
                )

                emails.append(self._parse_email(email_data))

            logger.info(f"Read {len(emails)} emails")
            return emails

        except Exception as e:
            logger.error(f"Failed to read emails: {e}")
            return []

    def _parse_email(self, email_data: Dict) -> Dict[str, Any]:
        """Parse Gmail API response"""

        headers = email_data["payload"].get("headers", [])

        # Extract headers
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), "No Subject"
        )
        from_email = next(
            (h["value"] for h in headers if h["name"] == "From"), "Unknown"
        )
        date = next((h["value"] for h in headers if h["name"] == "Date"), "")

        # Extract body
        body = self._get_body(email_data["payload"])

        return {
            "id": email_data["id"],
            "thread_id": email_data["threadId"],
            "subject": subject,
            "from": from_email,
            "date": date,
            "body": body,
            "labels": email_data.get("labelIds", []),
        }

    def _get_body(self, payload: Dict) -> str:
        """Extract email body from payload"""

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    if data:
                        return base64.urlsafe_b64decode(data).decode()
        elif "body" in payload:
            data = payload["body"].get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode()

        return ""

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: List[str] = None,
        bcc: List[str] = None,
    ) -> Dict[str, str]:
        """Send an email"""

        if not self.service:
            return {"error": "Gmail service not available"}

        try:
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            if cc:
                message["cc"] = ", ".join(cc)
            if bcc:
                message["bcc"] = ", ".join(bcc)

            # Create message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send
            sent_message = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            logger.info(f"Sent email: {sent_message['id']}")
            return {"status": "sent", "message_id": sent_message["id"]}

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"error": str(e)}
