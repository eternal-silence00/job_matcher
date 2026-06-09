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
    GROQ_API_KEY: str
    
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()
    