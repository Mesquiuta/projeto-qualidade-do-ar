"""
Schemas da API.
"""

from .requests import (
    ClimateDataRequest,
    PredictionRequest,
    BatchPredictionRequest,
    HistoricalDataRequest
)

from .responses import (
    QualityLevel,
    PollutantPrediction,
    PredictionResponse,
    BatchPredictionResponse,
    HistoricalDataPoint,
    HistoricalDataResponse,
    HealthResponse,
    ErrorResponse
)

__all__ = [
    # Requests
    "ClimateDataRequest",
    "PredictionRequest", 
    "BatchPredictionRequest",
    "HistoricalDataRequest",
    
    # Responses
    "QualityLevel",
    "PollutantPrediction",
    "PredictionResponse",
    "BatchPredictionResponse",
    "HistoricalDataPoint",
    "HistoricalDataResponse",
    "HealthResponse",
    "ErrorResponse"
]
