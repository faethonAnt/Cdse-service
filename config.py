
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    cdse_username: str
    cdse_password: str
    token_url: str = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    catalogue_url: str = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    catalogue_download_url: str = "https://download.dataspace.copernicus.eu/odata/v1/Products"

settings = Settings()