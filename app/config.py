# ============================================================
# config.py — All app settings live here
# Reads values from the .env file so secrets stay out of code
# ============================================================

from pydantic_settings import BaseSettings  # pip install pydantic-settings

class Settings(BaseSettings):
    # --- MongoDB ---
    MONGO_URI: str = "mongodb://localhost:27017"   # Default: local MongoDB
    MONGO_DB_NAME: str = "industrial_ai"           # Name of our database

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379"      # Default: local Redis

    # --- App ---
    APP_NAME: str = "Industrial AI Platform"
    DEBUG: bool = True                             # Set False in production

    class Config:
        env_file = ".env"                          # Load values from .env file
        # Example .env:
        # MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net
        # REDIS_URL=redis://localhost:6379

# Create one settings instance — import this everywhere
settings = Settings()
