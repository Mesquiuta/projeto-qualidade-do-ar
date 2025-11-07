"""
Configuração de logging para o projeto.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from src.config import settings


class JSONFormatter(logging.Formatter):
    """
    Formatter para logs em formato JSON.
    """
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adicionar informações de exceção se disponível
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Adicionar campos extras se disponíveis
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    Formatter com cores para terminal.
    """
    
    # Códigos de cor ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Ciano
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarelo
        'ERROR': '\033[31m',      # Vermelho
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Aplicar cor baseada no nível
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formatar mensagem
        formatted = super().format(record)
        
        # Aplicar cor apenas ao nível
        formatted = formatted.replace(
            record.levelname,
            f"{color}{record.levelname}{reset}"
        )
        
        return formatted


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_format: bool = False,
    enable_colors: bool = True
) -> None:
    """
    Configura o sistema de logging da aplicação.
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho para arquivo de log (opcional)
        json_format: Se deve usar formato JSON
        enable_colors: Se deve usar cores no terminal
    """
    # Usar configurações padrão se não especificado
    log_level = log_level or settings.LOG_LEVEL
    
    # Configurar logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if json_format:
        console_formatter = JSONFormatter()
    elif enable_colors and sys.stdout.isatty():
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            fmt=settings.LOG_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para arquivo se especificado
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Usar RotatingFileHandler para evitar arquivos muito grandes
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Sempre usar JSON para arquivos
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Configurar loggers específicos
    configure_specific_loggers()
    
    # Log inicial
    logger = logging.getLogger(__name__)
    logger.info(f"Sistema de logging configurado - Nível: {log_level}")


def configure_specific_loggers():
    """
    Configura loggers específicos para bibliotecas externas.
    """
    # Reduzir verbosidade de bibliotecas externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Configurar logger do FastAPI
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    
    # Configurar logger do scikit-learn
    logging.getLogger('sklearn').setLevel(logging.WARNING)


class LoggerMixin:
    """
    Mixin para adicionar logger a classes.
    """
    
    @property
    def logger(self):
        """Retorna logger específico para a classe."""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(
                f"{self.__class__.__module__}.{self.__class__.__name__}"
            )
        return self._logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém logger com nome específico.
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


class StructuredLogger:
    """
    Logger estruturado para facilitar análise de logs.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time: float,
        user_id: Optional[str] = None
    ):
        """Log estruturado para requisições da API."""
        extra_fields = {
            'event_type': 'api_request',
            'method': method,
            'path': path,
            'status_code': status_code,
            'response_time_ms': response_time * 1000,
            'user_id': user_id
        }
        
        # Determinar nível baseado no status code
        if status_code >= 500:
            level = logging.ERROR
        elif status_code >= 400:
            level = logging.WARNING
        else:
            level = logging.INFO
        
        record = logging.LogRecord(
            name=self.logger.name,
            level=level,
            pathname='',
            lineno=0,
            msg=f"{method} {path} - {status_code} ({response_time:.3f}s)",
            args=(),
            exc_info=None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)
    
    def log_model_prediction(
        self,
        model_name: str,
        input_features: dict,
        prediction: float,
        confidence: float,
        processing_time: float
    ):
        """Log estruturado para predições do modelo."""
        extra_fields = {
            'event_type': 'model_prediction',
            'model_name': model_name,
            'input_features': input_features,
            'prediction': prediction,
            'confidence': confidence,
            'processing_time_ms': processing_time * 1000
        }
        
        record = logging.LogRecord(
            name=self.logger.name,
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg=f"Predição realizada - Modelo: {model_name}, Resultado: {prediction:.2f}",
            args=(),
            exc_info=None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)
    
    def log_data_collection(
        self,
        source: str,
        records_collected: int,
        time_range: dict,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log estruturado para coleta de dados."""
        extra_fields = {
            'event_type': 'data_collection',
            'source': source,
            'records_collected': records_collected,
            'time_range': time_range,
            'success': success,
            'error_message': error_message
        }
        
        level = logging.INFO if success else logging.ERROR
        message = f"Coleta de dados - Fonte: {source}, Registros: {records_collected}"
        
        if not success and error_message:
            message += f", Erro: {error_message}"
        
        record = logging.LogRecord(
            name=self.logger.name,
            level=level,
            pathname='',
            lineno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        record.extra_fields = extra_fields
        
        self.logger.handle(record)
