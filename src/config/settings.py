"""
Configurações do projeto de qualidade do ar.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Configurações da aplicação
    APP_NAME: str = "API de Predição da Qualidade do Ar"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Configurações do servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Configurações de banco de dados
    MONGODB_URL: Optional[str] = None
    DATABASE_NAME: str = "qualidade_ar"
    
    # Configurações de APIs externas
    OPENAQ_API_URL: str = "https://api.openaq.org/v2"
    OPENAQ_API_KEY: Optional[str] = None
    
    # Configurações de dados INMET
    INMET_BASE_URL: str = "https://portal.inmet.gov.br/dadoshistoricos"
    
    # Configurações de modelos
    MODEL_PATH: str = "models/production"
    MODEL_NAME: str = "modelo_qualidade_ar.pkl"
    
    # Configurações de cache
    CACHE_TTL: int = 3600  # 1 hora em segundos
    
    # Configurações de logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configurações de CORS
    ALLOWED_ORIGINS: list = ["*", "https://5174-i5rd7yb40dyiyhjy5foyd-f093ec88.manus.computer"]
    ALLOWED_METHODS: list = ["GET", "POST", "PUT", "DELETE"]
    ALLOWED_HEADERS: list = ["*"]
    
    # Configurações de rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hora
    
    # Configurações de predição
    MAX_PREDICTION_DAYS: int = 7
    DEFAULT_CITY: str = "São Paulo"
    
    # Configurações de features
    CLIMATE_FEATURES: list = [
        "temperatura",
        "umidade", 
        "vento_velocidade",
        "vento_direcao",
        "precipitacao",
        "pressao_atmosferica"
    ]
    
    POLLUTION_TARGETS: list = [
        "pm25",
        "pm10", 
        "no2",
        "o3",
        "co",
        "so2"
    ]
    
    # Configurações de processamento
    MISSING_VALUE_STRATEGY: str = "interpolate"  # interpolate, mean, median, drop
    OUTLIER_DETECTION_METHOD: str = "iqr"  # iqr, zscore, isolation_forest
    FEATURE_SCALING_METHOD: str = "standard"  # standard, minmax, robust
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global das configurações
settings = Settings()


# Configurações específicas por ambiente
class DevelopmentSettings(Settings):
    """Configurações para desenvolvimento."""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class ProductionSettings(Settings):
    """Configurações para produção."""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    ALLOWED_ORIGINS: list = [
        "https://seu-dominio.com",
        "https://www.seu-dominio.com"
    ]


class TestingSettings(Settings):
    """Configurações para testes."""
    DEBUG: bool = True
    DATABASE_NAME: str = "qualidade_ar_test"
    LOG_LEVEL: str = "DEBUG"


def get_settings() -> Settings:
    """
    Retorna as configurações baseadas no ambiente.
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
