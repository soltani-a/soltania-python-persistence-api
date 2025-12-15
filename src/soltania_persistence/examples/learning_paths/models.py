from typing import ClassVar, Optional
from soltania_persistence.core.domain import BaseEntity, Relationship

class Topic(BaseEntity):
    """ ex: 'AWS VPC', 'Python Basics', 'Subnetting' """
    __label__: ClassVar[str] = "topic"
    name: str

class Certification(BaseEntity):
    """ ex: 'AWS Solutions Architect Associate' """
    __label__: ClassVar[str] = "certification"
    title: str

class Course(BaseEntity):
    """ ex: 'Ultimate AWS Network Course' """
    __label__: ClassVar[str] = "course"
    title: str
    platform: str = "Udemy"

# --- Relations ---

class Covers(Relationship):
    """ Course -> Topic (Un cours couvre un sujet) """
    __label__: ClassVar[str] = "covers"

class Requires(Relationship):
    """ Certification -> Topic (Une certif demande de connaitre un sujet) """
    __label__: ClassVar[str] = "requires"

class Prerequisite(Relationship):
    """ Course -> Course (Ordre suggéré) """
    __label__: ClassVar[str] = "depends_on"