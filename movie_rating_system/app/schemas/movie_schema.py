from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DirectorBase(BaseModel):
    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


class GenreBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class MovieBase(BaseModel):
    id: int
    title: str
    release_year: int
    director: DirectorBase
    genres: List[str]
    cast: Optional[str] = "Unknown"
    average_rating: Optional[float] = None
    ratings_count: Optional[int] = 0

    class Config:
        orm_mode = True


class PaginatedMovieResponse(BaseModel):   
    page: int
    page_size: int
    total_items: int
    items: List[MovieBase]


class ResponseModel(BaseModel):
    status: str
    data: Optional[PaginatedMovieResponse | MovieBase] = None
    error: Optional[dict] = None


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    director_id: int
    release_year: int = Field(..., ge=1888, le=datetime.now().year)
    cast: Optional[str] = None
    genres: List[str] = Field(default_factory=list)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    release_year: Optional[int] = Field(None, ge=1888, le=datetime.now().year)
    cast: Optional[str] = None
    genres: Optional[List[str]] = None



class DirectorSimple(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MovieSimpleResponse(BaseModel):   
    id: int
    title: str
    release_year: int
    director: DirectorSimple
    genres: List[str]
    average_rating: Optional[float]

    class Config:
        from_attributes = True


class PaginatedMovies(BaseModel):
    page: int
    page_size: int
    total_items: int
    items: List[MovieSimpleResponse]

    class Config:
        from_attributes = True
