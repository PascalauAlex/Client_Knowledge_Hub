import os.path
from contextlib import asynccontextmanager


from fastapi import FastAPI, UploadFile , HTTPException, status
from fastapi.middleware.cors import CORSMiddleware


from database import Base, engine
from routers import users, clients, documents



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

image = os.path.dirname("")

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(documents.router, prefix="/api/documents",tags=["documents"])
@app.get("/")
async def default():
    return {"default":"default"}





















