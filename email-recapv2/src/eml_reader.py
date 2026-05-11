"""
eml_reader.py
Reads .eml files and extracts sender, recipient, subject, date, and body text.
"""

from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from pathlib import Path


def parse_eml_file(filepath: str) -> dict:
    """Parse a single .eml file and return a structured dict."""
    with open(filepath, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    return {
        "filename": Path(filepath).name,
        "sent_from": _extract_address(msg, "from"),
        "sent_to": _extract_address(msg, "to"),
        "subject": msg.get("subject", "(no subject)"),
        "date": msg.get("date", ""),
        "date_parsed": _parse_date(msg.get("date", "")),  # used for sorting
        "body": _extract_body(msg),
    }


def load_all_emails(folder_path: str) -> list[dict]:
    """
    Load all .eml files from a folder and sort by date (oldest first).
    Returns a list of email dicts.
    """
    folder = Path(folder_path)
    eml_files = sorted(folder.glob("*.eml"))

    if not eml_files:
        print(f"Tidak ada file .eml di: {folder_path}")
        return []

    emails = []
    for filepath in eml_files:
        try:
            parsed = parse_eml_file(str(filepath))
            emails.append(parsed)
            print(f"  ✓ {filepath.name}")
        except Exception as e:
            print(f"  ✗ Gagal membaca {filepath.name}: {e}")

    # Sort by parsed date; emails with no date go to the end
    emails.sort(key=lambda e: e["date_parsed"] or "9999")

    return emails


def _extract_address(msg, field: str) -> str:
    """Extract a clean email address from a header field (From or To)."""
    value = msg.get(field, "")
    if "<" in value and ">" in value:
        return value.split("<")[1].replace(">", "").strip()
    return value.strip()


def _parse_date(date_str: str) -> str:
    """
    Parse an email date string into ISO format (YYYY-MM-DD HH:MM) for sorting.
    Returns empty string if parsing fails.
    """
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ""


def _extract_body(msg) -> str:
    """Extract plain text body from an email, trimmed to 3000 characters."""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_content()
                break
        # Fallback to HTML if no plain text
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    body = part.get_content()
                    break
    else:
        body = msg.get_content()

    return body.strip()[:3000]
