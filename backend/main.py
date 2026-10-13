from contextlib import asynccontextmanager
from typing import Callable
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.util import ellipses_string
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from slowapi import Limiter
from config import settings
from database import DbSession
from database import engine
from rag.cache import Cache
from rag.security import SecurityPipeline
from routers import users, clients, documents
from sqlalchemy import text
from rag.monitoring import JSONFormatter, MetricsCollector, get_logger
from schemas import CacheStatsResponse

templates = Jinja2Templates(directory="templates")

origins = ["http://localhost:5173"]



# === Global instances (initialized at lifespan) ===
security : SecurityPipeline = None
metrics : MetricsCollector = None
cache : Cache = None


logger = get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global security, metrics, cache

    print("="*150)
    logger.info(msg="Starting Client Knowledge Hub...",extra={"extra_data":{
        "environment":settings.app_env,
        "primary_model":settings.primary_model,
        "tracing_enabled": True if settings.langsmith_tracing else False
    }})

    # Initialize components
    security = SecurityPipeline()
    cache = Cache()
    metrics = MetricsCollector()


    logger.info(msg="All components initialized. Ready to server requests.")
    yield
    print("="*150)
    logger.info("Lifespan metrics: ", extra={"extra_data":metrics.summary})
    # Shutdown
    print("="*150)
    logger.info("Disposing database...")
    await engine.dispose()
    logger.info("Database disposed SUCCESSFULLY!")
    logger.info("Application shutting down.")


# Rater limiter based on IP address of each request
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(lifespan=lifespan,
              title="Client_Knowledge_Hub API",
              description="RAG System based on pgvector extension over client documents with security, monitoring and caching layers for providing a production ready enviroment.",
              version="1.0.0")

app.state.limiter = limiter



app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable):
    response = await call_next(request)

    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"

    if "Referrer-Policy" not in response.headers:
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.hostname not in ("localhost", "127.0.0.1"):
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )

    return response

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceed errors"""
    logger.warning("Rate limit exceeded.",extra={
        "extra_data":{
            'client_ip':get_remote_address(request)
        }
    })
    return JSONResponse(
        status_code=429,
        content={
            "error":"Rate limit exceeded.",
            "detail":"Too many requests, please slow down."
        }
    )



app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])


@app.get("/health")
async def health_check(db: DbSession):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable"
        ) from exc
    return {"status": "health"}


@app.get("/", include_in_schema=False, name="home")
async def default(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="Home.html",
    )

@app.get("/cache_stats",response_model=CacheStatsResponse, status_code=status.HTTP_200_OK)
async def cache_stats():
    stats = cache.get_stats
    return stats

