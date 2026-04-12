from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://modelplaza:changeme@localhost:5432/modelplaza"
    database_url_sync: str = "postgresql://modelplaza:changeme@localhost:5432/modelplaza"

    # Auth
    secret_key: str = "changeme-to-a-real-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Gitea
    gitea_url: str = "http://localhost:3000"
    gitea_admin_user: str = "gitea_admin"
    gitea_admin_password: str = "changeme"
    gitea_admin_token: str = ""

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "changeme"
    minio_bucket: str = "model-weights"
    minio_use_ssl: bool = False

    # Chain
    chain_rpc_url: str = "https://sepolia.base.org"
    chain_private_key: str = ""
    model_registry_address: str = ""

    model_config = {"env_file": "../../.env", "extra": "ignore"}


settings = Settings()
