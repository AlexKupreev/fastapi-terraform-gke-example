from typing import Optional

from src.domain.item import Item
from src.domain.schemas.item import ItemCreate
from src.services import item as item_service, unit_of_work
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_item(
    uow: unit_of_work.AbstractUnitOfWork, *, owner_id: Optional[int] = None
) -> Item:
    if owner_id is None:
        user = create_random_user(uow)
        owner_id = user.id
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description, id=id)
    return item_service.create(uow, obj_in=item_in, owner_id=owner_id)
