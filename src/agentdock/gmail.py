from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .keychain import get_secret, set_secret

GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
TOKEN_NAME = "AGENTDOCK_GMAIL_OAUTH_TOKEN"


@dataclass(frozen=True)
class EmailMessage:
    id: str
    sender: str
    subject: str
    date: str
    snippet: str


def _google_imports() -> Dict[str, Any]:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Gmail support is not installed. Run: python3 -m pip install -e '.[gmail]'"
        ) from exc
    return {"Request": Request, "Credentials": Credentials,
            "InstalledAppFlow": InstalledAppFlow, "build": build}


def connect_gmail(client_secrets: Path) -> None:
    google = _google_imports()
    flow = google["InstalledAppFlow"].from_client_secrets_file(
        str(client_secrets), [GMAIL_SCOPE]
    )
    credentials = flow.run_local_server(port=0)
    set_secret(TOKEN_NAME, credentials.to_json())


def _service() -> Any:
    google = _google_imports()
    raw = get_secret(TOKEN_NAME)
    if not raw:
        raise RuntimeError(
            "Gmail is not connected. Run: agentdock connect gmail --client-secrets PATH"
        )
    try:
        info = json.loads(raw)
        credentials = google["Credentials"].from_authorized_user_info(info, [GMAIL_SCOPE])
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Stored Gmail OAuth token is invalid; connect Gmail again") from exc
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(google["Request"]())
        set_secret(TOKEN_NAME, credentials.to_json())
    if not credentials.valid:
        raise RuntimeError("Gmail authorization expired; connect Gmail again")
    return google["build"]("gmail", "v1", credentials=credentials, cache_discovery=False)


def _header(headers: List[Dict[str, str]], name: str) -> str:
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


def parse_message(payload: Dict[str, Any]) -> EmailMessage:
    headers = payload.get("payload", {}).get("headers", [])
    return EmailMessage(
        id=payload.get("id", ""),
        sender=_header(headers, "From"),
        subject=_header(headers, "Subject") or "(no subject)",
        date=_header(headers, "Date"),
        snippet=payload.get("snippet", ""),
    )


def list_messages(query: str = "", limit: int = 10) -> List[EmailMessage]:
    service = _service()
    response = service.users().messages().list(
        userId="me", q=query or None, maxResults=limit
    ).execute()
    messages = []
    for item in response.get("messages", []):
        payload = service.users().messages().get(
            userId="me", id=item["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        ).execute()
        messages.append(parse_message(payload))
    return messages


def format_messages(messages: List[EmailMessage]) -> str:
    if not messages:
        return "No messages found."
    return "\n\n".join(
        f"From: {message.sender}\nSubject: {message.subject}\n"
        f"Date: {message.date}\nPreview: {message.snippet}"
        for message in messages
    )
