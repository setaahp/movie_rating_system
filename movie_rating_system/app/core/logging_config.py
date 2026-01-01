import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

log_dir = Path("app/logs")
log_dir.mkdir(exist_ok=True)

def setup_logging():
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    root_logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    file_handler = RotatingFileHandler(
        filename="app/logs/movie_rating.log",
        maxBytes=10*1024*1024,  
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    error_handler = RotatingFileHandler(
        filename="app/logs/error.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.WARNING) 
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    logging.getLogger("uvicorn").propagate = False
    logging.getLogger("uvicorn.access").propagate = True  
    
    api_logger = logging.getLogger("api")
    api_logger.setLevel(logging.INFO)
    api_logger.propagate = True
    
    root_logger.info("Logging setup completed")

setup_logging()
