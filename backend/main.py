from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile , HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from sympy.polys.subresultants_qq_zz import res

from database import Base, engine
from routers import users, clients, documents

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



app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(documents.router, prefix="/api/documents",tags=["documents"])
@app.get("/", include_in_schema=False, name="home")
async def default(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="Home.html",
    )





















