from typing import Optional
from soltania_persistence.core.domain import BaseEntity

class LearningUnit(BaseEntity):
    """
    Represents a specific course or module (Vertex).
    """
    __label__ = "learning_unit"

    slug: str       # Unique identifier (e.g., 'linux_basics')
    title: str
    category: str
    hours: int