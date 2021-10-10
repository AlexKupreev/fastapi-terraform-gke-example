import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sh

from src.config import settings
from src.domain import schemas
from src.initial_data import main as init_data
from src.utils import publish_with_err_handler


router = APIRouter()

security = HTTPBasic()


def get_basic_http_username(credentials: HTTPBasicCredentials = Depends(security)):
    if not settings.BASIC_HTTP_CREDS:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Not yet supported",
        )

    username, password = settings.BASIC_HTTP_CREDS.split(":", maxsplit=1)
    correct_username = secrets.compare_digest(credentials.username, username)
    correct_password = secrets.compare_digest(credentials.password, password)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.post("/migrate_db", response_model=schemas.Msg, status_code=201)
def migrate_db(username: str = Depends(get_basic_http_username)) -> Any:
    output = sh.alembic("upgrade", "head")
    return {"msg": str(output)}


@router.post("/prefill_db", response_model=schemas.Msg, status_code=201)
def prefill_db(username: str = Depends(get_basic_http_username)) -> Any:
    init_data()
    return {"msg": "DB prefilled"}


@router.post("/test-pubsub", response_model=schemas.Msg, status_code=201)
def test_pubsub(
    msg: schemas.Msg,
    username: str = Depends(get_basic_http_username),
) -> Any:
    """
    Test pubsub worker.
    """
    publish_with_err_handler(settings.PUBSUB_PROJECT_ID, settings.TOPIC_ID, msg.msg)
    return {"msg": "Word received"}
