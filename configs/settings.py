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
    debug: bool = False  # Add debug flag
    use_https: bool = False  # Add HTTPS flag for cookie security

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.secret_key:
            raise ValueError("SECRET_KEY is required for JWT authentication")


# admin_login.html (just the JavaScript part)

'''
if (response.ok) {
    const data = await response.json();
    // Store token in localStorage if needed
    localStorage.setItem('accessToken', data.access_token);

    // Set a cookie ourselves to be doubly sure
    document.cookie = `token=${data.access_token}; path=/; max-age=${60*60};`;

    // Redirect to admin panel
    window.location.href = '/admin';
}
'''