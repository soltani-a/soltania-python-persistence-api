from typing import Optional, List, Dict, Any
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import Order

from soltania_persistence.core.interfaces import EntityManager
from soltania_persistence.examples.learning_paths.models import LearningUnit, Dependency

class CurriculumRepository:
    def __init__(self, em: EntityManager):
        self.em = em

    def find_by_slug(self, slug: str) -> Optional[LearningUnit]:
        """Finds a unit by its unique slug."""
        return self.em.find_by_property(LearningUnit, "slug", slug)

    def save_unit(self, unit: LearningUnit) -> LearningUnit:
        """Upserts a learning unit."""
        existing = self.find_by_slug(unit.slug)
        if existing:
            unit.id = existing.id
            return unit
        return self.em.persist(unit)

    def add_prerequisite(self, prerequisite: LearningUnit, target: LearningUnit):
        """
        Creates a directional link: Prereq -> Target.
        Meaning: Prereq LEADS TO Target.
        """
        rel = Dependency(type="required")
        self.em.create_relationship(prerequisite, target, rel)

    def get_roadmap(self, target_slug: str) -> List[Dict]:
        """
        Generates the full learning path to reach a specific target.
        It traverses the graph BACKWARDS (who leads to me?) recursively.
        """
        target = self.find_by_slug(target_slug)
        if not target:
            return []

        print(f"🎓 Building roadmap for: {target.title}...")

        # GREMLIN QUERY:
        # 1. Start at target
        # 2. Repeat: go INcoming edges (leads_to) to find prerequisites
        # 3. Until no more prerequisites
        # 4. Emit everything found
        # 5. Deduplicate and return as a path list
        
        try:
            path = (
                self.em.g.V(target.id)
                .repeat(__.inE().outV().simplePath())
                .until(__.inE().count().is_(0))
                .emit()
                .path()
                .by(__.elementMap())
                .toList()
            )
            return path
        except Exception as e:
            print(f"❌ Error building roadmap: {e}")
            return []