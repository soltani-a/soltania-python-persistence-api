import sys
import os
import asyncio

# --- WINDOWS FIX ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# -------------------

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../../"))
if src_path not in sys.path:
    sys.path.append(src_path)

from soltania_persistence.config import settings
from soltania_persistence.provider.tinkerpop.manager import GremlinEntityManager
from soltania_persistence.examples.learning_paths.repositories.curriculum_repository import CurriculumRepository
from soltania_persistence.examples.learning_paths.services.importer import CurriculumImporter

def get_prop(element_map, key):
    """Helper for elementMap extraction."""
    if not isinstance(element_map, dict): return str(element_map)
    if key in element_map: return element_map[key]
    for k, v in element_map.items():
        if str(k) == key: return v
    return "???"

def main():
    em = GremlinEntityManager(settings.gremlin_url)
    repo = CurriculumRepository(em)
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "drop":
        print("💥 Clearing database...")
        em.g.V().drop().iterate()
        em.close()
        return

    if cmd == "load":
        json_path = os.path.join(current_dir, "data", "curriculum.json")
        importer = CurriculumImporter(repo, json_path)
        importer.run()
        em.close()
        return

    if cmd == "roadmap":
        target_slug = sys.argv[2] if len(sys.argv) > 2 else "devops_pro"
        raw_paths = repo.get_roadmap(target_slug)
        
        print(f"\n🗺️  ROADMAP TO: {target_slug}")
        print("="*40)
        
        # Le résultat est une liste de chemins. Pour une roadmap linéaire simple,
        # on peut extraire tous les nœuds uniques rencontrés.
        
        seen = set()
        steps = []
        
        # Gremlin renvoie des chemins depuis la racine vers la feuille ou l'inverse selon le sens.
        # Ici on a traversé "in" (en arrière).
        
        for path_obj in raw_paths:
            # path_obj est une liste d'objets [Unit, Edge, Unit...]
            # On parcourt à l'envers pour avoir l'ordre chronologique (Base -> Avancé)
            nodes = [x for x in path_obj if isinstance(x, dict) and 'slug' not in str(x)] # Filtrer edges approximativement
            
            # Meilleure méthode : itérer sur les objets du path
            for item in reversed(path_obj):
                if isinstance(item, dict):
                    # C'est un noeud (elementMap)
                    slug = get_prop(item, 'slug')
                    title = get_prop(item, 'title')
                    if slug and slug not in seen and slug != "???":
                        seen.add(slug)
                        steps.append(title)

        # Affichage
        if steps:
            for i, title in enumerate(steps, 1):
                if i == len(steps):
                     print(f"🎯 OBJETIF : {title}")
                else:
                     print(f" {i}. {title}")
                     print(f"    ⬇️")
        else:
            print("No prerequisites found or target is a standalone course.")
            
        print("="*40)
        em.close()
        return

    print("Usage: python main.py [drop|load|roadmap <slug>]")
    em.close()

if __name__ == "__main__":
    main()