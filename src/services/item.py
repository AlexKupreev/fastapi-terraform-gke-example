"""Item services"""
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder

from .unit_of_work import AbstractUnitOfWork
from src.domain import schemas
from src.domain.item import Item


def create(
    uow: AbstractUnitOfWork,
    obj_in: Union[schemas.ItemCreate, Dict[str, Any]],
    owner_id: int,
) -> Item:
    """Create new item."""
    item_data = jsonable_encoder(obj_in)
    item_data["owner_id"] = owner_id

    with uow:
        item_obj = Item(**item_data)

        item = uow.items.add(item_obj)

        uow.commit()
        return item


def get_by_id(uow: AbstractUnitOfWork, item_id: int) -> Optional[Item]:
    """Get item information by ID."""
    with uow:
        item = uow.items.get(id=item_id)

        return item


def update(
    uow: AbstractUnitOfWork,
    item_id: int,
    obj_in: Union[schemas.ItemUpdate, Dict[str, Any]],
    owner_id: int = None,
) -> Item:
    """Update item information."""
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)

    with uow:
        item = uow.items.get(id=item_id)
        if not item:
            raise ItemNotFoundException()

        if owner_id and item.owner_id != owner_id:
            raise ItemPermissionException()

        obj_data = jsonable_encoder(item)

        for field in obj_data:
            if field in update_data:
                setattr(item, field, update_data[field])

        item = uow.items.add(item)

        uow.commit()

        return item


def delete(uow: AbstractUnitOfWork, item_id: int, owner_id: int = None) -> Item:
    """Delete item (also respecting for its owner)."""
    with uow:
        item = uow.items.get(id=item_id)
        if not item:
            raise ItemNotFoundException()

        if owner_id and item.owner_id != owner_id:
            raise ItemPermissionException()

        uow.items.remove(item_id)

        uow.commit()

        return item


def get_list(uow: AbstractUnitOfWork, skip: int, limit: int) -> List[Item]:
    """List of items"""
    with uow:
        items = uow.items.list(skip, limit)

        return items


def get_list_by_owner(
    uow: AbstractUnitOfWork, owner_id: int, skip: int, limit: int
) -> List[Item]:
    """List of items"""
    with uow:
        items = uow.items.list_by_owner(owner_id, skip, limit)

        return items


class ItemNotFoundException(Exception):
    ...


class ItemPermissionException(Exception):
    ...
