from typing import Dict

from fastapi.testclient import TestClient

from src.config import settings
from src.domain.schemas.user import UserCreate, UserUpdate
from src.domain.user import User
from src.services import user as user_service, unit_of_work
from tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(uow: unit_of_work.AbstractUnitOfWork) -> User:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(username=email, email=email, password=password)
    user = user_service.create(uow, user_in)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, uow: unit_of_work.AbstractUnitOfWork
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    with uow:
        user = uow.users.get_by_email(email=email)

    if not user:
        user_in_create = UserCreate(username=email, email=email, password=password)
        user = user_service.create(uow, user_data=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        user = user_service.update_by_id(uow, user_id=user.id, obj_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)
