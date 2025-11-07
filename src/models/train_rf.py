#!/usr/bin/env python3
"""
Script para treinamento de modelos de predição da qualidade do ar.
Fase 1: Pipeline de Treino (artefatos)

Treina LinearRegression e RandomForest, compara por RMSE/MAE/R² e salva:
- model.joblib (modelo vencedor)
- model.metadata.json (métricas, features, modelo vencedor, timestamp)
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import logging

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_synthetic_data(n_samples: int = 1000) -> tuple:
    """
    Gera dados sintéticos para demonstração.
    
    Args:
        n_samples: Número de amostras a gerar
        
    Returns:
        Tupla (X, y) com features e target
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
    
    logger.info(f"Dados sintéticos gerados: {len(X)} amostras, {len(X.columns)} features")
    return X, y


def train_and_evaluate_models(X: pd.DataFrame, y: pd.Series) -> dict:
    """
    Treina LinearRegression e RandomForest, compara e retorna o melhor.
    
    Args:
        X: Features de entrada
        y: Target variable
        
    Returns:
        Dicionário com modelo vencedor, scaler, métricas e metadados
    """
    logger.info("Iniciando treinamento de modelos...")
    
    # Armazenar nomes das features
    feature_names = list(X.columns)
    
    # Dividir dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    logger.info(f"Dados divididos: {len(X_train)} treino, {len(X_test)} teste")
    
    # Normalizar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Dicionário para armazenar modelos e métricas
    models = {}
    
    # 1. Treinar LinearRegression
    logger.info("Treinando LinearRegression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train_scaled, y_train)
    
    y_pred_train_lr = lr_model.predict(X_train_scaled)
    y_pred_test_lr = lr_model.predict(X_test_scaled)
    
    lr_metrics = {
        'train_mae': float(mean_absolute_error(y_train, y_pred_train_lr)),
        'train_rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train_lr))),
        'train_r2': float(r2_score(y_train, y_pred_train_lr)),
        'test_mae': float(mean_absolute_error(y_test, y_pred_test_lr)),
        'test_rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test_lr))),
        'test_r2': float(r2_score(y_test, y_pred_test_lr))
    }
    
    models['LinearRegression'] = {
        'model': lr_model,
        'metrics': lr_metrics
    }
    
    logger.info(f"LinearRegression - MAE teste: {lr_metrics['test_mae']:.4f}, "
                f"RMSE teste: {lr_metrics['test_rmse']:.4f}, R² teste: {lr_metrics['test_r2']:.4f}")
    
    # 2. Treinar RandomForest
    logger.info("Treinando RandomForest...")
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)
    
    y_pred_train_rf = rf_model.predict(X_train_scaled)
    y_pred_test_rf = rf_model.predict(X_test_scaled)
    
    rf_metrics = {
        'train_mae': float(mean_absolute_error(y_train, y_pred_train_rf)),
        'train_rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train_rf))),
        'train_r2': float(r2_score(y_train, y_pred_train_rf)),
        'test_mae': float(mean_absolute_error(y_test, y_pred_test_rf)),
        'test_rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test_rf))),
        'test_r2': float(r2_score(y_test, y_pred_test_rf))
    }
    
    models['RandomForest'] = {
        'model': rf_model,
        'metrics': rf_metrics
    }
    
    logger.info(f"RandomForest - MAE teste: {rf_metrics['test_mae']:.4f}, "
                f"RMSE teste: {rf_metrics['test_rmse']:.4f}, R² teste: {rf_metrics['test_r2']:.4f}")
    
    # 3. Selecionar melhor modelo baseado em RMSE de teste (menor é melhor)
    logger.info("Selecionando melhor modelo...")
    
    best_model_name = None
    best_rmse = float('inf')
    
    for model_name, model_data in models.items():
        test_rmse = model_data['metrics']['test_rmse']
        if test_rmse < best_rmse:
            best_rmse = test_rmse
            best_model_name = model_name
    
    logger.info(f"Modelo vencedor: {best_model_name} (RMSE teste: {best_rmse:.4f})")
    
    # Preparar resultado
    winner_data = models[best_model_name]
    
    result = {
        'model': winner_data['model'],
        'scaler': scaler,
        'feature_names': feature_names,
        'winner': best_model_name,
        'metrics': {
            best_model_name: winner_data['metrics'],
            'all_models': {name: data['metrics'] for name, data in models.items()}
        },
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'trained_at': datetime.utcnow().isoformat()
    }
    
    return result


def save_model_artifacts(model_data: dict, output_dir: str) -> None:
    """
    Salva model.joblib e model.metadata.json.
    
    Args:
        model_data: Dados do modelo treinado
        output_dir: Diretório de saída
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Salvar model.joblib
    model_path = output_path / "model.joblib"
    joblib_data = {
        'model': model_data['model'],
        'scaler': model_data['scaler'],
        'feature_names': model_data['feature_names']
    }
    joblib.dump(joblib_data, model_path)
    logger.info(f"Modelo salvo em: {model_path}")
    
    # 2. Salvar model.metadata.json
    metadata_path = output_path / "model.metadata.json"
    metadata = {
        'winner': model_data['winner'],
        'metrics': model_data['metrics'],
        'features': model_data['feature_names'],
        'trained_at': model_data['trained_at'],
        'training_samples': model_data['training_samples'],
        'test_samples': model_data['test_samples']
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Metadata salvo em: {metadata_path}")


def main():
    """
    Função principal do script.
    """
    parser = argparse.ArgumentParser(
        description='Treinar modelos de qualidade do ar (Fase 1)'
    )
    parser.add_argument(
        '--samples', 
        type=int, 
        default=1000,
        help='Número de amostras sintéticas a gerar'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='models/production',
        help='Diretório para salvar os artefatos'
    )
    
    args = parser.parse_args()
    
    try:
        # 1. Gerar dados sintéticos
        X, y = generate_synthetic_data(args.samples)
        
        # 2. Treinar e avaliar modelos
        model_data = train_and_evaluate_models(X, y)
        
        # 3. Salvar artefatos
        save_model_artifacts(model_data, args.output_dir)
        
        # 4. Exibir resumo
        print("\n" + "="*60)
        print("FASE 1 CONCLUÍDA - Pipeline de Treino")
        print("="*60)
        print(f"\n✓ Modelo vencedor: {model_data['winner']}")
        print(f"✓ Amostras de treino: {model_data['training_samples']}")
        print(f"✓ Amostras de teste: {model_data['test_samples']}")
        print(f"✓ Features: {len(model_data['feature_names'])}")
        print(f"\nMétricas do modelo vencedor ({model_data['winner']}):")
        winner_metrics = model_data['metrics'][model_data['winner']]
        print(f"  - MAE (teste): {winner_metrics['test_mae']:.4f}")
        print(f"  - RMSE (teste): {winner_metrics['test_rmse']:.4f}")
        print(f"  - R² (teste): {winner_metrics['test_r2']:.4f}")
        print(f"\nArtefatos salvos em: {args.output_dir}/")
        print(f"  - model.joblib")
        print(f"  - model.metadata.json")
        print("="*60 + "\n")
        
        logger.info("Pipeline de treino concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante o treinamento: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

