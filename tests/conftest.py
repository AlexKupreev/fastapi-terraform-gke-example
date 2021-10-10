from typing import Dict, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.init_db import init_db
from src.api import deps
from src.api.api_v1.api import api_router
from src.config import settings
from src.services import unit_of_work

from tests.session import SQLITE_SESSION_FACTORY
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session")
def db() -> Generator:
    init_db(unit_of_work.SqlAlchemyUnitOfWork(SQLITE_SESSION_FACTORY))
    yield SQLITE_SESSION_FACTORY


@pytest.fixture(scope="session")
def uow_sqlite() -> unit_of_work.AbstractUnitOfWork:
    return unit_of_work.SqlAlchemyUnitOfWork(SQLITE_SESSION_FACTORY)


@pytest.fixture(scope="module")
def client() -> Generator:
    app = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    app.include_router(api_router, prefix=settings.API_V1_STR)

    app.dependency_overrides[deps.get_uow] = deps.get_uow_sqlite_memory

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(
    client: TestClient, uow_sqlite: unit_of_work.AbstractUnitOfWork
) -> Dict[str, str]:
    return get_superuser_token_headers(client, uow_sqlite)


@pytest.fixture(scope="module")
def normal_user_token_headers(
    client: TestClient, uow_sqlite: unit_of_work.AbstractUnitOfWork
) -> Dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, uow=uow_sqlite
    )
