import sys
import os
import asyncio

# --- WINDOWS COMPATIBILITY ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# -----------------------------

# Add the project root to sys.path to ensure absolute imports work correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../../"))
if src_path not in sys.path:
    sys.path.append(src_path)

from soltania_persistence.config import settings
from soltania_persistence.provider.tinkerpop.manager import GremlinEntityManager

# Imports from the new sub-folders
from soltania_persistence.examples.metro_network.repositories.metro_repository import MetroRepository
from soltania_persistence.examples.metro_network.services.importer import NetworkImporter

def format_seconds(seconds):
    if not seconds: return "0s"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins} min {secs} sec"

def get_prop(element_map, key):
    """Robust helper to extract values from Gremlin elementMap (handles both String and T.key)."""
    if not isinstance(element_map, dict): return str(element_map)
    if key in element_map: return element_map[key]
    for k, v in element_map.items():
        if str(k) == key: return v
    return "???"

def main():
    em = GremlinEntityManager(settings.gremlin_url)
    repo = MetroRepository(em)
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else None

    # --- DROP MODE ---
    if cmd == "drop":
        print("💥 Deleting all data in the database...")
        try:
            em.g.V().drop().iterate()
            print("✅ Database cleared.")
        except Exception as e: print(f"❌ Error: {e}")
        finally: em.close()
        return

    # --- LOAD MODE ---
    if cmd == "load":
        # Pointing to the 'data' subfolder
        json_path = os.path.join(current_dir, "data", "lines.json")
        importer = NetworkImporter(repo, json_path)
        importer.run()
        em.close()
        return

    # --- SEARCH MODE ---
    start = sys.argv[1] if len(sys.argv) >= 3 else "Mairie des Lilas"
    end = sys.argv[2] if len(sys.argv) >= 3 else "Chelles - Gournay"

    result = repo.find_fastest_path(start, end)

    if result:
        try:
            total_time = result.get('total_time', 0)
            path_data = result.get('path_data', [])

            print(f"\n🚀 FASTEST ROUTE ({format_seconds(total_time)})")
            print("="*50)
            
            if path_data:
                start_node = path_data[0]
                print(f"📍 START : {get_prop(start_node, 'name')}")
                
                previous_line = None

                # Iterate path (Edge -> Vertex -> Edge -> Vertex)
                for i in range(1, len(path_data), 2):
                    edge = path_data[i]
                    next_node = path_data[i+1]
                    
                    line_name = get_prop(edge, 'line')
                    station_name = get_prop(next_node, 'name')
                    
                    # Smart Display Logic
                    if line_name != previous_line:
                        icon = "🚄" if "RER" in str(line_name) else "🚇"
                        
                        if previous_line is None:
                            print(f"\n   ⬇️  TAKE {icon} {line_name}")
                        else:
                            print(f"\n   🔄 TRANSFER : Take {icon} {line_name}")
                            
                    print(f"      ▪️ {station_name}")
                    previous_line = line_name
                    
                print("="*50)
                print(f"🏁 ARRIVAL : {get_prop(path_data[-1], 'name')}")
            else:
                print("⚠️ Path found but data is empty.")

        except Exception as e:
            print(f"❌ Display Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ No path found between '{start}' and '{end}'.")

    em.close()

if __name__ == "__main__":
    main()