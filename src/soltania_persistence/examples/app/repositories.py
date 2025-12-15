from typing import Optional, List
from gremlin_python.process.graph_traversal import __
from ..core.interfaces import EntityManager
from ..core.domain import BaseEntity
from .models import Station

class StationRepository:
    """
    Repository for Station entities.
    Acts like a Spring Data JpaRepository.
    """
    def __init__(self, em: EntityManager):
        self.em = em

    def find_by_name(self, name: str) -> Optional[Station]:
        """Finds a station by its unique name."""
        return self.em.find_by_property(Station, "name", name)

    def save(self, station: Station) -> Station:
        """
        Upsert logic (Update or Insert).
        Checks if the station exists based on the name (Business Key).
        """
        # 1. Check if it already exists in the DB
        existing_station = self.find_by_name(station.name)

        if existing_station:
            # Update the local object with the DB ID to ensure relationships work
            station.id = existing_station.id
            return station
        
        print(f"  [+] Creating new Station: '{station.name}'")
        return self.em.persist(station)

    def find_shortest_path(self, start_name: str, end_name: str) -> List[str]:
        """
        Finds the shortest path (by hops) between two stations.
        Returns an alternating list: [StationName, LineName, StationName, LineName, ...]
        """
        # 1. Retrieve IDs (Validation)
        start_node = self.find_by_name(start_name)
        end_node = self.find_by_name(end_name)

        if not start_node or not end_node:
            print(f"  [!] Error: Station not found ({start_name} or {end_name})")
            return []

        print(f"  [Repo] Searching path with lines: {start_name} -> {end_name}")

        try:
            # 2. Native Gremlin Query logic
            # We assume self.em.g gives access to the GraphTraversalSource
            # Logic:
            #   - Start at source
            #   - Repeat (Out Edge -> In Vertex)
            #   - Until target is reached
            #   - Path() with modulators: .by('name') for Vertex, .by('line') for Edge
            
            path_result = (
                self.em.g.V(start_node.id)
                .repeat(__.outE().inV().simplePath())
                .until(__.hasId(end_node.id))
                .path()
                .by('name')   # First by() applies to Vertices
                .by('line')   # Second by() applies to Edges
                .limit(1)
                .next()
            )
            
            # Result example: ['Station A', '1', 'Station B', '1', 'Station C']
            return path_result

        except StopIteration:
            return [] # No path found
        except Exception as e:
            print(f"Gremlin Error: {e}")
            return []