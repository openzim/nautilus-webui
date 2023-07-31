import uuid

from dateutil import parser
from httpx import codes

from api.constants import constants


def test_create_user(client):
    response = client.post(f"{constants.api_version_prefix}/users")
    assert response.status_code == codes.CREATED
    json_result = response.json()
    assert uuid.UUID(json_result.get("id"))
    assert parser.parse(json_result.get("created_on"))
    assert response.cookies is not None
    assert uuid.UUID(response.cookies.get("user_id"))
