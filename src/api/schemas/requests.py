"""
Schemas de requisições da API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date


class ClimateDataRequest(BaseModel):
    """
    Schema para dados climáticos de entrada.
    """
    temperatura: float = Field(
        ..., 
        ge=-50, 
        le=60, 
        description="Temperatura em graus Celsius"
    )
    umidade: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Umidade relativa do ar em porcentagem"
    )
    vento_velocidade: float = Field(
        ..., 
        ge=0, 
        le=200, 
        description="Velocidade do vento em km/h"
    )
    vento_direcao: Optional[float] = Field(
        None, 
        ge=0, 
        le=360, 
        description="Direção do vento em graus (0-360)"
    )
    precipitacao: float = Field(
        ..., 
        ge=0, 
        le=1000, 
        description="Precipitação em mm"
    )
    pressao_atmosferica: Optional[float] = Field(
        None, 
        ge=800, 
        le=1200, 
        description="Pressão atmosférica em hPa"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "temperatura": 25.5,
                "umidade": 65.0,
                "vento_velocidade": 15.2,
                "vento_direcao": 180.0,
                "precipitacao": 0.0,
                "pressao_atmosferica": 1013.25
            }
        }


class PredictionRequest(BaseModel):
    """
    Schema para requisição de predição.
    """
    cidade: Optional[str] = Field(
        None, 
        description="Nome da cidade para predição"
    )
    dados_climaticos: ClimateDataRequest = Field(
        ..., 
        description="Dados climáticos para predição"
    )
    data_predicao: Optional[date] = Field(
        None, 
        description="Data para a predição (formato YYYY-MM-DD)"
    )
    incluir_historico: bool = Field(
        False, 
        description="Incluir dados históricos na resposta"
    )
    
    @validator('cidade')
    def validate_cidade(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Nome da cidade deve ter pelo menos 2 caracteres')
        return v.strip() if v else None
    
    class Config:
        schema_extra = {
            "example": {
                "cidade": "São Paulo",
                "dados_climaticos": {
                    "temperatura": 25.5,
                    "umidade": 65.0,
                    "vento_velocidade": 15.2,
                    "vento_direcao": 180.0,
                    "precipitacao": 0.0,
                    "pressao_atmosferica": 1013.25
                },
                "data_predicao": "2024-01-15",
                "incluir_historico": False
            }
        }


class BatchPredictionRequest(BaseModel):
    """
    Schema para predições em lote.
    """
    cidade: Optional[str] = Field(
        None, 
        description="Nome da cidade para predições"
    )
    dados_climaticos: List[ClimateDataRequest] = Field(
        ..., 
        min_items=1, 
        max_items=100,
        description="Lista de dados climáticos para predição"
    )
    datas_predicao: Optional[List[date]] = Field(
        None, 
        description="Datas correspondentes para cada predição"
    )
    
    @validator('datas_predicao')
    def validate_datas_predicao(cls, v, values):
        if v and 'dados_climaticos' in values:
            if len(v) != len(values['dados_climaticos']):
                raise ValueError('Número de datas deve corresponder ao número de dados climáticos')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "cidade": "São Paulo",
                "dados_climaticos": [
                    {
                        "temperatura": 25.5,
                        "umidade": 65.0,
                        "vento_velocidade": 15.2,
                        "vento_direcao": 180.0,
                        "precipitacao": 0.0,
                        "pressao_atmosferica": 1013.25
                    }
                ],
                "datas_predicao": ["2024-01-15"]
            }
        }


class HistoricalDataRequest(BaseModel):
    """
    Schema para requisição de dados históricos.
    """
    cidade: str = Field(
        ..., 
        description="Nome da cidade"
    )
    data_inicio: date = Field(
        ..., 
        description="Data de início (formato YYYY-MM-DD)"
    )
    data_fim: date = Field(
        ..., 
        description="Data de fim (formato YYYY-MM-DD)"
    )
    poluentes: Optional[List[str]] = Field(
        None, 
        description="Lista de poluentes desejados (pm25, pm10, no2, o3, co, so2)"
    )
    
    @validator('data_fim')
    def validate_data_fim(cls, v, values):
        if 'data_inicio' in values and v < values['data_inicio']:
            raise ValueError('Data de fim deve ser posterior à data de início')
        return v
    
    @validator('poluentes')
    def validate_poluentes(cls, v):
        valid_poluentes = {'pm25', 'pm10', 'no2', 'o3', 'co', 'so2'}
        if v:
            invalid = set(v) - valid_poluentes
            if invalid:
                raise ValueError(f'Poluentes inválidos: {invalid}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "cidade": "São Paulo",
                "data_inicio": "2024-01-01",
                "data_fim": "2024-01-31",
                "poluentes": ["pm25", "pm10", "no2"]
            }
        }
