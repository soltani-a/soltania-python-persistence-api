from soltania_persistence.core.domain import Relationship

class Connection(Relationship):
    """
    Represents the link between two stations (Edge).
    It carries properties like the line name and travel duration.
    """
    # Maps to the Gremlin edge label
    __label__ = "connects_to"

    line: str       # e.g., "METRO 1", "RER A"
    duration: int   # Time in seconds