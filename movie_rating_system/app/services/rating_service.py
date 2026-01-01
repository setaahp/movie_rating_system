from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.rating_repository import RatingRepository
from app.repositories.movie_repository import MovieRepository
from app.schemas.rating_schema import RatingCreate
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)
api_logger = logging.getLogger("api")

class RatingService:
    
    @staticmethod
    def create_rating(db: Session, movie_id: int, rating_data: RatingCreate) -> Dict[str, Any]:
        logger.info(f"Creating rating - movie_id={movie_id}, score={rating_data.score}")
        

        if not MovieRepository.movie_exists(db, movie_id):
            logger.warning(f"Movie not found when creating rating: movie_id={movie_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        

        if not (1 <= rating_data.score <= 10):
            logger.warning(f"Invalid rating score: {rating_data.score} for movie_id={movie_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 10"
            )
        
        try:
            rating = RatingRepository.create_rating(db, movie_id, rating_data.score)
            logger.info(f"Rating created in database - rating_id={rating.id}")
            api_logger.info(f"Rating saved to DB - ID: {rating.id}")
            
            return {
                "id": rating.id,
                "movie_id": rating.movie_id,
                "score": rating.score,
                "created_at": rating.created_at
            }
            
        except Exception as e:
            logger.error(f"Database error creating rating for movie {movie_id}: {str(e)}", exc_info=True)
            api_logger.error(f"Database error creating rating: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error creating rating: {str(e)}"
            )
    
    @staticmethod
    def get_movie_ratings(db: Session, movie_id: int) -> List[Dict[str, Any]]:
        logger.info(f"Getting ratings from database for movie: movie_id={movie_id}")
        
        if not MovieRepository.movie_exists(db, movie_id):
            logger.warning(f"Movie not found when getting ratings: movie_id={movie_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        try:
            ratings = RatingRepository.get_ratings_by_movie(db, movie_id)
            logger.info(f"Retrieved {len(ratings)} ratings from database for movie: movie_id={movie_id}")
            api_logger.info(f"Ratings fetched from DB - count: {len(ratings)}")
            
            return [
                {
                    "id": rating.id,
                    "movie_id": rating.movie_id,
                    "score": rating.score,
                    "created_at": rating.created_at
                }
                for rating in ratings
            ]
            
        except Exception as e:
            logger.error(f"Database error getting ratings for movie {movie_id}: {str(e)}", exc_info=True)
            api_logger.error(f"Database error getting ratings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error fetching ratings: {str(e)}"
            )
    
    @staticmethod
    def get_movie_average_rating(db: Session, movie_id: int) -> Dict[str, Any]:
        logger.info(f"Calculating average rating for movie: movie_id={movie_id}")
        
        if not MovieRepository.movie_exists(db, movie_id):
            logger.warning(f"Movie not found when calculating average rating: movie_id={movie_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        try:
            avg_rating = RatingRepository.get_average_rating(db, movie_id)
            ratings_count = RatingRepository.get_ratings_count(db, movie_id)
            
            logger.info(f"Average rating calculated: movie_id={movie_id}, avg={avg_rating}, count={ratings_count}")
            api_logger.info(f"Average rating calculated - avg: {avg_rating}")
            
            return {
                "movie_id": movie_id,
                "average_rating": avg_rating,
                "ratings_count": ratings_count
            }
            
        except Exception as e:
            logger.error(f"Database error calculating average rating for movie {movie_id}: {str(e)}", exc_info=True)
            api_logger.error(f"Database error calculating average: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error calculating average rating: {str(e)}"
            )
