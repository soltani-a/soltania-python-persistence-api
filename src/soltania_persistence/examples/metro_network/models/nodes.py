from typing import Optional
from soltania_persistence.core.domain import BaseEntity

class Station(BaseEntity):
    """
    Represents a physical subway station (Vertex).
    """
    # Maps to the Gremlin vertex label
    __label__ = "station"

    name: str
    zone: Optional[int] = 1