from typing import Optional, ClassVar, Union
from datetime import datetime
from pydantic import BaseModel, Field

# --- DÉFINITION DE 'ID' (C'est ce qui manquait) ---
ID = Union[str, int]

class BaseEntity(BaseModel):
    """
    Base class for all persistent entities (equivalent to @Entity).
    Uses Pydantic for validation.
    """
    id: Optional[ID] = Field(default=None, description="Database ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    # --- AJOUT DU CHAMP MANQUANT ---
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Metadata to define the label in GraphDB or Table in SQL
    __label__: ClassVar[str]

    class Config:
        # Allows populating by field name even if an alias is defined
        populate_by_name = True

class Relationship(BaseModel):
    """
    Represents an Edge in a Graph Database.
    """
    __label__: ClassVar[str]