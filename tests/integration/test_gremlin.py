import pytest
import uuid
from soltania_persistence.provider.tinkerpop.manager import GremlinEntityManager
from soltania_persistence.app.models import Station, Connection
from soltania_persistence.config import settings

# Skip integration tests if the marker is not explicitly called
pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def real_em():
    """
    Connects to the REAL database defined in config.
    """
    em = GremlinEntityManager(settings.gremlin_url)
    yield em
    em.close()

def test_full_lifecycle(real_em):
    """
    Integration Test: Create -> Find -> Link -> Query Path -> Cleanup
    """
    # 1. Setup unique names to avoid collision with real data
    uid = str(uuid.uuid4())[:8]
    name_a = f"Test_Station_A_{uid}"
    name_b = f"Test_Station_B_{uid}"

    # 2. Persist Entities
    station_a = Station(name=name_a)
    station_b = Station(name=name_b)
    
    saved_a = real_em.persist(station_a)
    saved_b = real_em.persist(station_b)

    assert saved_a.id is not None
    assert saved_b.id is not None

    # 3. Verify Find Mechanism
    fetched_a = real_em.find_by_property(Station, "name", name_a)
    assert fetched_a is not None
    assert fetched_a.id == saved_a.id
    assert fetched_a.name == name_a

    # 4. Create Relationship
    conn = Connection(line="TestLine")
    real_em.create_relationship(saved_a, saved_b, conn)

    # 5. Verification (Native Gremlin check via 'g')
    # Check if path exists: A -> B
    path_exists = (
        real_em.g.V(saved_a.id)
        .out("link")
        .hasId(saved_b.id)
        .hasNext()
    )
    assert path_exists is True, "Relationship was not created in GraphDB"

    # 6. Cleanup (Delete the test data)
    print(f"Cleaning up test nodes: {saved_a.id}, {saved_b.id}")
    real_em.g.V(saved_a.id).drop().iterate()
    real_em.g.V(saved_b.id).drop().iterate()