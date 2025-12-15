import sys
import os
from typing import Tuple, Type, Any, List
from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

# --- CORRECTION DU BUG ---
# On construit la liste des fichiers dynamiquement.
# On filtre pour enlever 'None' si la variable d'env n'est pas définie.
_potential_files = [".env", os.getenv("SOLTANIA_CONFIG_PATH")]
ACTIVE_ENV_FILES = tuple(f for f in _potential_files if f)

# --- 1. Source personnalisée pour les Arguments CLI ---
class CliArgsSettingsSource(PydanticBaseSettingsSource):
    """
    Simule le comportement '-Dkey=value'.
    Lit les arguments passés au script sous la forme --nom_variable=valeur
    """
    def get_field_value(self, field: Any, field_name: str) -> Tuple[Any, str, bool]:
        prefix = f"--{field_name}="
        for arg in sys.argv:
            if arg.startswith(prefix):
                return arg[len(prefix):], field_name, False
        return None, field_name, False

    def prepare_field_value(self, field_name: str, field: Any, value: Any, value_is_complex: bool) -> Any:
        return value

    def __call__(self) -> dict[str, Any]:
        d = {}
        for field_name, field in self.settings_cls.model_fields.items():
            val, _, _ = self.get_field_value(field, field_name)
            if val is not None:
                d[field_name] = val
        return d

# --- 2. La Classe de Configuration Principale ---
class AppConfig(BaseSettings):
    """
    Définition centralisée de la configuration.
    """
    
    # Définition des variables (insensible à la casse)
    gremlin_host: str = Field(default="localhost", description="IP du serveur Gremlin")
    gremlin_port: int = Field(default=8182, description="Port du serveur Gremlin")
    gremlin_protocol: str = Field(default="ws", description="Protocole (ws ou wss)")

    @property
    def gremlin_url(self) -> str:
        """Helper pour construire l'URL complète"""
        return f"{self.gremlin_protocol}://{self.gremlin_host}:{self.gremlin_port}/gremlin"

    # --- 3. Configuration de la hiérarchie de chargement ---
    model_config = SettingsConfigDict(
        # Utilisation de la liste filtrée (sans None)
        env_file=ACTIVE_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            CliArgsSettingsSource(settings_cls), # 1. Arguments CLI
            dotenv_settings,                     # 2. .env files
            env_settings,                        # 3. Env Vars systeme
            init_settings,                       # 4. Defaults
        )

# Instanciation unique
settings = AppConfig()