"""Login routers."""
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.api import deps
from src.domain import schemas
from src.domain.user import User
from src.services import unit_of_work
from src.services.user import (
    generate_auth_token,
    recover_password,
    reset_password,
    InvalidTokenException,
    UserInactiveException,
    UserNotFoundException,
)


router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        token = generate_auth_token(
            uow, email=form_data.username, password=form_data.password
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }
    except UserNotFoundException:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    except UserInactiveException:
        raise HTTPException(status_code=400, detail="Inactive user")


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def password_recovery(
    email: str,
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Password Recovery
    """
    try:
        recover_password(uow, email)

        return {"msg": "Password recovery email sent"}

    except UserNotFoundException:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )


@router.post("/reset-password/", response_model=schemas.Msg)
def password_reset(
    token: str = Body(...),
    new_password: str = Body(...),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Reset password
    """
    try:
        reset_password(uow, token, new_password)

        return {"msg": "Password updated successfully"}

    except InvalidTokenException:
        raise HTTPException(status_code=400, detail="Invalid token")
    except UserNotFoundException:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    except UserInactiveException:
        raise HTTPException(status_code=400, detail="Inactive user")
