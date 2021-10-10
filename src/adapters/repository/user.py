"""User repositories."""
from abc import ABC, abstractmethod
from typing import List, Optional, Set

from src.domain.user import User


class AbstractRepository(ABC):
    """User repository interface"""

    def __init__(self):
        self.modified = set()  # type: Set[User]

    def add(self, user: User):
        self._add(user)
        self.modified.add(user)

    @abstractmethod
    def _add(self, user: User):
        raise NotImplementedError

    @abstractmethod
    def get(self, id: int) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def list(self, skip: int, limit: int) -> List[User]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, user: User):
        """Create/update User."""
        if self.get(user.id):
            self._update(user)
        else:
            self.session.add(user)

    def _update(self, user: User):
        """Update User."""
        self.session.query(User).filter_by(id=user.id).update(
            {
                User.full_name: user.full_name,
                User.email: user.email,
                User.hashed_password: user.hashed_password,
                User.is_active: user.is_active,
                User.is_superuser: user.is_superuser,
            }
        )

    def get(self, id: int) -> Optional[User]:
        """Get User by id."""
        return self.session.query(User).get(id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get User by email."""
        return self.session.query(User).filter_by(email=email).one_or_none()

    def list(self, skip: int, limit: int) -> List[User]:
        """Get Users."""
        return (
            self.session.query(User).order_by(User.id).offset(skip).limit(limit).all()
        )
