import pytest
from pydantic import ValidationError
from soltania_persistence.app.models import Station, Connection

def test_station_creation():
    """Test that a Station model is correctly instantiated."""
    station = Station(name="Champs-Élysées")
    assert station.name == "Champs-Élysées"
    assert station.id is None  # Should be None before persistence
    assert station.__label__ == "station"

def test_station_validation_error():
    """Test that missing required fields raises a validation error."""
    with pytest.raises(ValidationError):
        # Name is mandatory, this should fail
        Station(id=1) 

def test_connection_creation():
    """Test that a Connection (Edge) model is valid."""
    conn = Connection(line="1")
    assert conn.line == "1"
    assert conn.__label__ == "link"