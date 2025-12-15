import pytest
from unittest.mock import MagicMock
from soltania_persistence.core.interfaces import EntityManager
from soltania_persistence.app.repositories import StationRepository
from soltania_persistence.app.models import Station

@pytest.fixture
def mock_em():
    """Creates a fake EntityManager."""
    return MagicMock(spec=EntityManager)

@pytest.fixture
def repo(mock_em):
    """Creates the repository using the fake EntityManager."""
    return StationRepository(mock_em)

def test_save_new_station(repo, mock_em):
    """
    Scenario: The station does not exist in DB.
    Expected: It calls persist().
    """
    # GIVEN: A new station
    new_station = Station(name="New Station")
    # AND: The DB says "I don't know this station" (returns None)
    mock_em.find_by_property.return_value = None
    # AND: persist returns the object with an ID
    mock_em.persist.return_value = Station(id=100, name="New Station")

    # WHEN: We save
    result = repo.save(new_station)

    # THEN:
    assert result.id == 100
    mock_em.find_by_property.assert_called_once()
    mock_em.persist.assert_called_once_with(new_station)

def test_save_existing_station(repo, mock_em):
    """
    Scenario: The station ALREADY exists in DB.
    Expected: It does NOT call persist(), just returns the existing one.
    """
    # GIVEN: A station we want to save
    station_to_save = Station(name="Existing Station")
    
    # AND: The DB says "I already have this, here is the ID"
    existing_in_db = Station(id=50, name="Existing Station")
    mock_em.find_by_property.return_value = existing_in_db

    # WHEN: We save
    result = repo.save(station_to_save)

    # THEN:
    assert result.id == 50
    mock_em.persist.assert_not_called() # Crucial: Should not persist again