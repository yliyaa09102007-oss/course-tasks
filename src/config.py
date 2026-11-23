"""Configuration module for PostgreSQL db connection settings"""

import os

from dataclasses import asdict, dataclass
from typing import Any

@dataclass(frozen = True)
class DatabaseConfig:
    """Immutable configuration container for PostgreSQL connection parameters.
    
    Field names match the keyword arguments expected by psycopg2.connect().

    Attributes:
        host: Database server hostname or IP address.
        port: Database server port number.
        dbname: Target PostgreSQL database name.
        user: Username for authentication.
        password: Password for authentication.
    """

    host: str
    port: int
    dbname: str
    user: str
    password: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the configuration dataclasses into a dict for psycopg2.connect"""
        return asdict(self)

def load_db_config() -> DatabaseConfig:
    """Load database configuration from env variables with fallback defaults
    
    Returns:
        Immutable DBConfig instance populated with connection settings.

    Raises:
        ValueError: If the DB_PORT environment variable cannot be converted to an integer.
    """

    return DatabaseConfig(
        host = os.getenv("DB_HOST", "localhost"),
        port = int(os.getenv("DB_PORT", "5432")),
        dbname = os.getenv("DB_NAME", "rooms_db"),
        user = os.getenv("DB_USER", "de"),
        password = os.getenv("DB_PASSWORD", "secret")
    )