from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from typing import Optional, List
import logging
from datetime import datetime

from app.db.database import get_db

from app.schemas.movie_schema import (
    MovieCreate, MovieUpdate, ResponseModel
)
from app.schemas.rating_schema import ResponseRatingModel

from app.repositories.director_repository import DirectorRepository
from app.repositories.genre_repository import GenreRepository
from app.repositories.movie_repository import MovieRepository

from app.services.movie_service import MovieService

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])

logger = logging.getLogger(__name__)
api_logger = logging.getLogger("api")


# Dependency Injection

def get_movie_service(db: Session = Depends(get_db)):
    movie_repo = MovieRepository(db)
    director_repo = DirectorRepository()
    genre_repo = GenreRepository()
    return MovieService(movie_repo, director_repo, genre_repo)


# Search movies (with filters)

@router.get("/search", response_model=ResponseModel)
def search_movies(
    title: Optional[str] = Query(None),
    release_year: Optional[int] = Query(None, ge=1800, le=2100),
    genres: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    service: MovieService = Depends(get_movie_service),
):
    # Log 
    logger.info(f"API Request: GET /api/v1/movies/search - title={title}, year={release_year}, genres={genres}, page={page}, page_size={page_size}")
    api_logger.info(f"Search movies request - filters: title={title}, year={release_year}")
    
    try:
        data = service.list_movies(
            title=title,
            release_year=release_year,
            genres=genres,
            page=page,
            page_size=page_size,
        )
        
        total_items = data.get("total_items", 0)
        
        # Log 
        logger.info(f"Search successful - found {total_items} movies")
        api_logger.info(f"Search completed - results: {total_items} movies")
        
        return {"status": "success", "data": data}
        
    except HTTPException as e:
        # Log 
        logger.warning(f"HTTP Error in search: status={e.status_code}, detail={e.detail}")
        api_logger.warning(f"Search failed - HTTP {e.status_code}: {e.detail}")
        raise e
        
    except Exception as e:
        # Log 
        logger.error(f"Server error in search: {str(e)}", exc_info=True)
        api_logger.error(f"Search server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching movies: {str(e)}"
        )


# List movies (pagination only)

@router.get("/", response_model=ResponseModel)
def list_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    service: MovieService = Depends(get_movie_service),
):
    # Log 
    logger.info(f"API Request: GET /api/v1/movies - page={page}, page_size={page_size}")
    api_logger.info(f"List movies request - page={page}, page_size={page_size}")
    
    try:
        data = service.list_movies(page=page, page_size=page_size)
        total_items = data["total_items"]
        total_pages = (total_items + page_size - 1) // page_size

        # Log 
        logger.info(f"List movies successful - total_items={total_items}, total_pages={total_pages}, current_page={page}")
        api_logger.info(f"Movies list retrieved - showing page {page} of {total_pages}")
        
        return {
            "status": "success",
            "data": data,
            "pagination": {
                "current_page": page,
                "next_page": page + 1 if page < total_pages else None,
                "prev_page": page - 1 if page > 1 else None,
                "total_pages": total_pages
            }
        }
        
    except HTTPException as e:
        # Log 
        logger.warning(f"HTTP Error in list movies: status={e.status_code}, detail={e.detail}")
        api_logger.warning(f"List movies failed - HTTP {e.status_code}")
        raise e
        
    except Exception as e:
        # Log 
        logger.error(f"Server error listing movies: {str(e)}", exc_info=True)
        api_logger.error(f"List movies server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing movies: {str(e)}"
        )


# List movies with ratings

