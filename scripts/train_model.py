#!/usr/bin/env python3
"""
Script para treinamento de modelos de predição da qualidade do ar.
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import logging

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.data.collectors import DataCollectionManager
from src.data.processors import DataProcessor
from src.models.base import BaseModel
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


class AirQualityModel(BaseModel):
    """
    Modelo de predição da qualidade do ar usando Random Forest.
    """
    
    def __init__(self):
        super().__init__("air_quality_rf")
        self.scaler = StandardScaler()
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """
        Treina o modelo Random Forest.
        """
        logger.info("Iniciando treinamento do modelo...")
        
        # Armazenar nomes das features
        self.feature_names = list(X.columns)
        
        # Dividir dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Normalizar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Treinar modelo
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Avaliar modelo
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Calcular métricas
        metrics = {
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, 
            cv=5, scoring='neg_mean_absolute_error'
        )
        metrics['cv_mae'] = -cv_scores.mean()
        metrics['cv_mae_std'] = cv_scores.std()
        
        self.is_trained = True
        self.metadata = {
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'features': self.feature_names,
            'metrics': metrics
        }
        
        logger.info(f"Treinamento concluído. MAE teste: {metrics['test_mae']:.2f}")
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Realiza predições.
        """
        if not self.is_trained:
            raise ValueError("Modelo não foi treinado")
        
        X_processed = self.preprocess_features(X)
        return self.model.predict(X_processed)


async def collect_training_data(cities: list, days_back: int = 90) -> pd.DataFrame:
    """
    Coleta dados para treinamento.
    """
    logger.info(f"Coletando dados de {len(cities)} cidades...")
    
    collector = DataCollectionManager()
    
    # Coletar dados de múltiplas cidades
    city_list = [{'name': city, 'state': 'SP'} for city in cities]
    all_data = await collector.collect_multiple_cities(city_list, days_back)
    
    # Combinar dados de todas as cidades
    combined_data = []
    
    for city, data in all_data.items():
        pollution_df = data['pollution']
        weather_df = data['weather']
        
        if not pollution_df.empty and not weather_df.empty:
            # Alinhar dados por timestamp
            merged = pd.merge_asof(
                pollution_df.sort_values('datetime'),
                weather_df.sort_values('datetime'),
                on='datetime',
                direction='nearest'
            )
            merged['city'] = city
            combined_data.append(merged)
    
    if combined_data:
        final_df = pd.concat(combined_data, ignore_index=True)
        logger.info(f"Dados coletados: {len(final_df)} registros")
        return final_df
    else:
        logger.warning("Nenhum dado foi coletado")
        return pd.DataFrame()


def prepare_training_data(df: pd.DataFrame) -> tuple:
    """
    Prepara dados para treinamento.
    """
    logger.info("Preparando dados para treinamento...")
    
    processor = DataProcessor()
    
    # Processar dados
    df_processed = processor.process_dataframe(df)
    
    # Definir features e target
    feature_columns = [
        'temperatura', 'umidade', 'vento_velocidade',
        'vento_direcao', 'precipitacao', 'pressao_atmosferica'
    ]
    
    target_column = 'value'  # PM2.5 value from OpenAQ
    
    # Filtrar colunas disponíveis
    available_features = [col for col in feature_columns if col in df_processed.columns]
    
    if not available_features:
        raise ValueError("Nenhuma feature disponível para treinamento")
    
    if target_column not in df_processed.columns:
        raise ValueError(f"Target '{target_column}' não encontrado nos dados")
    
    # Remover valores nulos
    df_clean = df_processed[available_features + [target_column]].dropna()
    
    X = df_clean[available_features]
    y = df_clean[target_column]
    
    logger.info(f"Dados preparados: {len(X)} amostras, {len(available_features)} features")
    return X, y


