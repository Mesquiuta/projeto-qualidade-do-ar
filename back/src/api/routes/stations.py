"""
Rotas de estações da API.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import List
import logging

from src.api.schemas.responses import StationResponse
from src.db.mock_db import mock_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stations", response_model=List[StationResponse])
async def get_stations(api_request: Request):
    """
    Retorna a lista de estações de monitoramento.
    """
    try:
        stations_data = await mock_db.get_stations()
        
        # Mapear para o schema de resposta
        stations_response = [StationResponse(**station) for station in stations_data]
        
        return stations_response
        
    except Exception as e:
        logger.error(f"Erro ao buscar estações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")
