"""
Rotas de predições da API.
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from datetime import datetime, date
import time
import logging
from typing import List

from src.api.schemas.requests import (
    PredictionRequest,
    BatchPredictionRequest,
    HistoricalDataRequest
)
from src.api.schemas.responses import (
    PredictionResponse,
    BatchPredictionResponse,
    HistoricalDataResponse,
    QualityLevel,
    PollutantPrediction
)
from src.config import settings
from src.db.mock_db import mock_db # Importar o MockDB

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict", response_model=PredictionResponse)
async def predict_air_quality(
    request: PredictionRequest,
    api_request: Request
):
    """
    Realiza predição da qualidade do ar baseada em dados climáticos.
    
    - **cidade**: Nome da cidade (opcional, padrão: São Paulo)
    - **dados_climaticos**: Dados climáticos necessários para predição
    - **data_predicao**: Data para a predição (opcional, padrão: hoje)
    - **incluir_historico**: Se deve incluir dados históricos na resposta
    """
    try:
        # Verificar se o modelo está carregado (para manter a estrutura)
        if not hasattr(api_request.app.state, 'model_manager'):
            raise HTTPException(
                status_code=503,
                detail="Serviço indisponível: modelo não carregado"
            )
        
        # Simulação de predição (Mock)
        
        # Dados mock para a resposta
        mock_prediction = PredictionResponse(
            cidade=request.cidade or "São Paulo",
            data_predicao=request.data_predicao or date.today(),
            timestamp=datetime.utcnow(),
            pm25=PollutantPrediction(
                valor=25.5,
                unidade="µg/m³",
                nivel_qualidade=QualityLevel.MODERATE,
                confianca=0.8
            ),
            pm10=PollutantPrediction(
                valor=45.0,
                unidade="µg/m³",
                nivel_qualidade=QualityLevel.GOOD,
                confianca=0.8
            ),
            no2=PollutantPrediction(
                valor=35.0,
                unidade="µg/m³",
                nivel_qualidade=QualityLevel.GOOD,
                confianca=0.8
            ),
            o3=PollutantPrediction(
                valor=80.0,
                unidade="µg/m³",
                nivel_qualidade=QualityLevel.MODERATE,
                confianca=0.8
            ),
            so2=PollutantPrediction(
                valor=15.0,
                unidade="µg/m³",
                nivel_qualidade=QualityLevel.GOOD,
                confianca=0.8
            ),
            co=PollutantPrediction(
                valor=1.5,
                unidade="mg/m³",
                nivel_qualidade=QualityLevel.GOOD,
                confianca=0.8
            ),
            overall_quality=QualityLevel.MODERATE,
            historical_data=[]
        )
        
        if request.incluir_historico:
            # Usar o MockDB para dados históricos
            # Como a requisição não especifica a estação, vamos usar a primeira estação mock (id=1)
            historical_data = await mock_db.get_historical_data(station_id=1)
            mock_prediction.historical_data = historical_data
            
        return mock_prediction
        
    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch_air_quality(
    request: BatchPredictionRequest,
    api_request: Request
):
    """
    Realiza predições em lote da qualidade do ar.
    
    - **cidade**: Nome da cidade (opcional)
    - **dados_climaticos**: Lista de dados climáticos para predição
    - **datas_predicao**: Datas correspondentes (opcional)
    """
    # Simulação de predição em lote (Mock)
    mock_predictions = []
    for i in range(len(request.dados_climaticos)):
        mock_predictions.append(
            PredictionResponse(
                cidade=request.cidade or "São Paulo",
                data_predicao=request.datas_predicao[i] if request.datas_predicao and i < len(request.datas_predicao) else date.today(),
                timestamp=datetime.utcnow(),
                pm25=PollutantPrediction(
                    valor=20.0 + i,
                    unidade="µg/m³",
                    nivel_qualidade=QualityLevel.GOOD,
                    confianca=0.9
                ),
                overall_quality=QualityLevel.GOOD,
                historical_data=[]
            )
        )
    
    return BatchPredictionResponse(
        cidade=request.cidade or "São Paulo",
        total_predicoes=len(mock_predictions),
        predicoes=mock_predictions,
        tempo_processamento=0.1
    )


@router.get("/historical", response_model=HistoricalDataResponse)
async def get_historical_data(
    request: HistoricalDataRequest,
    api_request: Request
):
    """
    Retorna dados históricos de qualidade do ar.
    """
    try:
        # Usar o MockDB para dados históricos
        historical_data = await mock_db.get_historical_data(
            station_id=request.station_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        return HistoricalDataResponse(
            station_id=request.station_id,
            data=historical_data
        )
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados históricos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")


@router.get("/analyze-llm", response_model=str)
async def analyze_data_with_llm(
    station_id: int = 1,
    api_request: Request = None
):
    """
    Simula a análise de dados históricos por um LLM.
    """
    try:
        # Buscar dados históricos (últimas 24h)
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=24)
        
        historical_data = await mock_db.get_historical_data(
            station_id=station_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Simular a análise do LLM
        analysis_result = await mock_db.analyze_data_with_llm(historical_data)
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Erro ao analisar dados com LLM: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")
