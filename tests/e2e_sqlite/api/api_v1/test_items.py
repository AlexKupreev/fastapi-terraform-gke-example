from fastapi.testclient import TestClient

from src.config import settings
from src.services import unit_of_work
from tests.utils.item import create_random_item


def test_create_item(
    client: TestClient,
    superuser_token_headers: dict,
    uow_sqlite: unit_of_work.AbstractUnitOfWork,
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )

    assert response.status_code == 200
    content = response.json()

    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_read_item(
    client: TestClient,
    superuser_token_headers: dict,
    uow_sqlite: unit_of_work.AbstractUnitOfWork,
) -> None:

    item = create_random_item(uow_sqlite)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == item.id
    assert content["owner_id"] == item.owner_id
