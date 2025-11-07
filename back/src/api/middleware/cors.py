"""
Middleware de CORS para a API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings


def setup_cors(app: FastAPI) -> None:
    """
    Configura CORS para a aplicação FastAPI.
    
    Args:
        app: Instância da aplicação FastAPI
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
        expose_headers=["X-Total-Count", "X-Request-ID"],
        max_age=3600  # Cache preflight por 1 hora
    )
