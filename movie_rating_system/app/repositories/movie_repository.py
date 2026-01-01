from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import Optional, List, Tuple

from app.models.movie import Movie
from app.models.genre import Genre
from app.models.rating import Rating


class MovieRepository:

    @staticmethod
    def get_movies_with_pagination(
        db: Session,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genre_name: Optional[str] = None
    ) -> Tuple[List[Movie], int]:

        query = db.query(Movie).options(
            joinedload(Movie.director),
            joinedload(Movie.genres)
        )

        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))

        if release_year:
            query = query.filter(Movie.release_year == release_year)

        if genre_name:
            query = query.join(Movie.genres).filter(Genre.name == genre_name)

        total_items = query.count()
        offset = (page - 1) * page_size
        movies = query.offset(offset).limit(page_size).all()

        return movies, total_items

    @staticmethod
    def get_movie_by_id(db: Session, movie_id: int) -> Optional[Movie]:
        return (
            db.query(Movie)
            .options(
                joinedload(Movie.director),
                joinedload(Movie.genres),
                joinedload(Movie.ratings)
            )
            .filter(Movie.id == movie_id)
            .first()
        )

    @staticmethod
    def movie_exists(db: Session, movie_id: int) -> bool:
        return db.query(Movie).filter(Movie.id == movie_id).first() is not None

    @staticmethod
    def get_movies_by_director(db: Session, director_id: int) -> List[Movie]:
        return db.query(Movie).filter(Movie.director_id == director_id).all()


    def __init__(self, db: Session):
        self.db = db

    def get_movies(
        self,
        page: int,
        page_size: int,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genres: Optional[List[str]] = None,
    ) -> Tuple[List[Movie], int]:

        query = self.db.query(Movie)

        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))

        if release_year:
            query = query.filter(Movie.release_year == release_year)

        if genres:
            query = (
                query.join(Movie.genres)
                .filter(Genre.name.in_(genres))
                .group_by(Movie.id)
                .having(func.count(Genre.id) == len(genres))
            )

        total_items = query.count()

        movies = (
            query
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return movies, total_items

    def get_movies_with_ratings(
        self,
        page: int,
        page_size: int,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genres: Optional[List[str]] = None,
    ) -> Tuple[List[dict], int]:

        query = (
            self.db.query(
                Movie,
                func.coalesce(func.avg(Rating.score), 0).label("average_rating"),
                func.count(Rating.id).label("ratings_count"),
            )
            .outerjoin(Rating)
            .options(joinedload(Movie.director), joinedload(Movie.genres))
            .group_by(Movie.id)
        )

        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))

        if release_year:
            query = query.filter(Movie.release_year == release_year)

        if genres:
            query = (
                query.join(Movie.genres)
                .filter(Genre.name.in_(genres))
                .group_by(Movie.id)
                .having(func.count(Genre.id) == len(genres))
            )

        total_items = query.count()

        movies = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for row in movies:
            movie = row[0]
            avg = row[1]
            count = row[2]
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

        return items, total_items
