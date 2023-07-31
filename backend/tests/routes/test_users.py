import uuid
from http import HTTPStatus

from dateutil import parser

from api.constants import constants


def test_create_user(client):
    response = client.post(f"{constants.api_version_prefix}/users")
    assert response.status_code == HTTPStatus.CREATED
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert parser.parse(json_result.get("created_on"))
    assert response.cookies is not None
    assert uuid.UUID(response.cookies.get("user_id"))
