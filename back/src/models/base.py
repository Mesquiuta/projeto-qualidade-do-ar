"""
Classes base para modelos de machine learning.
"""

import joblib
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from datetime import datetime

from src.config import settings

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Classe base abstrata para modelos de predição.
    """
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.is_trained = False
        self.version = "1.0.0"
        self.metadata = {}
    
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Treina o modelo com os dados fornecidos.
        
        Args:
            X: Features de entrada
            y: Target variable
            
        Returns:
            Métricas de treinamento
        """
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Realiza predições com o modelo treinado.
        
        Args:
            X: Features de entrada
            
        Returns:
            Predições
        """
        pass
    
    def save(self, filepath: str) -> None:
        """
        Salva o modelo treinado.
        
        Args:
            filepath: Caminho para salvar o modelo
        """
        if not self.is_trained:
            raise ValueError("Modelo deve ser treinado antes de ser salvo")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'version': self.version,
            'metadata': self.metadata,
            'model_name': self.model_name,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Modelo salvo em: {filepath}")
    
    def load(self, filepath: str) -> None:
        """
        Carrega um modelo salvo.
        
        Args:
            filepath: Caminho do modelo salvo
        """
        try:
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data.get('scaler')
            self.feature_names = model_data.get('feature_names')
            self.version = model_data.get('version', '1.0.0')
            self.metadata = model_data.get('metadata', {})
            self.model_name = model_data.get('model_name', self.model_name)
            self.is_trained = True
            
            logger.info(f"Modelo carregado: {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            raise
    
    def preprocess_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Pré-processa as features de entrada.
        
        Args:
            X: Features brutas
            
        Returns:
            Features processadas
        """
        # Garantir que as colunas estejam na ordem correta
        if self.feature_names:
            missing_cols = set(self.feature_names) - set(X.columns)
            if missing_cols:
                raise ValueError(f"Features faltando: {missing_cols}")
            
            X = X[self.feature_names]
        
        # Aplicar scaling se disponível
        if self.scaler:
            X_scaled = self.scaler.transform(X)
            X = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        return X
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Retorna a importância das features se disponível.
        
        Returns:
            Dicionário com importância das features
        """
        if not self.is_trained:
            return None
        
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            if self.feature_names:
                return dict(zip(self.feature_names, importance))
        
        return None


class DummyModel(BaseModel):
    """
    Modelo dummy para testes e desenvolvimento.
    """
    
    def __init__(self):
        super().__init__("dummy_model")
        self.is_trained = True
        self.version = "1.0.0"
        self.feature_names = [
            'temperatura', 'umidade', 'vento_velocidade',
            'vento_direcao', 'precipitacao', 'pressao_atmosferica'
        ]
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Simula treinamento do modelo dummy.
        """
        self.is_trained = True
        return {
            'mae': 5.2,
            'rmse': 7.8,
            'r2': 0.75
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Gera predições dummy baseadas em regras simples.
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado")
        
        # Regras simples baseadas nos dados climáticos
        predictions = []
        
        for _, row in X.iterrows():
            # PM2.5 base
            pm25 = 20.0
            
            # Ajustar baseado na temperatura
            if row['temperatura'] > 30:
                pm25 += 10
            elif row['temperatura'] < 15:
                pm25 += 5
            
            # Ajustar baseado na umidade
            if row['umidade'] < 40:
                pm25 += 8
            elif row['umidade'] > 80:
                pm25 -= 3
            
            # Ajustar baseado no vento
            if row['vento_velocidade'] > 20:
                pm25 -= 5
            elif row['vento_velocidade'] < 5:
                pm25 += 7
            
            # Ajustar baseado na precipitação
            if row['precipitacao'] > 5:
                pm25 -= 10
            
            # Adicionar alguma variabilidade
            pm25 += np.random.normal(0, 3)
            
            # Garantir valores positivos
            pm25 = max(5.0, pm25)
            
            predictions.append(pm25)
        
        return np.array(predictions)


class ModelManager:
    """
    Gerenciador de modelos para a aplicação.
    """
    
    def __init__(self):
        self.models = {}
        self.current_model = None
        self.model_path = Path(settings.MODEL_PATH)
        self.model_path.mkdir(parents=True, exist_ok=True)
    
    async def load_models(self) -> None:
        """
        Carrega todos os modelos disponíveis.
        """
        try:
            # Tentar carregar modelo de produção
            production_model_path = self.model_path / settings.MODEL_NAME
            
            if production_model_path.exists():
                model = DummyModel()  # Por enquanto usar dummy
                model.load(str(production_model_path))
                self.models['production'] = model
                self.current_model = model
                logger.info("Modelo de produção carregado")
            else:
                # Usar modelo dummy se não houver modelo treinado
                self.current_model = DummyModel()
                self.models['dummy'] = self.current_model
                logger.info("Usando modelo dummy (modelo de produção não encontrado)")
                
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {e}")
            # Fallback para modelo dummy
            self.current_model = DummyModel()
            self.models['dummy'] = self.current_model
            logger.info("Fallback para modelo dummy")
    
    def is_loaded(self) -> bool:
        """
        Verifica se há um modelo carregado.
        """
        return self.current_model is not None and self.current_model.is_trained
    
    async def predict(self, climate_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Realiza predição usando o modelo atual.
        
        Args:
            climate_data: Dados climáticos
            
        Returns:
            Predições e metadados
        """
        if not self.is_loaded():
            raise ValueError("Nenhum modelo carregado")
        
        # Converter para DataFrame
        df = pd.DataFrame([climate_data])
        
        # Garantir que todas as features necessárias estejam presentes
        required_features = self.current_model.feature_names or list(climate_data.keys())
        
        for feature in required_features:
            if feature not in df.columns:
                df[feature] = 0.0  # Valor padrão
        
        # Pré-processar
        df_processed = self.current_model.preprocess_features(df)
        
        # Predizer
        prediction = self.current_model.predict(df_processed)[0]
        
        # Retornar resultado estruturado
        return {
            'pm25': float(prediction),
            'pm25_confidence': 0.8,
            'pm10': float(prediction * 1.8),  # Estimativa baseada em PM2.5
            'pm10_confidence': 0.75,
            'no2': float(prediction * 1.4),   # Estimativa baseada em PM2.5
            'no2_confidence': 0.7,
            'overall_confidence': 0.75
        }
    
    def get_version(self) -> str:
        """
        Retorna a versão do modelo atual.
        """
        if self.current_model:
            return self.current_model.version
        return "unknown"
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o modelo atual.
        """
        if not self.current_model:
            return {}
        
        return {
            'name': self.current_model.model_name,
            'version': self.current_model.version,
            'is_trained': self.current_model.is_trained,
            'feature_names': self.current_model.feature_names,
            'metadata': self.current_model.metadata
        }
