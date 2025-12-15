import json
import os
from soltania_persistence.examples.learning_paths.models import LearningUnit
from soltania_persistence.examples.learning_paths.repositories.curriculum_repository import CurriculumRepository

class CurriculumImporter:
    def __init__(self, repo: CurriculumRepository, file_path: str):
        self.repo = repo
        self.file_path = file_path

    def run(self):
        if not os.path.exists(self.file_path):
            print(f"❌ File not found: {self.file_path}")
            return

        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        units_data = data.get("units", [])
        cache = {} # Cache to store created objects by slug

        print("🔄 PASS 1: Creating Learning Units...")
        for u in units_data:
            unit = LearningUnit(
                slug=u["id"],
                title=u["title"],
                category=u["category"],
                hours=u["hours"]
            )
            saved = self.repo.save_unit(unit)
            cache[u["id"]] = saved
            print(f"   ✅ Created: {u['title']}")

        print("🔗 PASS 2: Linking Prerequisites...")
        count = 0
        for u in units_data:
            target_slug = u["id"]
            prereqs = u.get("prerequisites", [])
            
            target_node = cache[target_slug]

            for p_slug in prereqs:
                if p_slug in cache:
                    source_node = cache[p_slug]
                    # Link: Source -> Leads To -> Target
                    self.repo.add_prerequisite(source_node, target_node)
                    count += 1
                else:
                    print(f"   ⚠️ Warning: Prerequisite '{p_slug}' not found for '{target_slug}'")

        print(f"✅ Import Complete: {len(cache)} units, {count} dependencies.")