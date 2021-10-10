from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr

from src.api import deps
from src.config import settings
from src.domain import schemas
from src.domain.user import User
from src.services import user as user_service, unit_of_work
from src.services.user import UserAlreadyExistsException, UserNotFoundException


router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Retrieve users.
    """
    users = user_service.get_list(uow, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    user_in: schemas.UserCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Create new user.
    """
    try:
        user = user_service.create(uow, user_in)

        return user

    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )


@router.post("/open", response_model=schemas.User)
def create_user_open(
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    try:
        user_in = schemas.UserCreate(
            password=password, email=email, full_name=full_name
        )
        user = user_service.create(uow, user_in)

        return user

    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: User = Depends(deps.get_current_active_user),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email

    user = user_service.update_by_id(uow, current_user.id, user_in)

    return user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_service.get_by_id(uow, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )

    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Update a user.
    """
    try:
        user = user_service.update_by_id(uow, user_id, user_in)

        return user

    except UserNotFoundException:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
