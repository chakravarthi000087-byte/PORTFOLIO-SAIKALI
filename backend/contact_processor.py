"""Contact form validation, sanitization, and persistence processor.

Designed for both Vercel serverless functions (using writable /tmp storage)
and local Python servers, with RFC-aligned email validation and duplicate
fingerprinting.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from backend.models import ContactSubmission
from backend.portfolio_data import OWNER_EMAIL

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
CONTROL_CHARS_REGEX = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
HTML_TAG_REGEX = re.compile(r"<[^>]+>")

DEFAULT_STORE_PATH = Path(os.environ.get("PORTFOLIO_CONTACT_STORE", "/tmp/sai_portfolio_contacts.jsonl"))
_MEMORY_SUBMISSIONS: List[Dict[str, Any]] = []


def sanitize_text(value: str, max_length: int) -> str:
    """Strip unsafe control characters, inline HTML tags, and excess whitespace."""
    cleaned = CONTROL_CHARS_REGEX.sub("", value or "")
    cleaned = HTML_TAG_REGEX.sub("", cleaned)
    cleaned = " ".join(cleaned.strip().split())
    return cleaned[:max_length]


def sanitize_multiline_text(value: str, max_length: int) -> str:
    """Preserve intentional line breaks while stripping HTML tags and control bytes."""
    cleaned = CONTROL_CHARS_REGEX.sub("", value or "")
    cleaned = HTML_TAG_REGEX.sub("", cleaned)
    lines = [line.strip() for line in cleaned.strip().splitlines()]
    normalized = "\n".join(line for line in lines if line or len(lines) == 1)
    return normalized[:max_length]


def validate_contact_payload(payload: Dict[str, Any]) -> Tuple[Optional[Dict[str, str]], List[str]]:
    """Validate and normalize incoming contact JSON payload."""
    errors: List[str] = []
    if not isinstance(payload, dict):
        return None, ["Request payload must be a JSON object."]

    raw_name = str(payload.get("name", ""))
    raw_email = str(payload.get("email", ""))
    raw_message = str(payload.get("message", ""))

    name = sanitize_text(raw_name, max_length=120)
    email = sanitize_text(raw_email, max_length=160).lower()
    message = sanitize_multiline_text(raw_message, max_length=2500)

    if len(name) < 2:
        errors.append("Please enter your name (at least 2 characters).")
    if not EMAIL_REGEX.match(email):
        errors.append("Please provide a valid email address.")
    if len(message) < 5:
        errors.append("Please include a message of at least 5 characters.")

    if errors:
        return None, errors

    return {"name": name, "email": email, "message": message}, []


def build_mailto_url(name: str, email: str, message: str) -> str:
    """Generate a URL-encoded mailto link matching the portfolio contact workflow."""
    subject = quote(f"Portfolio Inquiry from {name}")
    body = quote(f"Name: {name}\nEmail: {email}\n\n{message}")
    return f"mailto:{OWNER_EMAIL}?subject={subject}&body={body}"


def compute_submission_fingerprint(name: str, email: str, message: str) -> str:
    """Compute a short deterministic SHA-256 fingerprint for deduplication."""
    digest = hashlib.sha256(f"{name.lower()}|{email.lower()}|{message}".encode("utf-8")).hexdigest()
    return digest[:16]


def persist_submission(
    submission: ContactSubmission,
    store_path: Optional[Path] = None,
) -> bool:
    """Persist contact metadata to memory and /tmp JSONL storage when writable."""
    record = submission.to_dict()
    _MEMORY_SUBMISSIONS.append(record)
    if len(_MEMORY_SUBMISSIONS) > 100:
        del _MEMORY_SUBMISSIONS[0]

    target = store_path or DEFAULT_STORE_PATH
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
        return True
    except OSError:
        return False


def process_contact_submission(
    payload: Dict[str, Any],
    store_path: Optional[Path] = None,
) -> Tuple[int, Dict[str, Any]]:
    """Validate, enrich, persist, and acknowledge a contact form submission."""
    normalized, errors = validate_contact_payload(payload)
    if errors or normalized is None:
        return 400, {
            "ok": False,
            "errors": errors,
            "message": errors[0] if errors else "Invalid contact payload.",
        }

    name = normalized["name"]
    email = normalized["email"]
    message = normalized["message"]
    timestamp = datetime.now(timezone.utc).isoformat()
    fingerprint = compute_submission_fingerprint(name, email, message)
    mailto_url = build_mailto_url(name, email, message)

    submission = ContactSubmission(
        submission_id=f"msg_{uuid.uuid4().hex[:12]}",
        sender_name=name,
        sender_email=email,
        message=message,
        submitted_at=timestamp,
        fingerprint=fingerprint,
        mailto_url=mailto_url,
    )

    persisted_to_disk = persist_submission(submission, store_path=store_path)

    return 201, {
        "ok": True,
        "submission_id": submission.submission_id,
        "submitted_at": submission.submitted_at,
        "fingerprint": submission.fingerprint,
        "persisted_to_disk": persisted_to_disk,
        "mailto_url": submission.mailto_url,
        "confirmation": f"Thanks {name}! Your inquiry has been validated and prepared.",
    }


def get_contact_summary(store_path: Optional[Path] = None) -> Dict[str, Any]:
    """Return aggregate submission count without exposing private sender emails."""
    target = store_path or DEFAULT_STORE_PATH
    disk_count = 0
    if target.exists():
        try:
            with target.open("r", encoding="utf-8") as handle:
                disk_count = sum(1 for line in handle if line.strip())
        except OSError:
            disk_count = 0

    total = max(disk_count, len(_MEMORY_SUBMISSIONS))
    return {
        "total_submissions": total,
        "recipient_email": OWNER_EMAIL,
        "status": "ready",
    }
