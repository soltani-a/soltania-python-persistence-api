from typing import Optional, List, Dict, Any
# Imports corrigés pour éviter les conflits
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import P, Operator, Order

from soltania_persistence.core.interfaces import EntityManager
from .models import Station, Connection

class MetroRepository:
    def __init__(self, em: EntityManager):
        self.em = em

    def find_by_name(self, name: str) -> Optional[Station]:
        return self.em.find_by_property(Station, "name", name)

    def save_station(self, station: Station) -> Station:
        existing = self.find_by_name(station.name)
        if existing:
            station.id = existing.id
            return station
        return self.em.persist(station)

    def save_connection(self, from_st: Station, to_st: Station, line: str, duration: int):
        conn = Connection(line=line, duration=duration)
        self.em.create_relationship(from_st, to_st, conn)
        self.em.create_relationship(to_st, from_st, conn)

    def find_fastest_path(self, start_name: str, end_name: str) -> Optional[Dict[str, Any]]:
        start_node = self.find_by_name(start_name)
        end_node = self.find_by_name(end_name)

        if not start_node or not end_node:
            print(f"❌ Station inconnue: {start_name} ou {end_name}")
            return None

        print(f"⏱️  Calcul de l'itinéraire le plus rapide : {start_name} -> {end_name} ...")

        try:
            # Notez l'utilisation de Operator.sum_ (avec underscore)
            result = (
                self.em.g.withSack(0.0)
                .V(start_node.id)
                .repeat(
                    __.outE().sack(Operator.sum_).by('duration').inV().simplePath()
                )
                .until(__.hasId(end_node.id))
                .order().by(__.sack(), Order.asc)
                .limit(1)
                .project('total_time', 'path_names', 'lines')
                .by(__.sack())
                .by(__.path().by('name'))
                .by(__.path().by('line'))
                .next()
            )
            return result

        except StopIteration:
            print("❌ Aucun chemin trouvé (StopIteration).")
            return None
        except Exception as e:
            print(f"⚠️ Gremlin Error: {e}")
            import traceback
            traceback.print_exc()
            return None