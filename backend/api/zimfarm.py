import datetime
import json
import logging
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, NamedTuple
from uuid import UUID, uuid4

import requests
from pydantic import BaseModel

from api.constants import constants

GET = "GET"
POST = "POST"
PATCH = "PATCH"
DELETE = "DELETE"

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class RequestSchema:
    """Flags sent to ZF for the schedule/task"""

    collection_url: str
    name: str
    title: str
    description: str
    long_description: str | None
    language: str
    creator: str
    publisher: str
    tags: list[str]
    main_logo_url: str
    illustration_url: str


class WebhookPayload(BaseModel):
    """Webhook payload sent by ZF"""

    _id: str
    status: str
    timestamp: dict
    schedule_name: str
    worker_name: str
    updated_at: str
    config: dict
    original_schedule_name: str
    events: list[dict]
    debug: dict
    requested_by: str
    canceled_by: str
    container: str
    priority: int
    notification: dict
    files: dict[str, dict]
    upload: dict


class TokenData:
    """In-memory persistence of ZF credentials"""

    ACCESS_TOKEN: str = ""
    ACCESS_TOKEN_EXPIRY: datetime.datetime = datetime.datetime(
        2000, 1, 1, tzinfo=datetime.UTC
    )
    REFRESH_TOKEN: str = ""
    REFRESH_TOKEN_EXPIRY: datetime.datetime = datetime.datetime(
        2000, 1, 1, tzinfo=datetime.UTC
    )


class ZimfarmAPIError(Exception):
    def __init__(self, message: str, code: int = -1) -> None:
        super().__init__(message)
        self.code = code

    def __str__(self):
        if self.code:
            return f"HTTP {self.code}: {', '.join(self.args)}"
        return ", ".join(self.args)


class ZimfarmResponse(NamedTuple):
    succeeded: bool
    code: int
    data: str | dict[str, Any]


def get_url(path: str) -> str:
    return "/".join([constants.zimfarm_api_url, path[1:] if path[0] == "/" else path])


def get_token_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Token {token}",
        "Content-type": "application/json",
    }


def get_token(username: str, password: str) -> tuple[str, str]:
    req = requests.post(
        url=get_url("/auth/authorize"),
        headers={
            "username": username,
            "password": password,
            "Content-type": "application/json",
        },
        timeout=constants.zimfarm_request_timeout_sec,
    )
    req.raise_for_status()
    return req.json().get("access_token", ""), req.json().get("refresh_token", "")


def authenticate(*, force: bool = False):
    if (
        not force
        and TokenData.ACCESS_TOKEN
        and TokenData.ACCESS_TOKEN_EXPIRY
        > datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(minutes=2)
    ):
        return

    logger.debug(f"authenticate() with {force=}")

    try:
        access_token, refresh_token = get_token(
            username=constants.zimfarm_username, password=constants.zimfarm_password
        )
    except Exception:
        TokenData.ACCESS_TOKEN = TokenData.REFRESH_TOKEN = ""
        TokenData.ACCESS_TOKEN_EXPIRY = datetime.datetime(
            2000, 1, 1, tzinfo=datetime.UTC
        )
    else:
        TokenData.ACCESS_TOKEN, TokenData.REFRESH_TOKEN = access_token, refresh_token
        TokenData.ACCESS_TOKEN_EXPIRY = datetime.datetime.now(
            tz=datetime.UTC
        ) + datetime.timedelta(minutes=59)
        TokenData.REFRESH_TOKEN_EXPIRY = datetime.datetime.now(
            tz=datetime.UTC
        ) + datetime.timedelta(days=29)


def auth_required(func):
    def wrapper(*args, **kwargs):
        authenticate()
        return func(*args, **kwargs)

    return wrapper


@auth_required
def query_api(
    method: str,
    path: str,
    payload: dict[str, str | list[str]] | None = None,
    params: dict[str, str] | None = None,
) -> ZimfarmResponse:
    func = {
        GET: requests.get,
        POST: requests.post,
        PATCH: requests.patch,
        DELETE: requests.delete,
    }.get(method.upper(), requests.get)
    try:
        req = func(
            url=get_url(path),
            headers=get_token_headers(TokenData.ACCESS_TOKEN),
            json=payload,
            params=params,
            timeout=constants.zimfarm_request_timeout_sec,
        )
    except Exception as exc:
        logger.exception(exc)
        return ZimfarmResponse(False, 900, f"ConnectionError -- {exc!s}")

    try:
        resp = req.json() if req.text else {}
    except json.JSONDecodeError:
        return ZimfarmResponse(
            False,
            req.status_code,
            f"ResponseError (not JSON): -- {req.text}",
        )
    except Exception as exc:
        return ZimfarmResponse(
            False,
            req.status_code,
            f"ResponseError -- {exc!s} -- {req.text}",
        )

    if (
        req.status_code >= HTTPStatus.OK
        and req.status_code < HTTPStatus.MULTIPLE_CHOICES
    ):
        return ZimfarmResponse(True, req.status_code, resp)

    # Unauthorised error: attempt to re-auth as scheduler might have restarted?
    if req.status_code == HTTPStatus.UNAUTHORIZED:
        authenticate(force=True)

    reason = resp["error"] if "error" in resp else str(resp)
    if "error_description" in resp:
        reason = f"{reason}: {resp['error_description']}"
    return ZimfarmResponse(False, req.status_code, reason)


