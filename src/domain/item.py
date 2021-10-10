"""Item entity (POPO)."""


class Item:
    """App item."""

    def __init__(
        self,
        title: str,
        description: str,
        owner_id: int,
        id: int = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.owner_id = owner_id
