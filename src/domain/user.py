"""User entity (POPO)."""
from typing import List

from .item import Item


class User:
    """App user."""

    def __init__(
        self,
        full_name: str,
        email: str,
        hashed_password: str,
        is_active: bool,
        is_superuser: bool,
        id: int = None,
        items: List[Item] = None,
    ):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.items = items if items else []
