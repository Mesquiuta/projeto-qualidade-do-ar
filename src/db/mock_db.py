"""
Módulo para simular um banco de dados (Mock DB) para o projeto Qualidade do Ar.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

# Dados mock de estações
MOCK_STATIONS = [
    {"id": 1, "name": "Estação Centro", "latitude": -23.5505, "longitude": -46.6333, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 2, "name": "Estação Leste", "latitude": -23.5489, "longitude": -46.5810, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 3, "name": "Estação Oeste", "latitude": -23.5500, "longitude": -46.6800, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 4, "name": "Estação Norte", "latitude": -23.4500, "longitude": -46.6000, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 5, "name": "Estação Sul", "latitude": -23.6500, "longitude": -46.6500, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 6, "name": "Estação Parque", "latitude": -23.5800, "longitude": -46.6000, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 7, "name": "Estação Industrial", "latitude": -23.5000, "longitude": -46.7000, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 8, "name": "Estação Rural", "latitude": -23.7000, "longitude": -46.8000, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 9, "name": "Estação Praia", "latitude": -23.9600, "longitude": -46.3900, "city": "Santos", "state": "SP", "country": "BR"},
    {"id": 10, "name": "Estação Montanha", "latitude": -22.9000, "longitude": -47.0600, "city": "Campinas", "state": "SP", "country": "BR"},
    {"id": 11, "name": "Estação Histórica", "latitude": -23.5500, "longitude": -46.6300, "city": "São Paulo", "state": "SP", "country": "BR"},
    {"id": 12, "name": "Estação Nova", "latitude": -23.5200, "longitude": -46.6100, "city": "São Paulo", "state": "SP", "country": "BR"},
]

# Dados mock de medições históricas (simplificado)
def generate_mock_measurement(station_id: int, date_time: datetime) -> Dict[str, Any]:
    """Gera uma medição mock para uma estação em um dado momento."""
    return {
        "station_id": station_id,
        "timestamp": date_time.isoformat(),
        "pm25": round(random.uniform(5.0, 50.0), 2),
        "pm10": round(random.uniform(10.0, 100.0), 2),
        "o3": round(random.uniform(0.01, 0.1), 3),
        "no2": round(random.uniform(0.01, 0.1), 3),
        "so2": round(random.uniform(0.001, 0.05), 3),
        "co": round(random.uniform(0.1, 5.0), 2),
        "temperature": round(random.uniform(15.0, 35.0), 1),
        "humidity": round(random.uniform(30.0, 90.0), 1),
        "wind_speed": round(random.uniform(0.5, 10.0), 1),
    }

def generate_historical_data(station_id: int, days: int = 7) -> List[Dict[str, Any]]:
    end = datetime.now()
    start = end - timedelta(days=days)
    series: List[Dict[str, Any]] = []
    for i in range(days):
        when = start + timedelta(days=i)
        series.append({
            "station_id": station_id,
            "date": when.date().isoformat(),
            "pm25": random.uniform(5, 60),
            "pm10": random.uniform(10, 120),
            "o3": random.uniform(10, 200),
            "no2": random.uniform(5, 150),
            "so2": random.uniform(2, 50),
            "co": random.uniform(0.1, 2.0),
            "aqi": random.randint(0, 200),
        })
    return series

    
    MOCK_HISTORICAL_DATA = {}
    for station in MOCK_STATIONS:
        MOCK_HISTORICAL_DATA[station["id"]] = generate_historical_data(station["id"], days=30) # Aumentar para 30 dias de dados
    
    class MockDB:
        """Simula a interface de um banco de dados."""
        
        async def get_stations(self) -> List[Dict[str, Any]]:
            """Retorna a lista de estações."""
            return MOCK_STATIONS
        
        async def get_historical_data(
            self,
            station_id: int,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
        ) -> List[Dict[str, Any]]:
            """Retorna dados históricos para uma estação."""
            data = MOCK_HISTORICAL_DATA.get(station_id, [])
            
            # Simular filtragem por data (simplificado)
            if start_date:
                data = [d for d in data if datetime.fromisoformat(d["timestamp"]) >= start_date]
            if end_date:
                data = [d for d in data if datetime.fromisoformat(d["timestamp"]) <= end_date]
                
            return data
            
        async def analyze_data_with_llm(self, data: List[Dict[str, Any]]) -> str:
            """Simula a análise de dados por um LLM."""
            if not data:
                return "Não há dados para análise."
                
            # Simulação de análise simples
            pm25_avg = sum(d["pm25"] for d in data) / len(data)
            pm10_avg = sum(d["pm10"] for d in data) / len(data)
            
            analysis = f"Análise simulada por LLM:\n"
            analysis += f"- Média de PM2.5 nas últimas 24h: {pm25_avg:.2f} µg/m³\n"
            analysis += f"- Média de PM10 nas últimas 24h: {pm10_avg:.2f} µg/m³\n"
            
            if pm25_avg > 30 or pm10_avg > 50:
                analysis += "- **Alerta:** A qualidade do ar está em níveis moderados a ruins. Recomenda-se evitar atividades ao ar livre."
            else:
                analysis += "- **Conclusão:** A qualidade do ar está boa. Não há restrições."
                
            return analysis
    
    mock_db = MockDB()

# Instância global do MockDB
mock_db = MockDB()

# Criar o diretório src/db se não existir
import os
os.makedirs("/home/ubuntu/projeto-qualidade-ar-backend/projeto-qualidade-ar-2.0/projeto-qualidade-ar/back/src/db", exist_ok=True)
