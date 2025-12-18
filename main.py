from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from fastapi.middleware.cors import CORSMiddleware
from db.base import init_db
from api.routes import router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title="Cocktail Club Hospitality – AI Recipe Fallback Service (v1)",
    description="API that accepts a user query and returns a structured JSON recipe response.",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Welcome to AI Recipe Fallback Service"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

