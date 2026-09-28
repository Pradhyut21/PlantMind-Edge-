import os
from pydantic_settings import BaseSettings

class CloudSettings(BaseSettings):
    app_name: str = "PlantMind Central Cloud API"
    host: str = "0.0.0.0"
    port: int = 8001
    storage_dir: str = os.getenv("CLOUD_STORAGE_DIR", "./data/cloud_storage")
    qdrant_url: str = os.getenv("QDRANT_URL", "")  # Empty means embedded local at storage_dir/qdrant
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

cloud_settings = CloudSettings()
