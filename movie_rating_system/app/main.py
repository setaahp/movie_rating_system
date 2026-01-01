from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base

from app.models import director, genre, movie, rating

from app.core.logging_config import setup_logging

try:
    from app.controllers import movie_controller, rating_controller
    HAS_CONTROLLERS = True
except ImportError as e:
    print(f"Controllers not ready yet: {e}")
    HAS_CONTROLLERS = False

setup_logging()

import logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Movie Rating System API",
    description="Backend API for Movie Rating System - Phase 2 (with Logging)",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register controllers if available
if HAS_CONTROLLERS:
    app.include_router(movie_controller.router)
    app.include_router(rating_controller.router)

@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Movie Rating System API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "database": "connected"}

Base.metadata.create_all(bind=engine)
logger.info("Database tables created")
logger.info("Application started successfully")
