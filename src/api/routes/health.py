"""
Rotas de health check da API.
"""

from fastapi import APIRouter, Request
from datetime import datetime
import time
import psutil
import logging

from src.api.schemas.responses import HealthResponse
from src.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Timestamp de inicialização da aplicação
start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Verifica o status de saúde da API.
    
    Retorna informações sobre:
    - Status geral da aplicação
    - Carregamento de modelos
    - Conexão com banco de dados
    - Tempo de atividade
    - Uso de recursos
    """
    try:
        # Verificar se o modelo está carregado
        model_loaded = False
        if hasattr(request.app.state, 'model_manager'):
            model_loaded = request.app.state.model_manager.is_loaded()
        
        # Verificar conexão com banco (simulado por enquanto)
        database_connected = True  # TODO: Implementar verificação real
        
        # Calcular uptime
        uptime = time.time() - start_time
        
        # Status geral
        status = "healthy" if model_loaded and database_connected else "degraded"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.utcnow(),
            versao=settings.APP_VERSION,
            modelo_carregado=model_loaded,
            banco_conectado=database_connected,
            uptime=uptime
        )
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            versao=settings.APP_VERSION,
            modelo_carregado=False,
            banco_conectado=False,
            uptime=time.time() - start_time
        )


@router.get("/health/detailed")
async def detailed_health_check(request: Request):
    """
    Verifica o status detalhado da API incluindo métricas de sistema.
    """
    try:
        # Informações básicas de saúde
        basic_health = await health_check(request)
        
        # Métricas de sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Informações de processo
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            **basic_health.dict(),
            "system_metrics": {
                "cpu_usage_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": round((disk.used / disk.total) * 100, 2)
                },
                "process": {
                    "memory_mb": round(process_memory.rss / (1024**2), 2),
                    "cpu_percent": process.cpu_percent()
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no health check detalhado: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow()
        }


@router.get("/health/ready")
async def readiness_check(request: Request):
    """
    Verifica se a aplicação está pronta para receber requisições.
    """
    try:
        # Verificar componentes críticos
        model_ready = False
        if hasattr(request.app.state, 'model_manager'):
            model_ready = request.app.state.model_manager.is_loaded()
        
        database_ready = True  # TODO: Implementar verificação real
        
        if model_ready and database_ready:
            return {
                "status": "ready",
                "timestamp": datetime.utcnow(),
                "components": {
                    "model": "ready",
                    "database": "ready"
                }
            }
        else:
            return {
                "status": "not_ready",
                "timestamp": datetime.utcnow(),
                "components": {
                    "model": "ready" if model_ready else "not_ready",
                    "database": "ready" if database_ready else "not_ready"
                }
            }
            
    except Exception as e:
        logger.error(f"Erro no readiness check: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow()
        }


@router.get("/health/live")
async def liveness_check():
    """
    Verifica se a aplicação está viva (liveness probe).
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow()
    }
