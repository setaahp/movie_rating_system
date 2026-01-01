from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class MovieRatingSchema(BaseModel):
    id: int
    title: str
    average_rating: Optional[float] = None
    ratings_count: int = 0

    class Config:
        orm_mode = True


class PaginatedMovieRatingSchema(BaseModel):
    page: int
    page_size: int
    total_items: int
    items: List[MovieRatingSchema]


class ResponseRatingModel(BaseModel):
    status: str
    data: Optional[PaginatedMovieRatingSchema] = None
    error: Optional[dict] = None


class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)

    @validator('score')
    def validate_score(cls, v):
        if not 1 <= v <= 10:
            raise ValueError("Score must be between 1 and 10")
        return v


class RatingResponse(BaseModel):
    id: int
    movie_id: int
    score: int
    created_at: datetime

    class Config:
        from_attributes = True
