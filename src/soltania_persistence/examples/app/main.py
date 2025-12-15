import sys
import os

# Ensure the package is in path if running as script
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../.."))
if src_path not in sys.path:
    sys.path.append(src_path)

from soltania_persistence.provider.tinkerpop.manager import GremlinEntityManager
from soltania_persistence.app.models import Station, Connection
from soltania_persistence.app.repositories import StationRepository

# Import the centralized configuration
from soltania_persistence.config import settings

def populate_metro():
    print(f"Connecting to GraphDB at: {settings.gremlin_url}")
    
    # Initialize EntityManager with config from settings
    em = GremlinEntityManager(settings.gremlin_url)
    station_repo = StationRepository(em)

    # Metro Data Definition
    lines = {
        "1": [
            "La Défense", "Esplanade de la Défense", "Pont de Neuilly", "Les Sablons",
            "Porte Maillot", "Argentine", "Charles de Gaulle - Étoile", "George V",
            "Franklin D. Roosevelt", "Champs-Élysées - Clemenceau", "Concorde",
            "Tuileries", "Palais Royal - Musée du Louvre", "Louvre - Rivoli",
            "Châtelet", "Hôtel de Ville", "Saint-Paul", "Bastille", "Gare de Lyon",
            "Reuilly - Diderot", "Nation", "Porte de Vincennes", "Saint-Mandé",
            "Bérault", "Château de Vincennes"
        ],
        "9": [
            "Pont de Sèvres", "Billancourt", "Marcel Sembat", "Porte de Saint-Cloud",
            "Exelmans", "Michel-Ange - Molitor", "Michel-Ange - Auteuil", "Jasmin",
            "Ranelagh", "La Muette", "Rue de la Pompe", "Trocadéro", "Iéna",
            "Alma - Marceau", "Franklin D. Roosevelt", "Saint-Philippe du Roule",
            "Miromesnil", "Saint-Augustin", "Havre - Caumartin",
            "Chaussée d'Antin - La Fayette", "Richelieu - Drouot", "Grands Boulevards",
            "Bonne Nouvelle", "Strasbourg - Saint-Denis", "République", "Oberkampf",
            "Saint-Ambroise", "Voltaire", "Charonne", "Rue des Boulets", "Nation",
            "Buzenval", "Maraîchers", "Porte de Montreuil", "Robespierre",
            "Croix de Chavaux", "Mairie de Montreuil"
        ]
    }

    try:
        # Optional: Clear DB for clean state (Be careful in prod!)
        # em.clear_database()

        for line_name, stations in lines.items():
            print(f"\n--- Processing Line {line_name} ---")
            previous_station = None

            for station_name in stations:
                # 1. Instantiate (Transient state)
                new_station = Station(name=station_name)
                
                # 2. Save (Managed state) via Repository
                current_station = station_repo.save(new_station)

                # 3. Link (Edges)
                if previous_station:
                    conn = Connection(line=line_name)
                    # Create bi-directional link
                    em.create_relationship(previous_station, current_station, conn)
                    em.create_relationship(current_station, previous_station, conn)

                previous_station = current_station
        
        print("\n✅ Migration completed successfully!")

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        em.close()

if __name__ == "__main__":
    populate_metro()