import logging
from logging.config import dictConfig
from app.core.config import settings


def setup_logging() -> None:
    dictConfig({
        "version": 1,                        
        "disable_existing_loggers": False,    
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)-8s %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",   
                "formatter": "default",
                "stream": "ext://sys.stdout",       
            },
        },
        "loggers": {
            "app": {                                 
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,                  
            },
            "uvicorn.error": {                       
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {                      
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {                   
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    })