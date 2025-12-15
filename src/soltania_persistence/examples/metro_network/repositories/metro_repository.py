from typing import Optional, Dict, Any
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import P, Operator, Order

from soltania_persistence.core.interfaces import EntityManager
# Notice the clean import from the sibling 'models' package
from soltania_persistence.examples.metro_network.models import Station, Connection

class MetroRepository:
    def __init__(self, em: EntityManager):
        self.em = em

    def find_by_name(self, name: str) -> Optional[Station]:
        """Finds a station by its exact name."""
        return self.em.find_by_property(Station, "name", name)

    def save_station(self, station: Station) -> Station:
        """
        Upserts a station: checks if it exists by name, 
        returns the existing one ID if so, otherwise persists a new one.
        """
        existing = self.find_by_name(station.name)
        if existing:
            station.id = existing.id
            return station
        return self.em.persist(station)

    def save_connection(self, from_st: Station, to_st: Station, line: str, duration: int):
        """Creates a bidirectional relationship between two stations."""
        conn = Connection(line=line, duration=duration)
        self.em.create_relationship(from_st, to_st, conn)
        self.em.create_relationship(to_st, from_st, conn)

    def find_fastest_path(self, start_name: str, end_name: str) -> Optional[Dict[str, Any]]:
        """
        Calculates the shortest path using weighted edges (duration).
        Includes 'barrier' optimization to handle complex graphs without timeout.
        """
        start_node = self.find_by_name(start_name)
        end_node = self.find_by_name(end_name)

        if not start_node or not end_node:
            print(f"❌ Unknown station: {start_name} or {end_name}")
            return None

        print(f"⏱️  Calculating optimized route: {start_name} -> {end_name} ...")

        try:
            # Optimized A* / Beam Search logic
            result = (
                self.em.g.with_('evaluationTimeout', 90000) 
                .withSack(0.0)
                .V(start_node.id)
                .repeat(
                    __.outE()
                    .sack(Operator.sum_).by('duration')
                    .inV()
                    .simplePath()
                    # Keep only the top 100 fastest partial paths at each step
                    .order().by(__.sack(), Order.asc)
                    .barrier(100) 
                )
                .until(
                    __.hasId(end_node.id)
                    .or_().loops().is_(P.gt(40)) # Safety limit for path depth
                )
                .hasId(end_node.id)
                .order().by(__.sack(), Order.asc)
                .limit(1)
                .project('total_time', 'path_data')
                .by(__.sack())
                .by(__.path().by(__.elementMap())) 
                .next()
            )
            return result

        except StopIteration:
            print("❌ No path found (StopIteration).")
            return None
        except Exception as e:
            if "598" in str(e):
                print(f"⚠️ TIMEOUT: Graph complexity exceeded server limits.")
            else:
                print(f"⚠️ Gremlin Error: {e}")
            return None