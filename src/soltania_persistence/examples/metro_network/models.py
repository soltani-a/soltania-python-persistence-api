from typing import ClassVar
from pydantic import Field
from soltania_persistence.core.domain import BaseEntity, Relationship

class Station(BaseEntity):
    """ Représente une station (Sommet/Vertex) """
    __label__: ClassVar[str] = "station"
    name: str

class Connection(Relationship):
    """ 
    Représente un tronçon de voie (Arête/Edge).
    Contient maintenant le POIDS (Weight) pour l'algo de chemin.
    """
    __label__: ClassVar[str] = "link"
    line: str
    
    # Nouveaux champs pour le calcul pondéré
    duration: int = Field(..., description="Durée du trajet en secondes")
    distance: int = Field(default=0, description="Distance en mètres")