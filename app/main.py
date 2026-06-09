from fastapi import FastAPI
from app.auth.router import router as auth_router
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings



app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth_router)