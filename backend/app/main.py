from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routers import chat, documents, providers, usage


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="help-me-learn", lifespan=lifespan)

# Local personal app: accept any localhost port (Next.js auto-shifts ports
# when the default one is busy).
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(providers.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(usage.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
