import json
import os
from soltania_persistence.examples.metro_network.models import Station
from soltania_persistence.examples.metro_network.repositories import MetroRepository

class NetworkImporter:
    def __init__(self, repo: MetroRepository, file_path: str):
        self.repo = repo
        self.file_path = file_path

    def run(self):
        if not os.path.exists(self.file_path):
            print(f"❌ File not found: {self.file_path}")
            return

        print(f"📖 Reading network data from {self.file_path}...")
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_stations = 0
        total_connections = 0

        # Iterate over Types (METRO, RER, TRAM)
        for transport_type, type_data in data.items():
            avg_time = type_data.get("avg_stop_time", 90)
            lines = type_data.get("lines", {})

            print(f"   Processing {transport_type} lines...")

            for line_name, stations_list in lines.items():
                # Nom complet de la ligne (ex: "M1", "RER A")
                full_line_name = f"{transport_type} {line_name}" if transport_type != "METRO" else line_name
                
                previous_station = None

                for station_name in stations_list:
                    # 1. Upsert Station
                    current_station = self.repo.save_station(Station(name=station_name))
                    total_stations += 1

                    # 2. Link with previous if exists
                    if previous_station:
                        # On applique l'heuristique de temps (Durée moyenne)
                        # Pourrait être amélioré avec une vraie distance si on avait les GPS
                        self.repo.save_connection(
                            from_st=previous_station,
                            to_st=current_station,
                            line=full_line_name,
                            duration=avg_time
                        )
                        total_connections += 1
                    
                    previous_station = current_station
        
        print(f"✅ Import Complete: {total_stations} processed stations, {total_connections} links created.")