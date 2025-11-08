# src/api/schemas/responses.py
from __future__ import annotations

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# Utilitários e abstrações comuns
# ============================================================

class Pagination(BaseModel):
    """Metadados de paginação padronizados."""
    page: int = Field(1, ge=1, description="Página atual (1-indexed).")
    per_page: int = Field(20, ge=1, le=200, description="Itens por página.")
    total: int = Field(0, ge=0, description="Total de registros.")
    total_pages: int = Field(0, ge=0, description="Total de páginas.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"page": 1, "per_page": 20, "total": 120, "total_pages": 6}
        }
    )


class ErrorResponse(BaseModel):
    """Envelope de erro padrão."""
    error: bool = Field(True, const=True)
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": True,
                "message": "Recurso não encontrado",
                "status_code": 404,
                "details": {"resource": "station", "id": 999},
                "timestamp": "2024-01-15T12:00:00Z",
            }
        }
    )


# ============================================================
# Estações
# ============================================================

class StationResponse(BaseModel):
    """Representação pública de uma estação de monitoramento."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador da estação")
    name: str = Field(..., description="Nome da estação")
    latitude: float = Field(..., description="Latitude em graus decimais")
    longitude: float = Field(..., description="Longitude em graus decimais")
    city: str = Field(..., description="Cidade")
    state: str = Field(..., description="Estado/UF")
    country: str = Field(..., description="País (ISO-2 ou nome)")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Estação Centro",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "city": "São Paulo",
                "state": "SP",
                "country": "BR",
            }
        },
    )


class StationDetailResponse(StationResponse):
    """Detalhes opcionais adicionais de uma estação."""
    installed_at: Optional[date] = Field(None, description="Data de instalação")
    active: bool = Field(default=True, description="Indicador de atividade")
    sensors: Optional[List[str]] = Field(
        None, description="Lista de sensores disponíveis (ex.: pm25, pm10, o3)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Estação Centro",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "city": "São Paulo",
                "state": "SP",
                "country": "BR",
                "installed_at": "2023-04-20",
                "active": True,
                "sensors": ["pm25", "pm10", "o3", "no2", "so2", "co"],
            }
        }
    )


class StationListResponse(BaseModel):
    """Lista paginada de estações."""
    items: List[StationResponse]
    pagination: Optional[Pagination] = None


# ============================================================
# Saúde / Métricas
# ============================================================

class HealthResponse(BaseModel):
    status: Literal["ok", "healthy", "degraded", "down"] = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    model_loaded: bool = True
    db_connected: bool = True
    uptime_seconds: float = 0.0

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "timestamp": "2024-01-15T12:30:00Z",
                "version": "1.0.0",
                "model_loaded": True,
                "db_connected": True,
                "uptime_seconds": 12345.67,
            }
        }
    )


class MetricsResponse(BaseModel):
    uptime_seconds: float
    total_requests: int
    avg_latency_ms: Optional[float] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "uptime_seconds": 45231.4,
                "total_requests": 10342,
                "avg_latency_ms": 18.7,
            }
        }
    )


# ============================================================
# Qualidade do Ar / Predições
# ============================================================

class QualityLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    VERY_POOR = "very_poor"
    HAZARDOUS = "hazardous"


class PredictionItem(BaseModel):
    """Item simples de predição por timestamp."""
    timestamp: datetime
    aqi: int
    pm25: float
    pm10: float
    o3: float
    no2: float
    so2: float
    co: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": "2024-01-15T13:00:00Z",
                "aqi": 78,
                "pm25": 22.5,
                "pm10": 45.3,
                "o3": 120.1,
                "no2": 37.4,
                "so2": 10.2,
                "co": 0.7,
            }
        }
    )


class PredictionResponse(BaseModel):
    """Predição agregada por estação."""
    station_id: int
    items: List[PredictionItem]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "station_id": 1,
                "items": [
                    {
                        "timestamp": "2024-01-15T13:00:00Z",
                        "aqi": 78,
                        "pm25": 22.5,
                        "pm10": 45.3,
                        "o3": 120.1,
                        "no2": 37.4,
                        "so2": 10.2,
                        "co": 0.7,
                    }
                ],
            }
        }
    )


class PollutantPrediction(BaseModel):
    """Predição por poluente com nível de qualidade e confiança."""
    value: float = Field(..., description="Valor predito")
    unit: str = Field(..., description="Unidade de medida (ex.: µg/m³)")
    quality: QualityLevel = Field(..., description="Nível de qualidade do ar")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Confiança 0–1")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "value": 25.5,
                "unit": "µg/m³",
                "quality": "moderate",
                "confidence": 0.86,
            }
        }
    )


class RichPredictionEnvelope(BaseModel):
    """Envelope mais rico para /predict quando quiser respostas ‘explicadas’."""
    city: str
    station_id: Optional[int] = None
    predicted_at: datetime = Field(default_factory=datetime.utcnow)
    date_ref: date = Field(default_factory=date.today)
    aqi: int
    overall_quality: QualityLevel
    pm25: PollutantPrediction
    pm10: Optional[PollutantPrediction] = None
    o3: Optional[PollutantPrediction] = None
    no2: Optional[PollutantPrediction] = None
    so2: Optional[PollutantPrediction] = None
    co: Optional[PollutantPrediction] = None
    model_version: str = "1.0.0"
    overall_confidence: float = Field(..., ge=0, le=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "São Paulo",
                "station_id": 1,
                "predicted_at": "2024-01-15T13:15:00Z",
                "date_ref": "2024-01-15",
                "aqi": 82,
                "overall_quality": "moderate",
                "pm25": {"value": 26.1, "unit": "µg/m³", "quality": "moderate", "confidence": 0.84},
                "pm10": {"value": 48.2, "unit": "µg/m³", "quality": "moderate", "confidence": 0.81},
                "model_version": "1.0.0",
                "overall_confidence": 0.83,
            }
        }
    )


class BatchPredictionResponse(BaseModel):
    city: str
    total: int
    predictions: List[RichPredictionEnvelope]
    processing_time_sec: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "São Paulo",
                "total": 2,
                "predictions": [],
                "processing_time_sec": 0.27,
            }
        }
    )


# ============================================================
# Histórico
# ============================================================

class HistoricalDataPoint(BaseModel):
    date: date
    pollutants: Dict[str, float]
    weather: Optional[Dict[str, float]] = None
    quality: Optional[QualityLevel] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2024-01-15",
                "pollutants": {"pm25": 23.5, "pm10": 41.2, "no2": 30.1},
                "weather": {"temperature": 26.4, "humidity": 63.0, "wind_speed": 12.5},
                "quality": "moderate",
            }
        }
    )


class HistoricalDataResponse(BaseModel):
    city: str
    station_id: Optional[int] = None
    period: Dict[str, date]  # {"start": date, "end": date}
    total_records: int
    data: List[HistoricalDataPoint]
    stats: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "city": "São Paulo",
                "station_id": 1,
                "period": {"start": "2024-01-01", "end": "2024-01-31"},
                "total_records": 31,
                "data": [],
                "stats": {"pm25_mean": 22.8, "pm25_max": 45.2, "pm25_min": 11.7},
            }
        }
    )


# ============================================================
# LLM (se houver rota /llm que devolva algo estruturado)
# ============================================================

class LLMAnswer(BaseModel):
    prompt: str
    answer: str
    model: str = "gpt"
    latency_ms: Optional[float] = None
    meta: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Explique AQI em linguagem simples.",
                "answer": "AQI é um índice que traduz a qualidade do ar...",
                "model": "gpt",
                "latency_ms": 123.4,
                "meta": {"tokens_in": 123, "tokens_out": 256},
            }
        }
    )


# ============================================================
# Exports explícitos (opcional, mas ajuda a evitar imports quebrados)
# ============================================================

__all__ = [
    # util
    "Pagination",
    "ErrorResponse",
    # stations
    "StationResponse",
    "StationDetailResponse",
    "StationListResponse",
    # health & metrics
    "HealthResponse",
    "MetricsResponse",
    # predictions
    "QualityLevel",
    "PredictionItem",
    "PredictionResponse",
    "PollutantPrediction",
    "RichPredictionEnvelope",
    "BatchPredictionResponse",
    # historical
    "HistoricalDataPoint",
    "HistoricalDataResponse",
    # llm
    "LLMAnswer",
]
