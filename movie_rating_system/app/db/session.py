from app.db.database import SessionLocal

def get_db_session():
    return SessionLocal()