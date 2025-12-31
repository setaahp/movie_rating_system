from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    director_id = Column(Integer, ForeignKey("directors.id"), nullable=False)
    release_year = Column(Integer, nullable=False)
    cast = Column(Text, nullable=True)
    
    director = relationship("Director", back_populates="movies")
    genres = relationship("Genre", secondary="movie_genres", back_populates="movies")
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")
    
    @property
    def average_rating(self):
        if not self.ratings:
            return None
        total = sum(rating.score for rating in self.ratings)
        return round(total / len(self.ratings), 1)
    
    @property
    def ratings_count(self):
        return len(self.ratings)