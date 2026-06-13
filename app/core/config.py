from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    REDIS_URL: str
    ALGORITHM: str = "HS256"
    BASE_URL: str = "http://localhost:8000"
    CLIENT_ID: str
    CLIENT_SECRET: str
    MINIO_USER: str
    MINIO_PASSWORD: str
    MINIO_URL: str
    MINIO_PUBLIC_URL: str
    GROQ_API_KEY: str
    RABBITMQ_URL: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str  
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAX_RESUME_SIZE_BYTES: int = 5 * 1024 * 1024
    
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()
    