import random
import string
from typing import Dict

from fastapi.testclient import TestClient

from src.config import settings
from src.services import unit_of_work, user as user_service


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(
    client: TestClient, uow_sqlite: unit_of_work.AbstractUnitOfWork
) -> Dict[str, str]:
    user_service.get_list(uow_sqlite, skip=0, limit=10)

    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
