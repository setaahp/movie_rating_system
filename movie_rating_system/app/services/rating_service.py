from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.rating_repository import RatingRepository
from app.repositories.movie_repository import MovieRepository
from typing import Dict, Any, List


class RatingService:
    
    @staticmethod
    def create_rating(db: Session, movie_id: int, rating_data: RatingCreate) -> Dict[str, Any]:
        if not MovieRepository.movie_exists(db, movie_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        rating = RatingRepository.create_rating(db, movie_id, rating_data.score)
        
        return {
            "id": rating.id,
            "movie_id": rating.movie_id,
            "score": rating.score,
            "created_at": rating.created_at
        }
    
    @staticmethod
    def get_movie_ratings(db: Session, movie_id: int) -> List[Dict[str, Any]]:
        if not MovieRepository.movie_exists(db, movie_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        ratings = RatingRepository.get_ratings_by_movie(db, movie_id)
        
        return [
            {
                "id": rating.id,
                "movie_id": rating.movie_id,
                "score": rating.score,
                "created_at": rating.created_at
            }
            for rating in ratings
        ]
    
    @staticmethod
    def get_movie_average_rating(db: Session, movie_id: int) -> Dict[str, Any]:
        if not MovieRepository.movie_exists(db, movie_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        avg_rating = RatingRepository.get_average_rating(db, movie_id)
        ratings_count = RatingRepository.get_ratings_count(db, movie_id)
        
        return {
            "movie_id": movie_id,
            "average_rating": avg_rating,
            "ratings_count": ratings_count
        }
