from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Rating(Base):
    __tablename__ = "movie_ratings"
    __table_args__ = (
        CheckConstraint('score >= 1 AND score <= 10', name='score_range_check'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    movie = relationship("Movie", back_populates="ratings")