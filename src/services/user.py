"""User services"""
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder

from .security import get_password_hash, verify_password
from .unit_of_work import AbstractUnitOfWork
from src.config import settings
from src.domain import schemas
from src.domain.user import User
from src.services import security
from src.utils import (
    generate_password_reset_token,
    get_logger,
    send_new_account_email,
    send_reset_password_email,
    verify_password_reset_token,
)


logger = get_logger(__name__)


def create(uow: AbstractUnitOfWork, user_data: schemas.UserCreate) -> User:
    """Create new user."""

    with uow:
        user = uow.users.get_by_email(email=user_data.email)
        if user:
            raise UserAlreadyExistsException()

        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser,
        )

        uow.users.add(user)
        if settings.EMAILS_ENABLED and user.email:
            send_new_account_email(
                email_to=user.email, username=user.email, password=user_data.password
            )

        uow.commit()
        logger.info("User with id %d created", user.id)

        return user


def get_by_id(uow: AbstractUnitOfWork, user_id: int) -> Optional[User]:
    """Get user information by ID."""
    with uow:
        user = uow.users.get(id=user_id)

        return user


def update_by_id(
    uow: AbstractUnitOfWork,
    user_id: int,
    obj_in: Union[schemas.UserUpdate, Dict[str, Any]],
) -> User:
    """Update user information."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password

    with uow:
        user = uow.users.get(id=user_id)
        logger.debug("User %s found by id %d", str(user), user_id)
        if not user:
            raise UserNotFoundException()

        obj_data = jsonable_encoder(user)

        for field in obj_data:
            if field in update_data:
                setattr(user, field, update_data[field])

        uow.users.add(user)

        uow.commit()
        logger.info("User with id %d updated", user.id)

        return user


def get_list(uow: AbstractUnitOfWork, skip: int, limit: int) -> List[User]:
    """List of users"""
    with uow:
        users = uow.users.list(skip, limit)

        return users


def generate_auth_token(uow: AbstractUnitOfWork, email: str, password: str) -> str:
    """Ensure user exists and passwords match."""
    with uow:
        user = uow.users.get_by_email(email=email)

        if not user:
            raise UserNotFoundException()
        elif not user.is_active:
            raise UserInactiveException()

        if not verify_password(password, user.hashed_password):
            raise UserNotFoundException()

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        return security.create_access_token(user.id, expires_delta=access_token_expires)


def recover_password(uow: AbstractUnitOfWork, email: str) -> None:
    """Get user data and send recovery email."""
    with uow:
        user = uow.users.get_by_email(email=email)

        if not user:
            raise UserNotFoundException(
                "The user with this username does not exist in the system."
            )
        password_reset_token = generate_password_reset_token(email=email)
        send_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )


def reset_password(uow: AbstractUnitOfWork, token: str, new_password: str) -> None:
    """Reset password on provided user input."""
    with uow:
        email = verify_password_reset_token(token)
        if not email:
            raise InvalidTokenException()

        user = uow.users.get_by_email(email=email)
        if not user:
            raise UserNotFoundException()
        elif not user.is_active:
            raise UserInactiveException()

        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        uow.users.add(user)

        uow.commit()
        logger.info("User with id %d updated", user.id)


def authenticate(uow: AbstractUnitOfWork, email: str, password: str) -> Optional[User]:
    """Check password and return a user"""
    with uow:
        user = uow.users.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


class UserNotFoundException(Exception):
    ...


class UserInactiveException(Exception):
    ...


class UserAlreadyExistsException(Exception):
    ...


class InvalidTokenException(Exception):
    ...
