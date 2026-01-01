from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from typing import Optional, List

from app.db.database import get_db

from app.schemas.movie_schema import ResponseModel
from app.schemas.rating_schema import ResponseRatingModel

from app.repositories.director_repository import DirectorRepository
from app.repositories.genre_repository import GenreRepository
from app.repositories.movie_repository import MovieRepository

from app.services.movie_service import MovieService

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])

# ---------------------------
# Dependency Injection
# ---------------------------
def get_movie_service(db: Session = Depends(get_db)):
    movie_repo = MovieRepository(db)
    director_repo = DirectorRepository()
    genre_repo = GenreRepository()
    return MovieService(movie_repo, director_repo, genre_repo)

# ---------------------------
# 1. Search movies (with filters)
# ---------------------------

@router.get("/search", response_model=ResponseModel)
def search_movies(
    title: Optional[str] = Query(None),
    release_year: Optional[int] = Query(None, ge=1800, le=2100),
    genres: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    service: MovieService = Depends(get_movie_service),
):
    data = service.list_movies(
        title=title,
        release_year=release_year,
        genres=genres,
        page=page,
        page_size=page_size,
    )
    return {"status": "success", "data": data}


# ---------------------------
# 2. List movies (pagination only)
# ---------------------------
@router.get("/list", response_model=ResponseModel)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    service: MovieService = Depends(get_movie_service),
):
    data = service.list_movies(page=page, page_size=page_size)
    total_items = data["total_items"]
    total_pages = (total_items + page_size - 1) // page_size

    return {
        "status": "success",
        "data": data,
        "pagination": {
            "current_page": page,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
            "total_pages": total_pages
        }
    }


# ---------------------------
# 3. List movies with ratings
# ---------------------------
@router.get("/ratings", response_model=ResponseRatingModel)
def list_movies_ratings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    title: Optional[str] = Query(None),
    release_year: Optional[int] = Query(None),
    genres: Optional[List[str]] = Query(None),
    service: MovieService = Depends(get_movie_service),
):
    items, total_items = service.list_movies_ratings(
        page=page,
        page_size=page_size,
        title=title,
        release_year=release_year,
        genres=genres,
    )

    total_pages = (total_items + page_size - 1) // page_size

    return {
        "status": "success",
        "data": {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None,
        }
    }


# ---------------------------
# 4. Get movie by ID
# ---------------------------
@router.get("/detail/{movie_id}", response_model=ResponseModel)
def get_movie(movie_id: int, service: MovieService = Depends(get_movie_service)):
    movie = service.get_movie_by_id(movie_id)
    return {"status": "success", "data": movie}

