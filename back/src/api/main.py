"""
Aplicação principal da API de Predição da Qualidade do Ar.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from src.config import settings
from src.api.routes import predictions, health, metrics, stations, llm
from src.api.middleware.cors import setup_cors
from src.utils.logging import setup_logging
from src.models.base import ModelManager


# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Gerenciador de modelos global
model_manager = ModelManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    """
    # Startup
    logger.info("Iniciando aplicação...")
    
    try:
        # Carregar modelos
        await model_manager.load_models()
        logger.info("Modelos carregados com sucesso")
        
        # Adicionar o gerenciador ao estado da aplicação
        app.state.model_manager = model_manager
        
    except Exception as e:
        logger.error(f"Erro durante inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Finalizando aplicação...")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para predição da qualidade do ar em cidades brasileiras",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
setup_cors(app)

# Incluir rotas
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(stations.router, prefix="/stations", tags=["Stations"])
app.include_router(llm.router, prefix="/api/v1/llm", tags=["LLM Analysis"])


@app.get("/")
async def root():
    """
    Endpoint raiz da API.
    """
    return {
        "message": "API de Predição da Qualidade do Ar",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handler para exceções HTTP.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handler para exceções gerais.
    """
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erro interno do servidor",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
