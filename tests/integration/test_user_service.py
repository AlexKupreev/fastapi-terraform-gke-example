from fastapi.encoders import jsonable_encoder

from src.services import unit_of_work, user as user_service
from src.services.security import verify_password
from src.domain.schemas.user import UserCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


def test_create_user(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create(uow_sqlite, user_data=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create(uow_sqlite, user_data=user_in)
    authenticated_user = user_service.authenticate(
        uow_sqlite, email=email, password=password
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    email = random_email()
    password = random_lower_string()
    user = user_service.authenticate(uow_sqlite, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = user_service.create(uow_sqlite, user_data=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(
    uow_sqlite: unit_of_work.AbstractUnitOfWork,
) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, disabled=True)
    user = user_service.create(uow_sqlite, user_data=user_in)
    assert user.is_active


def test_check_if_user_is_superuser(
    uow_sqlite: unit_of_work.AbstractUnitOfWork,
) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = user_service.create(uow_sqlite, user_data=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(
    uow_sqlite: unit_of_work.AbstractUnitOfWork,
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = user_service.create(uow_sqlite, user_data=user_in)
    assert user.is_superuser is False


def test_get_user(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = user_service.create(uow_sqlite, user_data=user_in)
    user_2 = user_service.get_by_id(uow_sqlite, user_id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = user_service.create(uow_sqlite, user_data=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    user_service.update_by_id(uow_sqlite, user_id=user.id, obj_in=user_in_update)
    user_2 = user_service.get_by_id(uow_sqlite, user_id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(new_password, user_2.hashed_password)
