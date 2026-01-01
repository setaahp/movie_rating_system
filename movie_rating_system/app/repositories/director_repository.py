from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.director import Director

class DirectorRepository:
    
    @staticmethod
    def get_director_by_id(db: Session, director_id: int) -> Optional[Director]:
        return db.query(Director).filter(Director.id == director_id).first()
    
    @staticmethod
    def director_exists(db: Session, director_id: int) -> bool:
        return db.query(Director).filter(Director.id == director_id).first() is not None
    
    @staticmethod
    def get_all_directors(db: Session) -> List[Director]:
        return db.query(Director).all()
    
    @staticmethod
    def create_director(db: Session, name: str) -> Director:
        director = Director(name=name)
        db.add(director)
        db.commit()
        db.refresh(director)
        return director