@auth_required
def test_connection():
    return query_api(GET, "/auth/test")


def request_task(
    project_id: UUID, archive_id: UUID, request_def: RequestSchema, email: str | None
) -> UUID:
    ident = uuid4().hex

    flags = {
        "collection": request_def.collection_url,
        "name": request_def.name,
        "output": "/output",
        "zim-file": f"nautilus_{archive_id}_{ident}.zim",
        "language": request_def.language,
        "title": request_def.title,
        "description": request_def.description,
        "creator": request_def.creator,
        "publisher": request_def.publisher,
        "tags": ";".join(request_def.tags),
        "favicon": request_def.illustration_url,
    }
    if request_def.main_logo_url:
        flags.update({"main-logo": request_def.main_logo_url})

    config = {
        "task_name": "nautilus",
        "warehouse_path": "/other",
        "image": {
            "name": constants.zimfarm_nautilus_image.split(":")[0],
            "tag": constants.zimfarm_nautilus_image.split(":")[1],
        },
        "resources": {
            "cpu": constants.zimfarm_task_cpu,
            "memory": constants.zimfarm_task_memory,
            "disk": constants.zimfarm_task_disk,
        },
        "platform": None,
        "monitor": False,
        "flags": flags,
    }

    # gen schedule name
    schedule_name = f"nautilus_{archive_id}_{ident}"
    # create schedule payload
    payload = {
        "name": schedule_name,
        "language": {"code": "eng", "name_en": "English", "name_native": "English"},
        "category": "other",
        "periodicity": "manually",
        "tags": [],
        "enabled": True,
        "config": config,
    }

    # add notification callback if email supplied
    if email:
        url = (
            f"{constants.zimfarm_callback_base_url}"
            f"/projects/{project_id}/archives/{archive_id}/hook"
            f"?token={constants.zimfarm_callback_token}&target={email}"
        )
        payload.update(
            {
                "notification": {
                    "requested": {"webhook": [url]},
                    "ended": {"webhook": [url]},
                }
            }
        )

    # create a unique schedule for that request on the zimfarm
    success, status, resp = query_api("POST", "/schedules/", payload=payload)
    if not success:
        logger.error(f"Unable to create schedule via HTTP {status}: {resp}")
        message = f"Unable to create schedule via HTTP {status}: {resp}"
        if status == HTTPStatus.BAD_REQUEST:
            # if Zimfarm replied this is a bad request, then this is most probably
            # a bad request due to user input so we can track it like a bad request
            raise ZimfarmAPIError(message, status)
        else:
            # otherwise, this is most probably an internal problem in our systems
            raise ZimfarmAPIError(message, status)

    # request a task for that newly created schedule
    success, status, resp = query_api(
        "POST",
        "/requested-tasks/",
        payload={
            "schedule_names": [schedule_name],
            "worker": constants.zimfarm_task_worker,
            "priority": "6",
        },
    )
    if not success:
        logger.error(f"Unable to request {schedule_name} via HTTP {status}: {resp}")
        raise ZimfarmAPIError(f"Unable to request schedule: {resp}", status)

    if not isinstance(resp, dict):
        raise ZimfarmAPIError(f"response is unexpected format ({type(resp)})")

    try:
        task_id = resp["requested"].pop()
        if not task_id:
            raise ValueError(f"task_id is empty? `{task_id}`")
    except Exception as exc:
        raise ZimfarmAPIError(f"Couldn't retrieve requested task id: {exc!s}") from exc

    # remove newly created schedule (not needed anymore)
    success, status, resp = query_api("DELETE", f"/schedules/{schedule_name}")
    if not success:
        logger.error(
            f"Unable to remove schedule {schedule_name} via HTTP {status}: {resp}"
        )
    return UUID(task_id)
