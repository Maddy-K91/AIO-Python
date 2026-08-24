from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routes.user_routes import router as user_router
from app.routes.marketplace_routes import router as marketplace_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Authentication API",
        description="REST API for user authentication",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    settings.media_directory.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=settings.media_directory), name="media")

    api_router = APIRouter()
    api_router.include_router(user_router)
    api_router.include_router(marketplace_router)
    app.include_router(api_router)

    @app.get("/api/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "message": "API is running"}

    @app.get("/", tags=["Info"])
    async def root() -> dict[str, object]:
        return {
            "message": "Welcome to Authentication API",
            "docs": "/docs",
            "endpoints": {
                "health": "/api/health",
                "register": "/api/register",
                "login": "/api/login",
            },
        }

    return app


app = create_app()