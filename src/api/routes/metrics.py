"""
Rotas para exposição de métricas do modelo.
Fase 2: Exposição de Métricas
"""

import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    """
    Retorna as métricas do modelo treinado.
    
    Lê o arquivo model.metadata.json e retorna seu conteúdo.
    
    Returns:
        JSONResponse: Métricas do modelo incluindo:
            - winner: Nome do modelo vencedor
            - metrics: Métricas de desempenho (MAE, RMSE, R²)
            - features: Lista de features utilizadas
            - trained_at: Timestamp do treinamento
            - training_samples: Número de amostras de treino
            - test_samples: Número de amostras de teste
    
    Raises:
        HTTPException: 404 se o arquivo de metadata não existir
    """
    try:
        # Construir caminho para o arquivo de metadata
        metadata_path = Path(settings.MODEL_PATH) / "model.metadata.json"
        
        # Verificar se o arquivo existe
        if not metadata_path.exists():
            logger.warning(f"Arquivo de metadata não encontrado: {metadata_path}")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Metadata não encontrado",
                    "message": "O arquivo model.metadata.json não existe. Execute o treinamento primeiro.",
                    "path": str(metadata_path)
                }
            )
        
        # Ler o arquivo JSON
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        logger.info("Métricas retornadas com sucesso")
        
        # Retornar o conteúdo do metadata
        return JSONResponse(
            status_code=200,
            content=metadata
        )
        
    except HTTPException:
        # Re-lançar HTTPException
        raise
        
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erro ao ler metadata",
                "message": "O arquivo model.metadata.json está corrompido ou mal formatado."
            }
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erro interno",
                "message": str(e)
            }
        )

