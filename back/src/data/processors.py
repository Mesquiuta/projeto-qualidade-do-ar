"""
Processadores de dados para limpeza e preparação.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.ensemble import IsolationForest
from scipy import stats
import logging

from src.config import settings
from src.utils.logging import LoggerMixin

logger = logging.getLogger(__name__)


class DataProcessor(LoggerMixin):
    """
    Processador principal para limpeza e preparação de dados.
    """
    
    def __init__(self):
        self.scalers = {}
        self.imputers = {}
        self.outlier_detectors = {}
        self.feature_stats = {}
    
    def process_dataframe(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None,
        fit_transformers: bool = True
    ) -> pd.DataFrame:
        """
        Processa um DataFrame completo.
        
        Args:
            df: DataFrame a ser processado
            target_column: Nome da coluna target (não será processada)
            fit_transformers: Se deve ajustar os transformadores
            
        Returns:
            DataFrame processado
        """
        self.logger.info(f"Processando DataFrame com {len(df)} registros e {len(df.columns)} colunas")
        
        df_processed = df.copy()
        
        # Identificar colunas numéricas e categóricas
        numeric_columns = df_processed.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df_processed.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remover target das colunas a processar
        if target_column and target_column in numeric_columns:
            numeric_columns.remove(target_column)
        
        # Processar colunas numéricas
        if numeric_columns:
            df_processed = self._process_numeric_columns(
                df_processed, numeric_columns, fit_transformers
            )
        
        # Processar colunas categóricas
        if categorical_columns:
            df_processed = self._process_categorical_columns(
                df_processed, categorical_columns, fit_transformers
            )
        
        # Criar features derivadas
        df_processed = self._create_derived_features(df_processed)
        
        self.logger.info(f"Processamento concluído. DataFrame final: {len(df_processed)} registros")
        return df_processed
    
    def _process_numeric_columns(
        self,
        df: pd.DataFrame,
        columns: List[str],
        fit_transformers: bool
    ) -> pd.DataFrame:
        """
        Processa colunas numéricas.
        """
        df_processed = df.copy()
        
        for column in columns:
            if column not in df_processed.columns:
                continue
            
            self.logger.debug(f"Processando coluna numérica: {column}")
            
            # 1. Tratar valores ausentes
            df_processed[column] = self._handle_missing_values(
                df_processed[column], column, fit_transformers
            )
            
            # 2. Detectar e tratar outliers
            df_processed[column] = self._handle_outliers(
                df_processed[column], column, fit_transformers
            )
            
            # 3. Normalizar/Padronizar
            df_processed[column] = self._scale_feature(
                df_processed[column], column, fit_transformers
            )
        
        return df_processed
    
    def _process_categorical_columns(
        self,
        df: pd.DataFrame,
        columns: List[str],
        fit_transformers: bool
    ) -> pd.DataFrame:
        """
        Processa colunas categóricas.
        """
        df_processed = df.copy()
        
        for column in columns:
            if column not in df_processed.columns:
                continue
            
            self.logger.debug(f"Processando coluna categórica: {column}")
            
            # Tratar valores ausentes
            df_processed[column] = df_processed[column].fillna('unknown')
            
            # Encoding (por enquanto, manter como string)
            # TODO: Implementar one-hot encoding ou label encoding conforme necessário
        
        return df_processed
    
    def _handle_missing_values(
        self,
        series: pd.Series,
        column_name: str,
        fit_transformer: bool
    ) -> pd.Series:
        """
        Trata valores ausentes em uma série.
        """
        if series.isna().sum() == 0:
            return series
        
        strategy = settings.MISSING_VALUE_STRATEGY
        
        if fit_transformer or column_name not in self.imputers:
            if strategy == 'interpolate':
                # Interpolação linear
                filled_series = series.interpolate(method='linear')
                # Preencher valores ainda ausentes com a média
                filled_series = filled_series.fillna(series.mean())
            elif strategy in ['mean', 'median', 'most_frequent']:
                imputer = SimpleImputer(strategy=strategy)
                filled_values = imputer.fit_transform(series.values.reshape(-1, 1)).flatten()
                filled_series = pd.Series(filled_values, index=series.index)
                if fit_transformer:
                    self.imputers[column_name] = imputer
            elif strategy == 'knn':
                imputer = KNNImputer(n_neighbors=5)
                filled_values = imputer.fit_transform(series.values.reshape(-1, 1)).flatten()
                filled_series = pd.Series(filled_values, index=series.index)
                if fit_transformer:
                    self.imputers[column_name] = imputer
            else:
                # Drop strategy - manter NaN para remoção posterior
                filled_series = series
        else:
            # Usar imputer já ajustado
            imputer = self.imputers[column_name]
            filled_values = imputer.transform(series.values.reshape(-1, 1)).flatten()
            filled_series = pd.Series(filled_values, index=series.index)
        
        missing_count = series.isna().sum()
        if missing_count > 0:
            self.logger.debug(f"Preenchidos {missing_count} valores ausentes em {column_name}")
        
        return filled_series
    
    def _handle_outliers(
        self,
        series: pd.Series,
        column_name: str,
        fit_transformer: bool
    ) -> pd.Series:
        """
        Detecta e trata outliers.
        """
        method = settings.OUTLIER_DETECTION_METHOD
        
        if method == 'iqr':
            return self._handle_outliers_iqr(series)
        elif method == 'zscore':
            return self._handle_outliers_zscore(series)
        elif method == 'isolation_forest':
            return self._handle_outliers_isolation_forest(
                series, column_name, fit_transformer
            )
        else:
            return series
    
    def _handle_outliers_iqr(self, series: pd.Series, factor: float = 1.5) -> pd.Series:
        """
        Remove outliers usando método IQR.
        """
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        
        # Substituir outliers pelos limites
        series_clean = series.clip(lower_bound, upper_bound)
        
        outliers_count = ((series < lower_bound) | (series > upper_bound)).sum()
        if outliers_count > 0:
            self.logger.debug(f"Tratados {outliers_count} outliers usando IQR")
        
        return series_clean
    
    def _handle_outliers_zscore(self, series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """
        Remove outliers usando Z-score.
        """
        z_scores = np.abs(stats.zscore(series.dropna()))
        
        # Identificar outliers
        outlier_mask = z_scores > threshold
        
        if outlier_mask.any():
            # Substituir outliers pela mediana
            median_value = series.median()
            series_clean = series.copy()
            series_clean.iloc[series.dropna().index[outlier_mask]] = median_value
            
            outliers_count = outlier_mask.sum()
            self.logger.debug(f"Tratados {outliers_count} outliers usando Z-score")
            
            return series_clean
        
        return series
    
    def _handle_outliers_isolation_forest(
        self,
        series: pd.Series,
        column_name: str,
        fit_transformer: bool
    ) -> pd.Series:
        """
        Remove outliers usando Isolation Forest.
        """
        if fit_transformer or column_name not in self.outlier_detectors:
            detector = IsolationForest(contamination=0.1, random_state=42)
            
            # Ajustar apenas em valores não-nulos
            valid_data = series.dropna().values.reshape(-1, 1)
            if len(valid_data) > 0:
                detector.fit(valid_data)
                if fit_transformer:
                    self.outlier_detectors[column_name] = detector
            else:
                return series
        else:
            detector = self.outlier_detectors[column_name]
        
        # Detectar outliers
        predictions = detector.predict(series.dropna().values.reshape(-1, 1))
        outlier_mask = predictions == -1
        
        if outlier_mask.any():
            # Substituir outliers pela mediana
            median_value = series.median()
            series_clean = series.copy()
            series_clean.iloc[series.dropna().index[outlier_mask]] = median_value
            
            outliers_count = outlier_mask.sum()
            self.logger.debug(f"Tratados {outliers_count} outliers usando Isolation Forest")
            
            return series_clean
        
        return series
    
    def _scale_feature(
        self,
        series: pd.Series,
        column_name: str,
        fit_transformer: bool
    ) -> pd.Series:
        """
        Normaliza/padroniza uma feature.
        """
        method = settings.FEATURE_SCALING_METHOD
        
        if fit_transformer or column_name not in self.scalers:
            if method == 'standard':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()
            elif method == 'robust':
                scaler = RobustScaler()
            else:
                return series  # Sem scaling
            
            # Ajustar scaler
            valid_data = series.dropna().values.reshape(-1, 1)
            if len(valid_data) > 0:
                scaler.fit(valid_data)
                if fit_transformer:
                    self.scalers[column_name] = scaler
            else:
                return series
        else:
            scaler = self.scalers[column_name]
        
        # Aplicar scaling
        scaled_values = scaler.transform(series.values.reshape(-1, 1)).flatten()
        scaled_series = pd.Series(scaled_values, index=series.index)
        
        return scaled_series
    
    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features derivadas.
        """
        df_enhanced = df.copy()
        
        # Features temporais se houver coluna de datetime
        if 'datetime' in df_enhanced.columns:
            df_enhanced['hour'] = pd.to_datetime(df_enhanced['datetime']).dt.hour
            df_enhanced['day_of_week'] = pd.to_datetime(df_enhanced['datetime']).dt.dayofweek
            df_enhanced['month'] = pd.to_datetime(df_enhanced['datetime']).dt.month
            df_enhanced['is_weekend'] = (df_enhanced['day_of_week'] >= 5).astype(int)
        
        # Features climáticas derivadas
        if 'temperatura' in df_enhanced.columns and 'umidade' in df_enhanced.columns:
            # Índice de calor simplificado
            df_enhanced['indice_calor'] = (
                df_enhanced['temperatura'] * 0.7 + 
                df_enhanced['umidade'] * 0.3
            )
        
        if 'vento_velocidade' in df_enhanced.columns and 'vento_direcao' in df_enhanced.columns:
            # Componentes do vento
            df_enhanced['vento_u'] = (
                df_enhanced['vento_velocidade'] * 
                np.cos(np.radians(df_enhanced['vento_direcao']))
            )
            df_enhanced['vento_v'] = (
                df_enhanced['vento_velocidade'] * 
                np.sin(np.radians(df_enhanced['vento_direcao']))
            )
        
        # Features de médias móveis (se houver dados suficientes)
        numeric_columns = df_enhanced.select_dtypes(include=[np.number]).columns
        
        for column in ['temperatura', 'umidade', 'vento_velocidade']:
            if column in numeric_columns and len(df_enhanced) >= 24:
                # Média móvel de 24 períodos (aproximadamente 1 dia se dados horários)
                df_enhanced[f'{column}_ma24'] = (
                    df_enhanced[column].rolling(window=24, min_periods=1).mean()
                )
        
        return df_enhanced
    
    def get_feature_statistics(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Calcula estatísticas das features.
        """
        stats = {}
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            series = df[column].dropna()
            
            if len(series) > 0:
                stats[column] = {
                    'count': len(series),
                    'mean': series.mean(),
                    'std': series.std(),
                    'min': series.min(),
                    'max': series.max(),
                    'q25': series.quantile(0.25),
                    'q50': series.quantile(0.50),
                    'q75': series.quantile(0.75),
                    'missing_count': df[column].isna().sum(),
                    'missing_percentage': (df[column].isna().sum() / len(df)) * 100
                }
        
        return stats
    
    def save_transformers(self, filepath: str) -> None:
        """
        Salva os transformadores ajustados.
        """
        import joblib
        
        transformers = {
            'scalers': self.scalers,
            'imputers': self.imputers,
            'outlier_detectors': self.outlier_detectors,
            'feature_stats': self.feature_stats
        }
        
        joblib.dump(transformers, filepath)
        self.logger.info(f"Transformadores salvos em: {filepath}")
    
    def load_transformers(self, filepath: str) -> None:
        """
        Carrega transformadores salvos.
        """
        import joblib
        
        transformers = joblib.load(filepath)
        
        self.scalers = transformers.get('scalers', {})
        self.imputers = transformers.get('imputers', {})
        self.outlier_detectors = transformers.get('outlier_detectors', {})
        self.feature_stats = transformers.get('feature_stats', {})
        
        self.logger.info(f"Transformadores carregados de: {filepath}")


class FeatureEngineer:
    """
    Classe para engenharia de features específicas do domínio.
    """
    
    @staticmethod
    def create_pollution_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features específicas para poluição do ar.
        """
        df_enhanced = df.copy()
        
        # Índices de qualidade do ar
        if 'pm25' in df_enhanced.columns:
            df_enhanced['pm25_category'] = pd.cut(
                df_enhanced['pm25'],
                bins=[0, 12, 35.4, 55.4, 150.4, 250.4, float('inf')],
                labels=['Boa', 'Moderada', 'Insalubre_Sensíveis', 'Insalubre', 'Muito_Insalubre', 'Perigosa']
            )
        
        # Razões entre poluentes
        if 'pm25' in df_enhanced.columns and 'pm10' in df_enhanced.columns:
            df_enhanced['pm25_pm10_ratio'] = df_enhanced['pm25'] / (df_enhanced['pm10'] + 1e-8)
        
        return df_enhanced
    
    @staticmethod
    def create_temporal_features(df: pd.DataFrame, datetime_column: str = 'datetime') -> pd.DataFrame:
        """
        Cria features temporais avançadas.
        """
        df_enhanced = df.copy()
        
        if datetime_column not in df_enhanced.columns:
            return df_enhanced
        
        dt = pd.to_datetime(df_enhanced[datetime_column])
        
        # Features cíclicas
        df_enhanced['hour_sin'] = np.sin(2 * np.pi * dt.dt.hour / 24)
        df_enhanced['hour_cos'] = np.cos(2 * np.pi * dt.dt.hour / 24)
        df_enhanced['day_sin'] = np.sin(2 * np.pi * dt.dt.dayofyear / 365)
        df_enhanced['day_cos'] = np.cos(2 * np.pi * dt.dt.dayofyear / 365)
        
        # Períodos do dia
        df_enhanced['periodo_dia'] = pd.cut(
            dt.dt.hour,
            bins=[0, 6, 12, 18, 24],
            labels=['Madrugada', 'Manhã', 'Tarde', 'Noite'],
            include_lowest=True
        )
        
        # Estações do ano (hemisfério sul)
        month = dt.dt.month
        df_enhanced['estacao'] = pd.cut(
            month,
            bins=[0, 3, 6, 9, 12],
            labels=['Verão', 'Outono', 'Inverno', 'Primavera'],
            include_lowest=True
        )
        
        return df_enhanced
