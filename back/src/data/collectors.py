"""
Coletores de dados para APIs externas.
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import logging
import asyncio
import aiohttp
from pathlib import Path
import zipfile
import io

from src.config import settings

logger = logging.getLogger(__name__)


class OpenAQCollector:
    """
    Coletor de dados da API OpenAQ.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = settings.OPENAQ_API_URL
        self.api_key = api_key or settings.OPENAQ_API_KEY
        self.session = None
    
    async def __aenter__(self):
        """Context manager para sessão HTTP."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fechar sessão HTTP."""
        if self.session:
            await self.session.close()
    
    async def get_locations(self, country: str = "BR", limit: int = 100) -> List[Dict]:
        """
        Obtém lista de localizações disponíveis.
        
        Args:
            country: Código do país (BR para Brasil)
            limit: Número máximo de resultados
            
        Returns:
            Lista de localizações
        """
        try:
            params = {
                'country': country,
                'limit': limit,
                'order_by': 'lastUpdated',
                'sort': 'desc'
            }
            
            if self.api_key:
                params['api-key'] = self.api_key
            
            url = f"{self.base_url}/locations"
            
            if self.session:
                async with self.session.get(url, params=params) as response:
                    data = await response.json()
            else:
                response = requests.get(url, params=params)
                data = response.json()
            
            return data.get('results', [])
            
        except Exception as e:
            logger.error(f"Erro ao obter localizações OpenAQ: {e}")
            return []
    
    async def get_measurements(
        self,
        location_id: Optional[int] = None,
        city: Optional[str] = None,
        parameter: str = "pm25",
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Obtém medições de qualidade do ar.
        
        Args:
            location_id: ID da localização
            city: Nome da cidade
            parameter: Parâmetro a coletar (pm25, pm10, no2, o3, etc.)
            date_from: Data de início
            date_to: Data de fim
            limit: Número máximo de resultados
            
        Returns:
            DataFrame com as medições
        """
        try:
            params = {
                'parameter': parameter,
                'limit': limit,
                'order_by': 'datetime',
                'sort': 'desc'
            }
            
            if location_id:
                params['location_id'] = location_id
            elif city:
                params['city'] = city
            
            if date_from:
                params['date_from'] = date_from.isoformat()
            
            if date_to:
                params['date_to'] = date_to.isoformat()
            
            if self.api_key:
                params['api-key'] = self.api_key
            
            url = f"{self.base_url}/measurements"
            
            if self.session:
                async with self.session.get(url, params=params) as response:
                    data = await response.json()
            else:
                response = requests.get(url, params=params)
                data = response.json()
            
            measurements = data.get('results', [])
            
            if not measurements:
                return pd.DataFrame()
            
            # Converter para DataFrame
            df = pd.DataFrame(measurements)
            
            # Processar colunas de data
            if 'date' in df.columns:
                df['datetime'] = pd.to_datetime(df['date']['utc'])
                df = df.drop('date', axis=1)
            
            # Processar coordenadas se disponíveis
            if 'coordinates' in df.columns:
                coords = pd.json_normalize(df['coordinates'])
                df = pd.concat([df.drop('coordinates', axis=1), coords], axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter medições OpenAQ: {e}")
            return pd.DataFrame()
    
    async def get_latest_measurements(
        self,
        city: str = "São Paulo",
        parameters: List[str] = None
    ) -> Dict[str, float]:
        """
        Obtém as medições mais recentes para uma cidade.
        
        Args:
            city: Nome da cidade
            parameters: Lista de parâmetros desejados
            
        Returns:
            Dicionário com os valores mais recentes
        """
        if parameters is None:
            parameters = ['pm25', 'pm10', 'no2', 'o3', 'co', 'so2']
        
        latest_data = {}
        
        for parameter in parameters:
            try:
                df = await self.get_measurements(
                    city=city,
                    parameter=parameter,
                    limit=1
                )
                
                if not df.empty:
                    latest_data[parameter] = df.iloc[0]['value']
                    
            except Exception as e:
                logger.warning(f"Erro ao obter {parameter} para {city}: {e}")
                continue
        
        return latest_data


class INMETCollector:
    """
    Coletor de dados históricos do INMET.
    """
    
    def __init__(self):
        self.base_url = settings.INMET_BASE_URL
        self.stations_cache = {}
    
    def get_stations(self) -> pd.DataFrame:
        """
        Obtém lista de estações meteorológicas.
        
        Returns:
            DataFrame com informações das estações
        """
        try:
            # URL da API de estações do INMET
            url = "https://apitempo.inmet.gov.br/estacoes/T"
            
            response = requests.get(url)
            response.raise_for_status()
            
            stations_data = response.json()
            df = pd.DataFrame(stations_data)
            
            # Cache das estações
            self.stations_cache = df.set_index('CD_ESTACAO').to_dict('index')
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter estações INMET: {e}")
            return pd.DataFrame()
    
    def find_nearest_station(self, city: str, state: str = "SP") -> Optional[str]:
        """
        Encontra a estação mais próxima de uma cidade.
        
        Args:
            city: Nome da cidade
            state: Estado (sigla)
            
        Returns:
            Código da estação mais próxima
        """
        try:
            if not self.stations_cache:
                self.get_stations()
            
            # Buscar estações do estado
            state_stations = [
                (code, info) for code, info in self.stations_cache.items()
                if info.get('SG_ESTADO') == state
            ]
            
            if not state_stations:
                # Fallback: primeira estação disponível
                return list(self.stations_cache.keys())[0] if self.stations_cache else None
            
            # Por simplicidade, retornar a primeira estação do estado
            # Em uma implementação real, calcularíamos a distância geográfica
            return state_stations[0][0]
            
        except Exception as e:
            logger.error(f"Erro ao encontrar estação para {city}: {e}")
            return None
    
    def get_historical_data(
        self,
        station_code: str,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Obtém dados históricos de uma estação.
        
        Args:
            station_code: Código da estação
            start_date: Data de início
            end_date: Data de fim
            
        Returns:
            DataFrame com dados meteorológicos
        """
        try:
            # API do INMET para dados históricos
            url = f"https://apitempo.inmet.gov.br/estacao/{start_date}/{end_date}/{station_code}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            
            # Processar colunas de data
            if 'DT_MEDICAO' in df.columns:
                df['datetime'] = pd.to_datetime(df['DT_MEDICAO'])
                df = df.set_index('datetime')
            
            # Renomear colunas para padrão do projeto
            column_mapping = {
                'TEM_INS': 'temperatura',
                'UMD_INS': 'umidade',
                'VEN_VEL': 'vento_velocidade',
                'VEN_DIR': 'vento_direcao',
                'PRE_INS': 'pressao_atmosferica',
                'CHUVA': 'precipitacao'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Converter para numérico
            numeric_columns = ['temperatura', 'umidade', 'vento_velocidade', 
                             'vento_direcao', 'pressao_atmosferica', 'precipitacao']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos INMET: {e}")
            return pd.DataFrame()
    
    def download_historical_files(
        self,
        year: int,
        station_code: Optional[str] = None,
        save_path: Optional[Path] = None
    ) -> List[Path]:
        """
        Baixa arquivos históricos anuais do INMET.
        
        Args:
            year: Ano dos dados
            station_code: Código da estação (opcional)
            save_path: Diretório para salvar os arquivos
            
        Returns:
            Lista de caminhos dos arquivos baixados
        """
        try:
            if save_path is None:
                save_path = Path("data/raw/inmet")
            
            save_path.mkdir(parents=True, exist_ok=True)
            
            downloaded_files = []
            
            # URL para download de dados anuais
            if station_code:
                url = f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}/{station_code}.zip"
                filename = f"{station_code}_{year}.zip"
            else:
                url = f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip"
                filename = f"inmet_{year}.zip"
            
            response = requests.get(url)
            
            if response.status_code == 200:
                file_path = save_path / filename
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # Extrair ZIP se necessário
                if zipfile.is_zipfile(file_path):
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        extract_path = save_path / f"extracted_{year}"
                        extract_path.mkdir(exist_ok=True)
                        zip_ref.extractall(extract_path)
                        
                        # Listar arquivos extraídos
                        for extracted_file in extract_path.glob("*.csv"):
                            downloaded_files.append(extracted_file)
                
                downloaded_files.append(file_path)
                logger.info(f"Arquivo baixado: {file_path}")
            
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Erro ao baixar dados INMET: {e}")
            return []


class DataCollectionManager:
    """
    Gerenciador principal para coleta de dados.
    """
    
    def __init__(self):
        self.openaq = OpenAQCollector()
        self.inmet = INMETCollector()
    
    async def collect_city_data(
        self,
        city: str = "São Paulo",
        state: str = "SP",
        days_back: int = 30
    ) -> Dict[str, pd.DataFrame]:
        """
        Coleta dados completos para uma cidade.
        
        Args:
            city: Nome da cidade
            state: Estado
            days_back: Número de dias para coletar dados históricos
            
        Returns:
            Dicionário com DataFrames de poluição e clima
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        results = {
            'pollution': pd.DataFrame(),
            'weather': pd.DataFrame()
        }
        
        try:
            # Coletar dados de poluição
            async with self.openaq as collector:
                pollution_data = await collector.get_measurements(
                    city=city,
                    parameter="pm25",
                    date_from=start_date,
                    date_to=end_date,
                    limit=days_back * 24  # Aproximadamente dados horários
                )
                results['pollution'] = pollution_data
            
            # Coletar dados meteorológicos
            station_code = self.inmet.find_nearest_station(city, state)
            if station_code:
                weather_data = self.inmet.get_historical_data(
                    station_code, start_date, end_date
                )
                results['weather'] = weather_data
            
            logger.info(f"Dados coletados para {city}: "
                       f"Poluição: {len(results['pollution'])} registros, "
                       f"Clima: {len(results['weather'])} registros")
            
        except Exception as e:
            logger.error(f"Erro na coleta de dados para {city}: {e}")
        
        return results
    
    async def collect_multiple_cities(
        self,
        cities: List[Dict[str, str]],
        days_back: int = 30
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Coleta dados para múltiplas cidades.
        
        Args:
            cities: Lista de dicionários com 'name' e 'state'
            days_back: Número de dias para coletar
            
        Returns:
            Dicionário aninhado com dados por cidade
        """
        results = {}
        
        tasks = []
        for city_info in cities:
            task = self.collect_city_data(
                city_info['name'],
                city_info.get('state', 'SP'),
                days_back
            )
            tasks.append((city_info['name'], task))
        
        # Executar coletas em paralelo
        for city_name, task in tasks:
            try:
                city_data = await task
                results[city_name] = city_data
            except Exception as e:
                logger.error(f"Erro na coleta para {city_name}: {e}")
                results[city_name] = {
                    'pollution': pd.DataFrame(),
                    'weather': pd.DataFrame()
                }
        
        return results
