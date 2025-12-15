# Expose the public API
from .core.domain import BaseEntity
from .core.interfaces import EntityManager, Repository

__all__ = ["BaseEntity", "Repository", "EntityManager"]
