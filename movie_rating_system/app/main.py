from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
import uvicorn

# Import models
from app.models import director, genre, movie, rating

# Import controllers
try:
    from app.controllers import movie_controller, rating_controller
    HAS_CONTROLLERS = True
except ImportError as e:
    print(f"⚠️  Controllers not ready yet: {e}")
    HAS_CONTROLLERS = False

app = FastAPI(
    title="Movie Rating System API",
    description="Backend API for Movie Rating System - Phase 1",
    version="1.0.0",
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
    return {
        "message": "Welcome to Movie Rating System API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Run server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"] 
    )
