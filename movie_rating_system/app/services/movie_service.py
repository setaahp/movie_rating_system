from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
import logging

from app.repositories.movie_repository import MovieRepository
from app.repositories.director_repository import DirectorRepository
from app.repositories.genre_repository import GenreRepository
from app.models.rating import Rating
from app.schemas.movie_schema import MovieCreate, MovieUpdate

logger = logging.getLogger(__name__)
api_logger = logging.getLogger("api")

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
        
    # LIST MOVIES (pagination)
    
    def list_movies(
        self,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genres: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        
        logger.info(f"Service: Listing movies - page={page}, page_size={page_size}, filters: title={title}, year={release_year}")
        
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

        logger.info(f"Service: Retrieved {len(items)} movies from database")
        
        return {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "items": items,
        }

    # LIST MOVIES WITH RATINGS

    def list_movies_ratings(
        self,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genres: Optional[List[str]] = None,
    ) -> tuple[list[dict], int]:
        
        logger.info(f"Service: Listing movies with ratings - page={page}, page_size={page_size}")
        
        return self.movie_repo.get_movies_with_ratings(
            page=page,
            page_size=page_size,
            title=title,
            release_year=release_year,
            genres=genres,
        )

    # GET MOVIE BY ID

    def get_movie_by_id(self, movie_id: int) -> Dict[str, Any]:
        
        logger.info(f"Service: Getting movie by ID - movie_id={movie_id}")
        
        movie = self.movie_repo.get_movie_by_id(self.movie_repo.db, movie_id)
        if not movie:
            logger.warning(f"Service: Movie not found in database - movie_id={movie_id}")
            raise HTTPException(status_code=404, detail="Movie not found")

        avg, count = (
            self.movie_repo.db.query(
                func.coalesce(func.avg(Rating.score), 0),
                func.count(Rating.id),
            )
            .filter(Rating.movie_id == movie_id)
            .one()
        )

        logger.info(f"Service: Movie found - movie_id={movie_id}, title={movie.title}")
        
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


    # CREATE MOVIE

    def create_movie(self, db: Session, data: MovieCreate) -> Dict[str, Any]:
        
        logger.info(f"Service: Creating movie - title='{data.title}', year={data.release_year}")
        
        # validate director
        director = self.director_repo.get_director_by_id(db, data.director_id)
        if not director:
            logger.warning(f"Service: Director not found - director_id={data.director_id}")
            raise HTTPException(status_code=404, detail="Director not found")

        # validate genres
        genre_objs = self.genre_repo.get_genres_by_names(db, data.genres)
        if len(genre_objs) != len(data.genres):
            logger.warning(f"Service: Invalid genre names - requested={data.genres}, found={[g.name for g in genre_objs]}")
            raise HTTPException(status_code=404, detail="Invalid genre names")

        movie_data = data.dict(exclude={"genres"})
        movie = self.movie_repo.create_movie(db, movie_data, genre_objs)
        
        logger.info(f"Service: Movie created in database - movie_id={movie.id}")

        return {
        "id": movie.id,
        "title": movie.title,
        "release_year": movie.release_year,
        "director": {"id": director.id, "name": director.name},
        "genres": [g.name for g in movie.genres],
        "cast": getattr(movie, "cast", "Unknown"),
        "average_rating": None,
        "ratings_count": 0
    }
    

    def update_movie(self, movie_id: int, data: MovieUpdate) -> Dict[str, Any]:
        
        logger.info(f"Service: Updating movie - movie_id={movie_id}")
        
        db = self.movie_repo.db
        genre_objs = None
        if data.genres is not None:
            genre_objs = self.genre_repo.get_genres_by_names(db, data.genres)
            if len(genre_objs) != len(data.genres):
                logger.warning(f"Service: Invalid genre names when updating - requested={data.genres}")
                raise HTTPException(status_code=404, detail="Some genre names are invalid")

        movie = self.movie_repo.update_movie(
            db,
            movie_id,
            data.dict(exclude_unset=True, exclude={"genres"}),
            genre_objs  
        )

        if not movie:
            logger.warning(f"Service: Movie not found for update - movie_id={movie_id}")
            raise HTTPException(status_code=404, detail="Movie not found")

        avg, count = (
            db.query(
                func.coalesce(func.avg(Rating.score), 0),
                func.count(Rating.id),
        )
            .filter(Rating.movie_id == movie.id)
            .one()
    )

        logger.info(f"Service: Movie updated successfully - movie_id={movie_id}")

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



    # DELETE MOVIE

    def delete_movie(self, movie_id: int) -> None:
        
        logger.info(f"Service: Deleting movie - movie_id={movie_id}")
        
        db = self.movie_repo.db
        if not self.movie_repo.delete_movie(db, movie_id):
            logger.warning(f"Service: Movie not found for deletion - movie_id={movie_id}")
            raise HTTPException(status_code=404, detail="Movie not found")
        
        logger.info(f"Service: Movie deleted from database - movie_id={movie_id}")
