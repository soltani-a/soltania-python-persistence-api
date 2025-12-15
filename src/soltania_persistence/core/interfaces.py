from abc import ABC, abstractmethod
from typing import Type, TypeVar, List, Any, Optional, Generic
from .domain import BaseEntity, Relationship, ID

# Generic Type definitions
T = TypeVar("T", bound=BaseEntity)
R = TypeVar("R", bound=Relationship)

class EntityManager(ABC):
    """
    Interface for the Persistence Context (similar to jakarta.persistence.EntityManager).
    """

    @abstractmethod
    def persist(self, entity: T) -> T:
        """Saves or updates an entity."""
        pass

    @abstractmethod
    def find_by_property(self, entity_class: Type[T], key: str, value: Any) -> Optional[T]:
        """Finds a single entity by a specific property."""
        pass

    @abstractmethod
    def create_relationship(self, source: T, target: T, relation: R) -> None:
        """Creates a link (Edge) between two entities."""
        pass

    @abstractmethod
    def clear_database(self):
        """Truncates the database (Dangerous)."""
        pass
    
    @abstractmethod
    def close(self):
        """Closes the connection."""
        pass

class Repository(ABC, Generic[T]):
    """
    Base interface for all Repositories (similar to JpaRepository<T, ID>).
    """
    def __init__(self, em: EntityManager, entity_class: Type[T]):
        self.em = em
        self.entity_class = entity_class

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist the entity."""
        pass
    
    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        """Find entity by ID."""
        pass