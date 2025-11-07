"""
Schemas de respostas da API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class QualityLevel(str, Enum):
    """
    Níveis de qualidade do ar.
    """
    EXCELENTE = "excelente"
    BOA = "boa"
    MODERADA = "moderada"
    RUIM = "ruim"
    MUITO_RUIM = "muito_ruim"
    PERIGOSA = "perigosa"


class PollutantPrediction(BaseModel):
    """
    Predição para um poluente específico.
    """
    valor: float = Field(..., description="Valor predito do poluente")
    unidade: str = Field(..., description="Unidade de medida")
    nivel_qualidade: QualityLevel = Field(..., description="Nível de qualidade")
    confianca: Optional[float] = Field(None, ge=0, le=1, description="Nível de confiança da predição")
    
    class Config:
        schema_extra = {
            "example": {
                "valor": 25.5,
                "unidade": "µg/m³",
                "nivel_qualidade": "moderada",
                "confianca": 0.85
            }
        }


class PredictionResponse(BaseModel):
    """
    Resposta de predição da qualidade do ar.
    """
    cidade: str = Field(..., description="Nome da cidade")
    data_predicao: date = Field(..., description="Data da predição")
    timestamp: datetime = Field(..., description="Timestamp da predição")
    
    class StationResponse(BaseModel):
        """
        Informações sobre uma estação de monitoramento.
        """
        id: int = Field(..., description="ID da estação")
        name: str = Field(..., description="Nome da estação")
        latitude: float = Field(..., description="Latitude da estação")
        longitude: float = Field(..., description="Longitude da estação")
        city: str = Field(..., description="Cidade da estação")
        state: str = Field(..., description="Estado da estação")
        country: str = Field(..., description="País da estação")
        
        class Config:
            schema_extra = {
                "example": {
                    "id": 1,
                    "name": "Estação Centro",
                    "latitude": -23.5505,
                    "longitude": -46.6333,
                    "city": "São Paulo",
                    "state": "SP",
                    "country": "BR"
                }
            }
    
    # Poluentes principais
    pm25: PollutantPrediction = Field(..., description="Predição para PM2.5")
    pm10: Optional[PollutantPrediction] = Field(None, description="Predição para PM10")
    no2: Optional[PollutantPrediction] = Field(None, description="Predição para NO2")
    o3: Optional[PollutantPrediction] = Field(None, description="Predição para O3")
    co: Optional[PollutantPrediction] = Field(None, description="Predição para CO")
    so2: Optional[PollutantPrediction] = Field(None, description="Predição para SO2")
    
    # Qualidade geral
    qualidade_geral: QualityLevel = Field(..., description="Qualidade geral do ar")
    indice_qualidade: float = Field(..., ge=0, le=500, description="Índice de qualidade do ar (0-500)")
    
    # Metadados
    modelo_versao: str = Field(..., description="Versão do modelo utilizado")
    confianca_geral: float = Field(..., ge=0, le=1, description="Confiança geral da predição")
    
    class Config:
        schema_extra = {
            "example": {
                "cidade": "São Paulo",
                "data_predicao": "2024-01-15",
                "timestamp": "2024-01-15T10:30:00Z",
                "pm25": {
                    "valor": 25.5,
                    "unidade": "µg/m³",
                    "nivel_qualidade": "moderada",
                    "confianca": 0.85
                },
                "pm10": {
                    "valor": 45.2,
                    "unidade": "µg/m³",
                    "nivel_qualidade": "moderada",
                    "confianca": 0.82
                },
                "qualidade_geral": "moderada",
                "indice_qualidade": 75.5,
                "modelo_versao": "1.0.0",
                "confianca_geral": 0.83
            }
        }


class BatchPredictionResponse(BaseModel):
    """
    Resposta para predições em lote.
    """
    cidade: str = Field(..., description="Nome da cidade")
    total_predicoes: int = Field(..., description="Número total de predições")
    predicoes: List[PredictionResponse] = Field(..., description="Lista de predições")
    tempo_processamento: float = Field(..., description="Tempo de processamento em segundos")
    
    class Config:
        schema_extra = {
            "example": {
                "cidade": "São Paulo",
                "total_predicoes": 2,
                "predicoes": [
                    {
                        "cidade": "São Paulo",
                        "data_predicao": "2024-01-15",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "pm25": {
                            "valor": 25.5,
                            "unidade": "µg/m³",
                            "nivel_qualidade": "moderada",
                            "confianca": 0.85
                        },
                        "qualidade_geral": "moderada",
                        "indice_qualidade": 75.5,
                        "modelo_versao": "1.0.0",
                        "confianca_geral": 0.83
                    }
                ],
                "tempo_processamento": 0.25
            }
        }


class HistoricalDataPoint(BaseModel):
    """
    Ponto de dados históricos.
    """
    data: date = Field(..., description="Data do registro")
    poluentes: Dict[str, float] = Field(..., description="Valores dos poluentes")
    clima: Optional[Dict[str, float]] = Field(None, description="Dados climáticos")
    qualidade: Optional[QualityLevel] = Field(None, description="Nível de qualidade")
    
    class Config:
        schema_extra = {
            "example": {
                "data": "2024-01-15",
                "poluentes": {
                    "pm25": 25.5,
                    "pm10": 45.2,
                    "no2": 35.8
                },
                "clima": {
                    "temperatura": 25.5,
                    "umidade": 65.0,
                    "vento_velocidade": 15.2
                },
                "qualidade": "moderada"
            }
        }


class HistoricalDataResponse(BaseModel):
    """
    Resposta de dados históricos.
    """
    cidade: str = Field(..., description="Nome da cidade")
    periodo: Dict[str, date] = Field(..., description="Período dos dados")
    total_registros: int = Field(..., description="Número total de registros")
    dados: List[HistoricalDataPoint] = Field(..., description="Dados históricos")
    estatisticas: Optional[Dict[str, Any]] = Field(None, description="Estatísticas dos dados")
    
    class Config:
        schema_extra = {
            "example": {
                "cidade": "São Paulo",
                "periodo": {
                    "inicio": "2024-01-01",
                    "fim": "2024-01-31"
                },
                "total_registros": 31,
                "dados": [
                    {
                        "data": "2024-01-15",
                        "poluentes": {
                            "pm25": 25.5,
                            "pm10": 45.2
                        },
                        "qualidade": "moderada"
                    }
                ],
                "estatisticas": {
                    "pm25_media": 23.8,
                    "pm25_max": 45.2,
                    "pm25_min": 12.1
                }
            }
        }


class HealthResponse(BaseModel):
    """
    Resposta de status de saúde da API.
    """
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    versao: str = Field(..., description="Versão da API")
    modelo_carregado: bool = Field(..., description="Status do carregamento do modelo")
    banco_conectado: bool = Field(..., description="Status da conexão com banco")
    uptime: float = Field(..., description="Tempo de atividade em segundos")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "versao": "1.0.0",
                "modelo_carregado": True,
                "banco_conectado": True,
                "uptime": 3600.5
            }
        }


class ErrorResponse(BaseModel):
    """
    Resposta de erro padrão.
    """
    error: bool = Field(True, description="Indica se é uma resposta de erro")
    message: str = Field(..., description="Mensagem de erro")
    status_code: int = Field(..., description="Código de status HTTP")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(..., description="Timestamp do erro")
    
    class Config:
        schema_extra = {
            "example": {
                "error": True,
                "message": "Dados de entrada inválidos",
                "status_code": 400,
                "details": {
                    "field": "temperatura",
                    "issue": "Valor fora do intervalo permitido"
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
