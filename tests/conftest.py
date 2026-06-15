import pytest
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.main import app
from app.core.database import get_db
from app.core.base import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@db_test:5432/job_matcher_test"
)

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

async def override_get_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

@pytest.fixture(scope="session")
async def async_client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
    

@pytest.fixture
async def client_with_token(async_client):
    await async_client.post("/auth/register", json={
        "email": "test@mail.com",
        "password": "test12345"
    })
    response = await async_client.post("/auth/login", json={
        "email": "test@mail.com",
        "password": "test12345"
    })
    token = response.json()["access_token"]
    async_client.headers["Authorization"] = f"Bearer {token}"
    yield async_client
    async_client.headers.pop("Authorization", None)
    
    
@pytest.fixture
async def admin_client_with_token(async_client):
    await async_client.post("/auth/register", json={
        "email": "admin@mail.com",
        "password": "admin12345"
    })
    
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE users SET role = 'admin' WHERE email = 'admin@mail.com'"))
    await engine.dispose()
    
    response = await async_client.post("/auth/login", json={
        "email": "admin@mail.com",
        "password": "admin12345"
    })
    token = response.json()["access_token"]
    async_client.headers["Authorization"] = f"Bearer {token}"
    yield async_client
    async_client.headers.pop("Authorization", None)
    
    
@pytest.fixture(autouse=True)
async def clean_db():
    yield
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE users, jobs, resumes RESTART IDENTITY CASCADE"))
    await engine.dispose()