@router.get("/ratings", response_model=ResponseRatingModel)
def list_movies_ratings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    title: Optional[str] = Query(None),
    release_year: Optional[int] = Query(None),
    genres: Optional[List[str]] = Query(None),
    service: MovieService = Depends(get_movie_service),
):
    # Log 
    logger.info(f"API Request: GET /api/v1/movies/ratings - title={title}, year={release_year}, genres={genres}, page={page}, page_size={page_size}")
    api_logger.info(f"Movies with ratings request")
    
    try:
        items, total_items = service.list_movies_ratings(
            page=page,
            page_size=page_size,
            title=title,
            release_year=release_year,
            genres=genres,
        )

        total_pages = (total_items + page_size - 1) // page_size

        # Log 
        logger.info(f"Movies with ratings retrieved - items={len(items)}, total={total_items}")
        api_logger.info(f"Movies with ratings retrieved successfully")
        
        return {
            "status": "success",
            "data": {
                "items": items,
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "next_page": page + 1 if page < total_pages else None,
                "prev_page": page - 1 if page > 1 else None,
            }
        }
        
    except HTTPException as e:
        # Log 
        logger.warning(f"HTTP Error in movies with ratings: status={e.status_code}, detail={e.detail}")
        api_logger.warning(f"Movies with ratings failed - HTTP {e.status_code}")
        raise e
        
    except Exception as e:
        # Log 
        logger.error(f"Server error in movies with ratings: {str(e)}", exc_info=True)
        api_logger.error(f"Movies with ratings server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing movies with ratings: {str(e)}"
        )


# Get movie by ID

@router.get("/detail/{movie_id}", response_model=ResponseModel)
def get_movie(movie_id: int, service: MovieService = Depends(get_movie_service)):
    # Log 
    logger.info(f"API Request: GET /api/v1/movies/detail/{movie_id}")
    api_logger.info(f"Get movie details request - movie_id={movie_id}")
    
    try:
        movie = service.get_movie_by_id(movie_id)
        
        if not movie:
            # Log 
            logger.warning(f"Movie not found: movie_id={movie_id}")
            api_logger.warning(f"Movie not found - movie_id={movie_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Movie not found"
            )
        
        # Log 
        movie_title = movie.get('title', 'Unknown')
        logger.info(f"Movie retrieved successfully: movie_id={movie_id}, title='{movie_title}'")
        api_logger.info(f"Movie details retrieved - {movie_title}")
        
        return {"status": "success", "data": movie}
        
    except HTTPException as e:
        if e.status_code == 404:
            logger.warning(f"Movie not found (HTTP 404): movie_id={movie_id}")
            api_logger.warning(f"Movie not found - 404")
        else:
            logger.warning(f"HTTP Error in get movie: status={e.status_code}, detail={e.detail}")
            api_logger.warning(f"Get movie failed - HTTP {e.status_code}")
        raise e
        
    except Exception as e:
        # Log 
        logger.error(f"Server error getting movie {movie_id}: {str(e)}", exc_info=True)
        api_logger.error(f"Get movie server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching movie: {str(e)}"
        )


# Create movie

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_movie(
    movie_data: MovieCreate,
    db: Session = Depends(get_db),
):
    # Log 
    logger.info(f"API Request: POST /api/v1/movies - title='{movie_data.title}', year={movie_data.release_year}")
    api_logger.info(f"Create movie request - title='{movie_data.title}'")
    
    try:
        service = get_movie_service(db)
        created_movie = service.create_movie(db, movie_data)
        
        # Log 
        movie_id = created_movie.get('id')
        logger.info(f"Movie created successfully: movie_id={movie_id}, title='{movie_data.title}'")
        api_logger.info(f"Movie created - ID: {movie_id}")
        
        return {"status": "success", "data": created_movie}
        
    except HTTPException as e:
        # Log 
        if e.status_code == 404:
            logger.warning(f"Director/Genre not found when creating movie: {e.detail}")
            api_logger.warning(f"Create movie failed - resource not found")
        elif e.status_code == 400:
            logger.warning(f"Validation error creating movie: {e.detail}")
            api_logger.warning(f"Create movie failed - validation error")
        else:
            logger.warning(f"HTTP Error creating movie: status={e.status_code}, detail={e.detail}")
            api_logger.warning(f"Create movie failed - HTTP {e.status_code}")
        raise e
        
    except Exception as e:
        # Log 
        logger.error(f"Server error creating movie: {str(e)}", exc_info=True)
        api_logger.error(f"Create movie server error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating movie: {str(e)}"
        )


