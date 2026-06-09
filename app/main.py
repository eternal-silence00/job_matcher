from fastapi import FastAPI
from app.auth.routers import router as auth_router
from app.jobs.routers import router as jobs_router
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings



app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth_router)
app.include_router(jobs_router)