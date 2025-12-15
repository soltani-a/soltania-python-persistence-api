from typing import Type, Any, Optional
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
# --- CORRECTION ICI : On importe T en tant que GremlinT pour éviter le conflit ---
from gremlin_python.process.traversal import T as GremlinT

from ...core.interfaces import EntityManager, T, R

class GremlinEntityManager(EntityManager):
    def __init__(self, url: str):
        self.connection = DriverRemoteConnection(url, "g")
        self.g = traversal().withRemote(self.connection)

    def persist(self, entity: T) -> T:
        # 1. Check if entity exists (Upsert logic)
        label = entity.__class__.__label__
        
        # We assume 'name' is a unique business key for this example
        if hasattr(entity, 'name'):
            # On vérifie si ça existe déjà
            traversal_check = self.g.V().has(label, 'name', entity.name)
            
            if traversal_check.hasNext():
                existing = traversal_check.elementMap().next()
                
                # --- CORRECTION : Utilisation de GremlinT pour lire l'ID ---
                # Gremlin renvoie souvent l'ID sous la clé T.id (enum) ou "id" (str)
                entity.id = existing.get(GremlinT.id, existing.get('id'))
                return entity

        # 2. Create new Vertex
        t = self.g.addV(label)
        
        # Iterate over Pydantic fields to set properties
        for key, value in entity.model_dump(exclude={'id'}).items():
            if value is not None:
                t = t.property(key, value)
        
        # Execute and get the created vertex
        vertex = t.next()
        entity.id = vertex.id
        # print(f"  [JPA] Persisted {label}: {getattr(entity, 'name', 'Unknown')}")
        return entity

    def find_by_property(self, entity_class: Type[T], key: str, value: Any) -> Optional[T]:
        label = entity_class.__label__
        try:
            # Fetch generic map
            data = self.g.V().has(label, key, value).elementMap().next()
            
            # --- CORRECTION : Nettoyage des clés Gremlin (T.id, T.label) ---
            clean_data = {}
            for k, v in data.items():
                if k == GremlinT.id:
                    clean_data['id'] = v
                elif k == GremlinT.label:
                    continue # On ignore le label dans l'objet Pydantic
                else:
                    clean_data[str(k)] = v # On garde les autres propriétés
            
            return entity_class(**clean_data)
        except StopIteration:
            return None

    def create_relationship(self, source: T, target: T, relation: R) -> None:
        if not source.id or not target.id:
            raise ValueError("Entities must be persisted before linking.")

        label = relation.__class__.__label__
        
        # Check if edge exists to avoid duplicates
        exists = self.g.V(source.id).outE(label).where(
            __.inV().hasId(target.id)
        ).hasNext()

        if exists:
            return

        # Start traversal from source
        t = self.g.V(source.id).addE(label).to(__.V(target.id))
        
        # Add properties to the edge
        for key, value in relation.model_dump().items():
             if value is not None:
                t = t.property(key, value)
        
        t.iterate()

    def clear_database(self):
        print("  [JPA] Clearing persistence context (Database)...")
        self.g.V().drop().iterate()

    def close(self):
        self.connection.close()