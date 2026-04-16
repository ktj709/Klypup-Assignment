import logging
import time
import uuid

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.orgs import router as orgs_router
from app.api.routes.research import router as research_router
from app.api.routes.reports import router as reports_router
from app.api.routes.watchlist import router as watchlist_router
from app.core.config import get_settings
from app.db.session import Base, engine

settings = get_settings()
logger = logging.getLogger("klypup.api")

if settings.request_logging_enabled:
    logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(orgs_router, prefix=settings.api_v1_prefix)
app.include_router(reports_router, prefix=settings.api_v1_prefix)
app.include_router(research_router, prefix=settings.api_v1_prefix)
app.include_router(watchlist_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    if settings.request_logging_enabled:
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

    response.headers["x-request-id"] = request_id
    return response


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
