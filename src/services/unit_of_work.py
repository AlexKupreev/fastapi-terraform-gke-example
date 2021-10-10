# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
from abc import ABC, abstractmethod

from sqlalchemy.orm.session import Session
from src.adapters.repository import (
    user as user_repo,
    item as item_repo,
)
from src.adapters.session import DEFAULT_SESSION_FACTORY


class AbstractUnitOfWork(ABC):
    users: user_repo.AbstractRepository
    items: item_repo.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.users = user_repo.SqlAlchemyRepository(self.session)
        self.items = item_repo.SqlAlchemyRepository(self.session)

        return super().__enter__()

    def __exit__(self, *args):
        self.session.expunge_all()
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()
        for item in self.users.modified:
            self.session.refresh(item)

        for item in self.items.modified:
            self.session.refresh(item)

    def rollback(self):
        self.session.rollback()
