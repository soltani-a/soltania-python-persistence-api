from typing import ClassVar
from ..core.domain import BaseEntity, Relationship

class Station(BaseEntity):
    """
    Represents a Metro Station vertex.
    """
    __label__: ClassVar[str] = "station"
    name: str

class Connection(Relationship):
    """
    Represents a connection (Edge) between stations.
    """
    __label__: ClassVar[str] = "link"
    line: str