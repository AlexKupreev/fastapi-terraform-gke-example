"""Adapters to ORM."""

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.orm import mapper, relationship

from src.domain.item import Item
from src.domain.user import User


metadata = MetaData()

users = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("full_name", String, index=True),
    Column("email", String, unique=True, index=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, default=True),
    Column("is_superuser", Boolean, default=False),
)


items = Table(
    "item",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("title", String, index=True),
    Column("description", String, index=True),
    Column("owner_id", Integer, ForeignKey("user.id")),
)


def start_mappers():
    """Run classical mapping"""
    mapper(
        User,
        users,
        properties={
            "items": relationship(Item, back_populates="owner"),
        },
    )

    mapper(
        Item,
        items,
        properties={
            "owner": relationship(User, back_populates="items"),
        },
    )
