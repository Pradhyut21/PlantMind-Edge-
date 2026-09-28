import os
from pydantic_settings import BaseSettings

class EdgeSettings(BaseSettings):
    app_name: str = "PlantMind Edge Kiosk API"
    host: str = "0.0.0.0"
    port: int = 8000
    device_id: str = os.getenv("DEVICE_ID", "kiosk-1")
    storage_base: str = os.getenv("EDGE_STORAGE_BASE", "./data/edge_devices")
    cloud_api_url: str = os.getenv("CLOUD_API_URL", "http://127.0.0.1:8001")
    is_offline_simulation: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_device_storage_path(self, dev_id: str = None) -> str:
        d = dev_id or self.device_id
        return os.path.join(self.storage_base, d)

edge_settings = EdgeSettings()
