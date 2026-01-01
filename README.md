
# Movie Rating System 

A RESTful back-end system for managing movies and user ratings, developed as part of the **Software Engineering** course at AUT.  
This project is fully containerized and runs using **Docker Compose**.

---

##  Project Overview

This project is a **Movie Rating System Back-End** built with **Python** and **FastAPI**.  
It provides APIs for managing movies, directors, genres, and movie ratings, following **RESTful principles** and a **layered architecture**.

The system supports:
- Movie listing with pagination
- Filtering and searching movies
- Viewing detailed movie information
- Creating, updating, and deleting movies
- Submitting ratings (1–10) for movies
- Automatic calculation of average rating and rating count

---

##  Technologies Used

- **Python 3**
- **FastAPI**
- **SQLAlchemy (ORM)**
- **PostgreSQL**
- **Alembic** (Migrations)
- **Pydantic**
- **Docker & Docker Compose**
- **Git & GitHub**

---



##  Database Design

### Main Tables

| Table | Description |
|------|-------------|
| `movies` | Movies information |
| `directors` | Directors data |
| `genres` | Movie genres |
| `movie_genres` | Many-to-many relation |
| `movie_ratings` | Movie ratings (1–10) |

### Relationships

- One movie → One director  
- One movie → Many genres  
- One movie → Many ratings  

---

##  API Endpoints 

### Movies

| Method | Endpoint | Description |
|------|---------|-------------|
| GET | `/api/v1/movies/search` | Search movies |
| GET | `/api/v1/movies/list` | List movies (pagination) |
| GET | `/api/v1/movies/detail/{movie_id}` | Get movie |
| GET | `/api/v1/movies/ratings` | List movies ratings |
| POST | `/api/v1/movies/` | Create movie |
| PUT | `/api/v1/movies/{movie_id}` | Update movie |
| DELETE | `/api/v1/movies/{movie_id}` | Delete movie |

---

##  Dataset (Required)

Due to GitHub file size limitations and environment restrictions,
large CSV dataset files are **not included** in this repository.

Before running the project, please download the following datasets
and place them inside the `scripts/` directory:

- `tmdb_5000_movies.csv`
- `tmdb_5000_credits.csv`

You can download the datasets from the following source:

🔗 https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

After downloading, your `scripts/` directory should look like this:

---

##  Running the Project with Docker Compose

### 1. Prerequisites
Make sure you have installed:
- **Docker**
- **Docker Compose**

No additional tools (such as Git LFS) are required.

---

### 2. Environment Variables
Create a `.env` file based on the example file:

```bash
cp .env.example .env
```

---

### 3. Build and Start Containers

From the root directory of the project, run the following command:
```
docker compose up --build
```

This command will build the required Docker images and start the following services:


   PostgreSQL database container
   FastAPI application container

---

### License
This project is developed for educational purposes.

---
### Team participants
- Hamid

- Setayesh
