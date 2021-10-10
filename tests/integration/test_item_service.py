from src.domain.schemas.item import ItemCreate, ItemUpdate
from src.services import unit_of_work, item as item_service
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def test_create_item(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    user = create_random_user(uow_sqlite)
    item = item_service.create(uow_sqlite, obj_in=item_in, owner_id=user.id)
    assert item.title == title
    assert item.description == description
    assert item.owner_id == user.id


def test_get_item(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    user = create_random_user(uow_sqlite)
    item = item_service.create(uow_sqlite, obj_in=item_in, owner_id=user.id)
    stored_item = item_service.get_by_id(uow_sqlite, item_id=item.id)
    assert stored_item
    assert item.id == stored_item.id
    assert item.title == stored_item.title
    assert item.description == stored_item.description
    assert item.owner_id == stored_item.owner_id


def test_update_item(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    user = create_random_user(uow_sqlite)
    item = item_service.create(uow_sqlite, obj_in=item_in, owner_id=user.id)
    description2 = random_lower_string()
    item_update = ItemUpdate(description=description2)
    item2 = item_service.update(uow_sqlite, item_id=item.id, obj_in=item_update)
    assert item.id == item2.id
    assert item.title == item2.title
    assert item2.description == description2
    assert item.owner_id == item2.owner_id


def test_delete_item(uow_sqlite: unit_of_work.AbstractUnitOfWork) -> None:
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    user = create_random_user(uow_sqlite)
    item = item_service.create(uow_sqlite, obj_in=item_in, owner_id=user.id)
    item2 = item_service.delete(uow_sqlite, item_id=item.id)
    item3 = item_service.get_by_id(uow_sqlite, item_id=item.id)
    assert item3 is None
    assert item2.id == item.id
    assert item2.title == title
    assert item2.description == description
    assert item2.owner_id == user.id
