from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException

from src.api import deps
from src.domain import schemas
from src.domain.user import User
from src.services import item as item_service, unit_of_work
from src.services.item import ItemNotFoundException, ItemPermissionException


router = APIRouter()


@router.get("/", response_model=List[schemas.Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Retrieve items.
    """
    if current_user.is_superuser:
        items = item_service.get_list(uow, skip=skip, limit=limit)
    else:
        items = item_service.get_list_by_owner(
            uow, owner_id=current_user.id, skip=skip, limit=limit
        )
    return items


@router.post("/", response_model=schemas.Item)
def create_item(
    item_in: schemas.ItemCreate,
    current_user: User = Depends(deps.get_current_active_user),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Create new item.
    """
    item = item_service.create(uow, obj_in=item_in, owner_id=current_user.id)
    return item


@router.put("/{id}", response_model=schemas.Item)
def update_item(
    id: int,
    item_in: schemas.ItemUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Update an item.
    """
    try:
        if current_user.is_superuser:
            item = item_service.update(uow, id, item_in)
        else:
            item = item_service.update(uow, id, item_in, current_user.id)

        return item

    except ItemNotFoundException:
        raise HTTPException(status_code=404, detail="Item not found")

    except ItemPermissionException:
        raise HTTPException(status_code=400, detail="Not enough permissions")


@router.get("/{id}", response_model=schemas.Item)
def read_item(
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Get item by ID.
    """
    item = item_service.get_by_id(uow, item_id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return item


@router.delete("/{id}", response_model=schemas.Item)
def delete_item(
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
    uow: unit_of_work.AbstractUnitOfWork = Depends(deps.get_uow),
) -> Any:
    """
    Delete an item.
    """
    try:
        if current_user.is_superuser:
            item = item_service.delete(uow, item_id=id)
        else:
            item = item_service.delete(uow, item_id=id, owner_id=current_user.id)

        return item

    except ItemNotFoundException:
        raise HTTPException(status_code=404, detail="Item not found")

    except ItemPermissionException:
        raise HTTPException(status_code=400, detail="Not enough permissions")
