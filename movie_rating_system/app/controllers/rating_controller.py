from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any

from sqlalchemy import func
from app.models.movie import Movie
from app.models.rating import Rating
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.rating_schema import RatingCreate
from app.services.rating_service import RatingService

router = APIRouter(prefix="/api/v1/movies/{movie_id}/ratings", tags=["ratings"])


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_rating(
    movie_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db)
):
    try:
        rating = RatingService.create_rating(db, movie_id, rating_data)
        return {"status": "success", "data": rating}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating rating: {str(e)}"
        )


@router.get("/", response_model=dict)
def get_movie_ratings(
    movie_id: int,
    db: Session = Depends(get_db)
):
    try:
        ratings = RatingService.get_movie_ratings(db, movie_id)
        return {"status": "success", "data": ratings}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ratings: {str(e)}"
        )


