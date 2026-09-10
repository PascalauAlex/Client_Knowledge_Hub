from contextlib import asynccontextmanager
from typing import Callable
from fastapi import FastAPI, UploadFile , HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from sympy.polys.subresultants_qq_zz import res
from database import DbSession
from database import  engine
from routers import users, clients, documents
from sqlalchemy import text

templates = Jinja2Templates(directory="templates")

origins = [
    "http://localhost:5173"
]

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)



app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable):
    response = await call_next(request)

    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"

    if "Referrer-Policy" not in response.headers:
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.hostname not in ("localhost","127.0.0.1"):
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )

    return response



app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(documents.router, prefix="/api/documents",tags=["documents"])


@app.get("/health")
async def health_check(db : DbSession):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc
    return {"status":"health"}

@app.get("/", include_in_schema=False, name="home")
async def default(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="Home.html",
    )





















