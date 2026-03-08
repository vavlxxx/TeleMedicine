from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

BASE_DIR = Path(__file__).resolve().parent.parent


class DbSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    name: str = "telemedicine"
    name_test: str = "telemedicine_test"
    echo: bool = False

    @property
    def async_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.name,
        )


class AppSettings(BaseModel):
    title: str = "TeleMedicine API"
    mode: Literal["DEV", "TEST", "PROD"] = "DEV"
    api_prefix: str = "/api"
    v1_prefix: str = "/v1"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    openapi_url: str | None = "/openapi.json"


class JwtSettings(BaseModel):
    secret_key: SecretStr = SecretStr("change-me-please-in-prod-very-long-secret")
    algorithm: str = "HS256"
    access_ttl_minutes: int = 15
    refresh_ttl_days: int = 30
    issuer: str = "telemedicine-backend"
    audience: str = "telemedicine-frontend"
    refresh_cookie_name: str = "refresh_token"
    refresh_cookie_path: str = "/api/v1/auth"
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None


class CorsSettings(BaseModel):
    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    allow_credentials: bool = True
    allow_methods: list[str] = Field(default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    allow_headers: list[str] = Field(default_factory=lambda: ["Authorization", "Content-Type", "X-Requested-With"])

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


class UploadSettings(BaseModel):
    directory: Path = BASE_DIR / "uploads" / "doctor_documents"
    max_file_size_mb: int = 8
    max_files_per_request: int = 10
    allowed_extensions: set[str] = {"pdf", "png", "jpg", "jpeg", "webp"}
    allowed_mime_types: set[str] = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/webp",
    }

    @field_validator("allowed_extensions", "allowed_mime_types", mode="before")
    @classmethod
    def parse_collection(cls, value: set[str] | list[str] | str) -> set[str]:
        if isinstance(value, str):
            return {item.strip().lower() for item in value.split(",") if item.strip()}
        return {item.lower() for item in value}


class GunicornSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    timeout: int = 120
    worker_class: str = "uvicorn.workers.UvicornWorker"
    access_log: str | None = "-"
    error_log: str | None = "-"
    reload: bool = False


class UvicornSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


class BootstrapSettings(BaseModel):
    superuser_username: str | None = None
    superuser_password: SecretStr | None = None
    superuser_first_name: str | None = "System"
    superuser_last_name: str | None = "Administrator"


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    app: AppSettings = AppSettings()
    auth: JwtSettings = JwtSettings()
    cors: CorsSettings = CorsSettings()
    upload: UploadSettings = UploadSettings()
    gunicorn: GunicornSettings = GunicornSettings()
    uvicorn: UvicornSettings = UvicornSettings()
    bootstrap: BootstrapSettings = BootstrapSettings()

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="CFG_",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        if self.app.mode == "PROD":
            if self.auth.secret_key.get_secret_value() == "change-me-please-in-prod-very-long-secret":
                raise ValueError("Set a strong CFG_AUTH__SECRET_KEY for PROD mode")
            if not self.auth.cookie_secure:
                raise ValueError("CFG_AUTH__COOKIE_SECURE must be true for PROD mode")
        return self


settings = Settings()