# Update movie

@router.put("/{movie_id}", response_model=dict)
def update_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    service: MovieService = Depends(get_movie_service)
):
    # Log 
    update_fields = {k: v for k, v in movie_data.dict(exclude_unset=True).items() if v is not None}
    logger.info(f"API Request: PUT /api/v1/movies/{movie_id} - update_fields={update_fields}")
    api_logger.info(f"Update movie request - movie_id={movie_id}")
    
    try:
        existing_movie = service.get_movie_by_id(movie_id)
        if not existing_movie:
            # Log
            logger.warning(f"Movie not found for update: movie_id={movie_id}")
            api_logger.warning(f"Update movie failed - movie not found")
            return JSONResponse(
                status_code=404,
                content={
                    "status": "failure",
                    "error": {
                        "code": 404,
                        "message": "Movie not found"
                    }
                }
            )
        
        updated_movie = service.update_movie(movie_id, movie_data)
        
        # Log 
        logger.info(f"Movie updated successfully: movie_id={movie_id}, fields_updated={list(update_fields.keys())}")
        api_logger.info(f"Movie updated - ID: {movie_id}")
        
        return {"status": "success", "data": updated_movie}
        
    except HTTPException as e:
        # Log 
        if e.status_code == 404:
            logger.warning(f"Genre not found when updating movie: {e.detail}")
            api_logger.warning(f"Update movie failed - genre not found")
        elif e.status_code == 400:
            logger.warning(f"Validation error updating movie: {e.detail}")
            api_logger.warning(f"Update movie failed - validation error")
        raise e
        
    except ValueError as e:
        # Log 
        logger.warning(f"Validation error updating movie {movie_id}: {str(e)}")
        api_logger.warning(f"Update movie validation error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "failure",
                "error": {
                    "code": 400,
                    "message": str(e)
                }
            }
        )
        
    except Exception as e:
        # Log خطای سرور
        logger.error(f"Server error updating movie {movie_id}: {str(e)}", exc_info=True)
        api_logger.error(f"Update movie server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating movie: {str(e)}"
        )


# Delete movie

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    service: MovieService = Depends(get_movie_service)
):
    # Log 
    logger.info(f"API Request: DELETE /api/v1/movies/{movie_id}")
    api_logger.info(f"Delete movie request - movie_id={movie_id}")
    
    try:
        existing_movie = service.get_movie_by_id(movie_id)
        if not existing_movie:
            # Log 
            logger.warning(f"Movie not found for deletion: movie_id={movie_id}")
            api_logger.warning(f"Delete movie failed - movie not found")
            return JSONResponse(
                status_code=404,
                content={
                    "status": "failure",
                    "error": {
                        "code": 404,
                        "message": "Movie not found"
                    }
                }
            )
        
        deleted = service.delete_movie(movie_id)
        
        if deleted:
            # Log 
            movie_title = existing_movie.get('title', 'Unknown')
            logger.info(f"Movie deleted successfully: movie_id={movie_id}, title='{movie_title}'")
            api_logger.info(f"Movie deleted - ID: {movie_id}")
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        else:
            # Log 
            logger.error(f"Failed to delete movie: movie_id={movie_id}")
            api_logger.error(f"Delete movie failed - internal error")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "failure",
                    "error": {
                        "code": 500,
                        "message": "Failed to delete movie"
                    }
                }
            )
        
    except Exception as e:
        # Log 
        logger.error(f"Server error deleting movie {movie_id}: {str(e)}", exc_info=True)
        api_logger.error(f"Delete movie server error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting movie: {str(e)}"
        )


# Health check endpoint

@router.get("/health")
def movies_health_check():
    logger.debug("Movies health check endpoint accessed")
    return {
        "status": "healthy",
        "service": "movies",
        "timestamp": datetime.utcnow().isoformat()
    }
