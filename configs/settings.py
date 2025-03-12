from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    database_name: str
    database_usr: str
    database_psw: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.secret_key:
            raise ValueError("SECRET_KEY is required for JWT authentication")
