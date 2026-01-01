from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.genre import Genre

class GenreRepository:
    
    @staticmethod
    def get_genres_by_ids(db: Session, genre_ids: List[int]) -> List[Genre]:
        if not genre_ids:
            return []
        return db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
    
    @staticmethod
    def get_genre_by_id(db: Session, genre_id: int) -> Optional[Genre]:
        return db.query(Genre).filter(Genre.id == genre_id).first()
    
    @staticmethod
    def get_all_genres(db: Session) -> List[Genre]:
        return db.query(Genre).all()
    
    @staticmethod
    def create_genre(db: Session, name: str) -> Genre:
        genre = Genre(name=name)
        db.add(genre)
        db.commit()
        db.refresh(genre)
        return genre
    
    @staticmethod
    def get_genres_by_names(db: Session, genre_names: List[str]) -> List[Genre]:
        if not genre_names:
            return []
        return db.query(Genre).filter(Genre.name.in_(genre_names)).all()
