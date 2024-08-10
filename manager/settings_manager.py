from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    TENANT_NAME: str = ""
    APP_CLIENT_ID: str = ""
    APP_CLIENT_SECRET: str = ""
    OPENAPI_CLIENT_ID: str = ""
    AUTH_POLICY_NAME: str = ""
    SCOPE_DESCRIPTION: str = "user_impersonation"
    REDIRECT_URI: str = "http://localhost:8000/signin-oidc"
    APP_CLIENT_ID: str = ""
    AZURE_AD_ISSUER: str = ""
    AZURE_AD_JWKS_URI: str = ""

    @computed_field
    @property
    def SCOPE_NAME(self) -> str:
        return f"https://{self.TENANT_NAME}.onmicrosoft.com/{self.APP_CLIENT_ID}/{self.SCOPE_DESCRIPTION}"

    @computed_field
    @property
    def SCOPES(self) -> dict:
        return {self.SCOPE_NAME: self.SCOPE_DESCRIPTION}

    @computed_field
    @property
    def OPENID_CONFIG_URL(self) -> dict:
        return f"https://{self.TENANT_NAME}.b2clogin.com/{self.TENANT_NAME}.onmicrosoft.com/{self.AUTH_POLICY_NAME}/v2.0/.well-known/openid-configuration"

    @computed_field
    @property
    def OPENAPI_AUTHORIZATION_URL(self) -> dict:
        return f"https://{self.TENANT_NAME}.b2clogin.com/{self.TENANT_NAME}.onmicrosoft.com/{self.AUTH_POLICY_NAME}/oauth2/v2.0/authorize"

    @computed_field
    @property
    def OPENAPI_TOKEN_URL(self) -> dict:
        return f"https://{self.TENANT_NAME}.b2clogin.com/{self.TENANT_NAME}.onmicrosoft.com/{self.AUTH_POLICY_NAME}/oauth2/v2.0/token"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )