from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    database_name: str
    database_usr: str
    database_psw: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)