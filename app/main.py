import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.auth.routers import router as auth_router
from app.jobs.routers import router as jobs_router
from app.resumes.routers import router as resume_router
from app.matching.routers import router as matching_router
from app.core.config import settings
from app.core.embedding_service import EmbeddingService


logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    EmbeddingService()
    yield


app = FastAPI(root_path="/api", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(matching_router)
