from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.rating import Rating
from app.models.movie import Movie


class RatingRepository:
    
    @staticmethod
    def create_rating(db: Session, movie_id: int, score: int) -> Rating:
        rating = Rating(movie_id=movie_id, score=score)
        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating
    
    @staticmethod
    def get_ratings_by_movie(db: Session, movie_id: int) -> List[Rating]:
        return db.query(Rating).filter(Rating.movie_id == movie_id).all()
    
    @staticmethod
    def get_rating_by_id(db: Session, rating_id: int) -> Optional[Rating]:
        return db.query(Rating).filter(Rating.id == rating_id).first()
    
    @staticmethod
    def get_average_rating(db: Session, movie_id: int) -> Optional[float]:
        from sqlalchemy import func
        result = db.query(func.avg(Rating.score)).filter(Rating.movie_id == movie_id).scalar()
        return round(result, 1) if result else None
    
    @staticmethod
    def get_ratings_count(db: Session, movie_id: int) -> int:
        return db.query(Rating).filter(Rating.movie_id == movie_id).count()