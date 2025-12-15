import sys
import os

# Ensure the package is in path if running as script
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../.."))
if src_path not in sys.path:
    sys.path.append(src_path)

from soltania_persistence.provider.tinkerpop.manager import GremlinEntityManager
from soltania_persistence.app.repositories import StationRepository
from soltania_persistence.config import settings

def parse_stations():
    """
    Extracts start and end stations from command line arguments.
    Filters out arguments starting with '--' used for configuration.
    """
    # Filter out config flags (e.g. --gremlin_host=...)
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    
    if len(args) >= 2:
        return args[0], args[1]
    
    return "La Défense", "Château de Vincennes"

def main():
    # 1. Parse Station Arguments
    start, end = parse_stations()

    print(f"Configuration loaded: {settings.gremlin_url}")
    print(f"Request: Path from '{start}' to '{end}'")

    # 2. Init Context
    em = GremlinEntityManager(settings.gremlin_url)
    repo = StationRepository(em)

    try:
        # 3. Execute Business Logic
        path = repo.find_shortest_path(start, end)

        if path:
            print(f"\n✅ ITINERARY FOUND ({len(path)//2} stops):")
            print("=" * 40)
            
            # Display Start
            print(f"📍 START: {path[0]}")
            
            # Loop through the rest in chunks of 2: [Line, Station]
            for i in range(1, len(path), 2):
                line_name = path[i]
                station_name = path[i+1]
                
                print(f"    ⬇️  (Take Line {line_name})")
                print(f"🚉 {station_name}")
                
            print("=" * 40)
            print("🏁 ARRIVAL")
        else:
            print("\n❌ No path found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        em.close()

if __name__ == "__main__":
    main()