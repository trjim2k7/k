from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Manages application settings, loading environment variables from a .env file.
    All environment variables are prefixed with the field name (case-sensitive).
    """

    # Model configuration for Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",  # Load environment variables from .env file
        extra="ignore",  # Ignore extra fields in .env not defined here
        case_sensitive=True,  # Environment variables are case-sensitive
    )

    # --- Database Settings ---
    DB_HOST: str = Field(
        default="localhost", description="Hostname for the PostgreSQL database connection."
    )
    DB_PORT: int = Field(
        default=5432, description="Port number for the PostgreSQL database connection."
    )
    DB_NAME: str = Field(description="Name of the PostgreSQL database.")
    DB_USER: str = Field(description="Username for connecting to the PostgreSQL database.")
    DB_PASSWORD: SecretStr = Field(description="Password for connecting to the PostgreSQL database.")
    DATABASE_ECHO: bool = Field(
        default=False, description="If True, SQLAlchemy will log all SQL statements."
    )
    DATABASE_POOL_SIZE: int = Field(
        default=10, description="The number of connections to keep in the connection pool."
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=20, description="The number of connections that can be opened beyond the pool_size."
    )

    @property
    def DATABASE_URL(self) -> str:
        """
        Constructs the SQLAlchemy database URL from individual database settings.
        Uses `postgresql+asyncpg` for async PostgreSQL drivers, which is common
        with FastAPI.
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # --- JWT Authentication Settings ---
    SECRET_KEY: SecretStr = Field(
        description="The secret key for signing JWT tokens. "
        "MAKE SURE TO CHANGE THIS IN PRODUCTION TO A STRONG, RANDOM VALUE!"
    )
    ALGORITHM: str = Field(
        default="HS256", description="The algorithm used for JWT token signing (e.g., 'HS256')."
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="The number of minutes after which an access token expires."
    )


# Instantiate settings to be imported throughout the application.
# This ensures that environment variables are loaded only once.
settings = Settings()