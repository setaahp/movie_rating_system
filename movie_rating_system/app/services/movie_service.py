from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from app.repositories.movie_repository import MovieRepository
from app.repositories.director_repository import DirectorRepository
from app.repositories.genre_repository import GenreRepository
from app.models.rating import Rating


class MovieService:
    def __init__(
        self,
        movie_repo: MovieRepository,
        director_repo: DirectorRepository,
        genre_repo: GenreRepository
    ):
        self.movie_repo = movie_repo
        self.director_repo = director_repo
        self.genre_repo = genre_repo
    # ------------------------
    # LIST MOVIES (pagination)
    # ------------------------
    def list_movies(
        self,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genres: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        movies, total_items = self.movie_repo.get_movies(
            page=page, page_size=page_size, title=title, release_year=release_year, genres=genres
        )

        items = []
        for movie in movies:
            avg, count = (
                self.movie_repo.db.query(
                    func.coalesce(func.avg(Rating.score), 0),
                    func.count(Rating.id),
                )
                .filter(Rating.movie_id == movie.id)
                .one()
            )

            items.append({
                "id": movie.id,
                "title": movie.title,
                "release_year": movie.release_year,
                "director": {
                    "id": movie.director.id,
                    "name": movie.director.name,
                } if movie.director else None,
                "genres": [g.name for g in movie.genres],
                "cast": getattr(movie, "cast", "Unknown"),
                "average_rating": round(avg, 2) if count > 0 else None,
                "ratings_count": count,
            })

        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "items": items,
        }

    # ------------------------
    # LIST MOVIES WITH RATINGS
    # ------------------------
    def list_movies_ratings(
        self,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genres: Optional[List[str]] = None,
    ) -> tuple[list[dict], int]:
        return self.movie_repo.get_movies_with_ratings(
            page=page,
            page_size=page_size,
            title=title,
            release_year=release_year,
            genres=genres,
        )

    # ------------------------
    # GET MOVIE BY ID
    # ------------------------
    def get_movie_by_id(self, movie_id: int) -> Dict[str, Any]:
        movie = self.movie_repo.get_movie_by_id(self.movie_repo.db, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")

        avg, count = (
            self.movie_repo.db.query(
                func.coalesce(func.avg(Rating.score), 0),
                func.count(Rating.id),
            )
            .filter(Rating.movie_id == movie_id)
            .one()
        )

        return {
            "id": movie.id,
            "title": movie.title,
            "release_year": movie.release_year,
            "director": {
                "id": movie.director.id,
                "name": movie.director.name,
            } if movie.director else None,
            "genres": [g.name for g in movie.genres],
            "cast": getattr(movie, "cast", "Unknown"),
            "average_rating": round(avg, 2) if count > 0 else None,
            "ratings_count": count,
        }

    