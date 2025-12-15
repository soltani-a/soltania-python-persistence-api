# tests/test_basic.py
from datetime import datetime
from soltania_persistence.core.domain import BaseEntity

def test_base_entity_instantiation():
    """
    Test that the BaseEntity can be instantiated and 
    automatically sets defaults like created_at.
    """
    # Create an entity without arguments
    entity = BaseEntity()

    # Check that Pydantic initialized the fields
    assert entity.id is None
    assert isinstance(entity.created_at, datetime)
    assert isinstance(entity.updated_at, datetime)