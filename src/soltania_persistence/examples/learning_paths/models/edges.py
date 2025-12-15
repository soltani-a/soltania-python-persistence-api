from soltania_persistence.core.domain import Relationship

class Dependency(Relationship):
    """
    Represents a prerequisite link: Unit A --leads_to--> Unit B.
    Meaning: You must finish A to start B.
    """
    __label__ = "leads_to"

    type: str = "required" # 'required' or 'optional'