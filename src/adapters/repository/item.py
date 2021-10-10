"""Item repositories."""
from abc import ABC, abstractmethod
from typing import List, Optional, Set

from src.domain.item import Item


class AbstractRepository(ABC):
    """Item repository interface"""

    def __init__(self):
        self.modified = set()  # type: Set[Item]

    def add(self, item: Item):
        self._add(item)
        self.modified.add(item)
        return item

    @abstractmethod
    def _add(self, item: Item):
        raise NotImplementedError

    @abstractmethod
    def get(self, id: int) -> Optional[Item]:
        raise NotImplementedError

    @abstractmethod
    def list(self, offset: int, limit: int) -> List[Item]:
        raise NotImplementedError

    @abstractmethod
    def list_by_owner(self, owner_id: int, offset: int, limit: int) -> List[Item]:
        raise NotImplementedError

    @abstractmethod
    def remove(self, id: int) -> Optional[Item]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, item: Item):
        """Create/update Item."""
        if self.get(item.id):
            self._update(item)
        else:
            self.session.add(item)

    def _update(self, item: Item):
        """Update User."""
        self.session.query(Item).filter_by(id=item.id).update(
            {
                Item.title: item.title,
                Item.description: item.description,
                Item.owner_id: item.owner_id,
            }
        )

    def get(self, id: int) -> Optional[Item]:
        """Get Item by id."""
        return self.session.query(Item).get(id)

    def list(self, skip: int, limit: int) -> List[Item]:
        """Get Items."""
        return (
            self.session.query(Item).order_by(Item.id).offset(skip).limit(limit).all()
        )

    def list_by_owner(self, owner_id: int, skip: int, limit: int) -> List[Item]:
        """Get Items by owner."""
        return (
            self.session.query(Item)
            .filter_by(owner_id=owner_id)
            .order_by(Item.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def remove(self, item_id: int) -> None:
        """Delete an item."""
        self.session.query(Item).filter_by(id=item_id).delete()
