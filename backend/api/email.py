from collections.abc import Iterable
from pathlib import Path
from typing import Any

import humanfriendly
import requests
from jinja2 import Environment, FileSystemLoader, select_autoescape
from werkzeug.datastructures import MultiDict

from api.constants import constants, logger
from api.database.models import Archive

jinja_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "txt"]),
)
jinja_env.filters["short_id"] = lambda value: str(value)[:5]
jinja_env.filters["format_size"] = lambda value: humanfriendly.format_size(
    value, binary=True
)


def send_email_via_mailgun(
    to: Iterable[str] | str,
    subject: str,
    contents: str,
    cc: Iterable[str] | None = None,
    bcc: Iterable[str] | None = None,
    attachments: Iterable[Path] | None = None,
) -> str:
    if not constants.mailgun_api_url or not constants.mailgun_api_key:
        logger.warn(f"Mailgun not configured, ignoring email request to: {to!s}")
        return ""

    values = [
        ("from", constants.mailgun_from),
        ("subject", subject),
        ("html", contents),
    ]

    values += [("to", list(to) if isinstance(to, Iterable) else [to])]
    values += [("cc", list(cc) if isinstance(cc, Iterable) else [cc])]
    values += [("bcc", list(bcc) if isinstance(bcc, Iterable) else [bcc])]
    data = MultiDict(values)

    try:
        resp = requests.post(
            url=f"{constants.mailgun_api_url}/messages",
            auth=("api", constants.mailgun_api_key),
            data=data,
            files=(
                [
                    ("attachment", (fpath.name, open(fpath, "rb").read()))
                    for fpath in attachments
                ]
                if attachments
                else []
            ),
            timeout=constants.mailgun_request_timeout_sec,
        )
        resp.raise_for_status()
    except Exception as exc:
        logger.error(f"Failed to send mailgun notif: {exc}")
        logger.exception(exc)
    return resp.json().get("id") or resp.text


def get_context(task: dict[str, Any], archive: Archive):
    """Jinja context dict for email notifications"""
    return {
        "base_url": constants.public_url,
        "download_url": constants.download_url,
        "task": task,
        "archive": archive,
    }
