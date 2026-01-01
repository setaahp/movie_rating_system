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
import logging
from datetime import datetime

router = APIRouter(prefix="/api/v1/movies/{movie_id}/ratings", tags=["ratings"])

logger = logging.getLogger(__name__)
api_logger = logging.getLogger("api")


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_rating(
    movie_id: int,
    rating_data: RatingCreate,
    db: Session = Depends(get_db)
):
    # Log
    logger.info(f"API Request: POST /api/v1/movies/{movie_id}/ratings - rating={rating_data.score}")
    api_logger.info(f"Create rating request - movie_id={movie_id}, rating={rating_data.score}")
    
    try:
        if not (1 <= rating_data.score <= 10):
            logger.warning(f"Invalid rating value: {rating_data.score} for movie_id={movie_id}")
            api_logger.warning(f"Create rating failed - invalid rating value")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 10"
            )
        
        rating = RatingService.create_rating(db, movie_id, rating_data)
        
        # Log 
        logger.info(f"Rating created successfully: movie_id={movie_id}, rating={rating_data.score}, rating_id={rating['id']}")
        api_logger.info(f"Rating created - ID: {rating['id']}")
        
        return {"status": "success", "data": rating}
        
    except HTTPException as e:
        # Log
        if e.status_code == 404:
            logger.warning(f"Movie not found for rating: movie_id={movie_id}")
            api_logger.warning(f"Create rating failed - movie not found")
        elif e.status_code == 400:
            logger.warning(f"Validation error for rating: movie_id={movie_id}, error={e.detail}")
            api_logger.warning(f"Create rating failed - validation error")
        else:
            logger.warning(f"HTTP Error creating rating: status={e.status_code}, detail={e.detail}")
            api_logger.warning(f"Create rating failed - HTTP {e.status_code}")
        raise e
        
    except Exception as e:
        # Log 
        logger.error(f"Server error creating rating for movie_id={movie_id}: {str(e)}", exc_info=True)
        api_logger.error(f"Create rating server error: {str(e)}")
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
    # Log 
    logger.info(f"API Request: GET /api/v1/movies/{movie_id}/ratings")
    api_logger.info(f"Get ratings request - movie_id={movie_id}")
    
    try:
        ratings = RatingService.get_movie_ratings(db, movie_id)
        
        # Log 
        logger.info(f"Ratings retrieved successfully: movie_id={movie_id}, count={len(ratings)}")
        api_logger.info(f"Ratings retrieved - count: {len(ratings)}")
        
        return {"status": "success", "data": ratings}
        
    except HTTPException as e:
        # Log 
        if e.status_code == 404:
            logger.warning(f"Movie not found when getting ratings: movie_id={movie_id}")
            api_logger.warning(f"Get ratings failed - movie not found")
        else:
            logger.warning(f"HTTP Error getting ratings: status={e.status_code}, detail={e.detail}")
            api_logger.warning(f"Get ratings failed - HTTP {e.status_code}")
        raise e
        
    except Exception as e:
        # Log 
        
        logger.error(f"Server error getting ratings for movie_id={movie_id}: {str(e)}", exc_info=True)
        api_logger.error(f"Get ratings server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching ratings: {str(e)}"
        )


# Health check endpoint

@router.get("/health")
def ratings_health_check():
    logger.debug("Ratings health check endpoint accessed")
    return {
        "status": "healthy",
        "service": "ratings",
        "timestamp": datetime.utcnow().isoformat()
    }