def generate_synthetic_data(n_samples: int = 1000) -> tuple:
    """
    Gera dados sintéticos para demonstração.
    """
    logger.info(f"Gerando {n_samples} amostras sintéticas...")
    
    np.random.seed(42)
    
    # Gerar features climáticas realistas
    temperatura = np.random.normal(25, 8, n_samples)  # 25°C ± 8°C
    umidade = np.random.normal(65, 15, n_samples)     # 65% ± 15%
    vento_velocidade = np.random.exponential(10, n_samples)  # Distribuição exponencial
    vento_direcao = np.random.uniform(0, 360, n_samples)
    precipitacao = np.random.exponential(2, n_samples)  # Maioria dos dias sem chuva
    pressao_atmosferica = np.random.normal(1013, 20, n_samples)
    
    # Garantir valores realistas
    umidade = np.clip(umidade, 10, 100)
    vento_velocidade = np.clip(vento_velocidade, 0, 50)
    precipitacao = np.clip(precipitacao, 0, 100)
    pressao_atmosferica = np.clip(pressao_atmosferica, 950, 1050)
    
    # Gerar PM2.5 baseado em relações realistas
    pm25 = (
        20 +  # Base
        (temperatura - 25) * 0.5 +  # Temperatura mais alta = mais poluição
        (65 - umidade) * 0.3 +      # Umidade baixa = mais poluição
        np.maximum(0, 15 - vento_velocidade) * 0.8 +  # Vento baixo = mais poluição
        np.maximum(0, 5 - precipitacao) * 2 +  # Sem chuva = mais poluição
        np.random.normal(0, 5, n_samples)  # Ruído
    )
    
    # Garantir valores positivos
    pm25 = np.maximum(pm25, 5)
    
    # Criar DataFrame
    X = pd.DataFrame({
        'temperatura': temperatura,
        'umidade': umidade,
        'vento_velocidade': vento_velocidade,
        'vento_direcao': vento_direcao,
        'precipitacao': precipitacao,
        'pressao_atmosferica': pressao_atmosferica
    })
    
    y = pd.Series(pm25, name='pm25')
    
    return X, y


async def main():
    """
    Função principal do script.
    """
    parser = argparse.ArgumentParser(description='Treinar modelo de qualidade do ar')
    parser.add_argument('--synthetic', action='store_true', 
                       help='Usar dados sintéticos em vez de dados reais')
    parser.add_argument('--cities', nargs='+', 
                       default=['São Paulo', 'Rio de Janeiro', 'Belo Horizonte'],
                       help='Cidades para coleta de dados')
    parser.add_argument('--days', type=int, default=90,
                       help='Número de dias de dados históricos')
    parser.add_argument('--output', type=str, 
                       default='models/production/modelo_qualidade_ar.pkl',
                       help='Caminho para salvar o modelo')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(log_level='INFO')
    
    try:
        # Preparar dados
        if args.synthetic:
            X, y = generate_synthetic_data(1000)
        else:
            # Coletar dados reais
            df = await collect_training_data(args.cities, args.days)
            
            if df.empty:
                logger.warning("Dados reais não disponíveis, usando dados sintéticos")
                X, y = generate_synthetic_data(1000)
            else:
                X, y = prepare_training_data(df)
        
        # Treinar modelo
        model = AirQualityModel()
        metrics = model.train(X, y)
        
        # Salvar modelo
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        model.save(str(output_path))
        
        # Exibir resultados
        print("\n=== Resultados do Treinamento ===")
        print(f"Modelo salvo em: {output_path}")
        print(f"Amostras de treino: {model.metadata['training_samples']}")
        print(f"Amostras de teste: {model.metadata['test_samples']}")
        print(f"Features: {len(model.feature_names)}")
        print("\n=== Métricas ===")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")
        
        # Importância das features
        importance = model.get_feature_importance()
        if importance:
            print("\n=== Importância das Features ===")
            for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                print(f"{feature}: {imp:.4f}")
        
        logger.info("Treinamento concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante o treinamento: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
