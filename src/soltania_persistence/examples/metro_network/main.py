import sys
import os
import asyncio

# --- FIX WINDOWS ASYNCIO ERROR ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ---------------------------------

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../../"))
if src_path not in sys.path:
    sys.path.append(src_path)

from soltania_persistence.config import settings
from soltania_persistence.provider.tinkerpop.manager import GremlinEntityManager
from soltania_persistence.examples.metro_network.repositories import MetroRepository
from soltania_persistence.examples.metro_network.importer import NetworkImporter

def format_seconds(seconds):
    if not seconds: return "0s"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins} min {secs} sec"

def main():
    em = GremlinEntityManager(settings.gremlin_url)
    repo = MetroRepository(em)

    # Commande: "load"
    if len(sys.argv) > 1 and sys.argv[1] == "load":
        json_path = os.path.join(current_dir, "data", "lines.json")
        importer = NetworkImporter(repo, json_path)
        importer.run()
        em.close()
        return

    # Mode Recherche
    start = "La Défense"
    end = "Anvers"
    
    if len(sys.argv) >= 3:
        start = sys.argv[1]
        end = sys.argv[2]

    result = repo.find_fastest_path(start, end)

    if result:
        # --- DEBUG BLOCK (Au cas où ça plante encore) ---
        # print(f"DEBUG RAW RESULT: {result}") 
        # -----------------------------------------------
        
        try:
            total_time = result.get('total_time', 0)
            path_names = result.get('path_names', [])
            path_lines = result.get('lines', [])

            print(f"\n🚀 FASTEST ROUTE FOUND ({format_seconds(total_time)})")
            print("="*40)
            
            if path_names:
                print(f"📍 START: {path_names[0]}")
                
                for i in range(1, len(path_names)):
                    # Protection contre index out of bounds
                    line_info = "Subway/RER"
                    if i < len(path_lines) and path_lines[i]:
                        line_info = path_lines[i]
                    
                    print(f"    ⬇️  (Travel via {line_info})")
                    print(f"🚉 {path_names[i]}")
                    
                print("="*40)
                print(f"🏁 ARRIVAL: {path_names[-1]}")
            else:
                print("⚠️ Path found but empty names list.")
                
        except KeyError as e:
            print(f"❌ Erreur de structure de données : {e}")
            print(f"Contenu reçu : {result}")
    else:
        print(f"❌ No path found between '{start}' and '{end}'.")

    em.close()

if __name__ == "__main__":
    main()