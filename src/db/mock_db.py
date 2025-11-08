from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import logging

__all__ = ["generate_historical_data", "MockDB", "mock_db"]

log = logging.getLogger(__name__)


def generate_historical_data(station_id: int, days: int = 7) -> List[Dict[str, Any]]:
    """Gera uma série histórica fake para testes."""
    if days < 1:
        days = 1

    end = datetime.now()
    start = end - timedelta(days=days)
    series: List[Dict[str, Any]] = []
    for i in range(days):
        when = start + timedelta(days=i)
        series.append(
            {
                "station_id": station_id,
                "date": when.date().isoformat(),
                "pm25": round(random.uniform(5, 60), 2),
                "pm10": round(random.uniform(10, 120), 2),
                "o3": round(random.uniform(10, 200), 2),
                "no2": round(random.uniform(5, 150), 2),
                "so2": round(random.uniform(2, 50), 2),
                "co": round(random.uniform(0.1, 2.0), 3),
                "aqi": random.randint(0, 200),
            }
        )
    return series


class MockDB:
    """Banco fake em memória para rotas e testes locais."""

    def __init__(self) -> None:
        self._predictions: List[Dict[str, Any]] = []
        self._stations: List[Dict[str, Any]] = [
            {
                "id": 1,
                "name": "Estação Centro",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "city": "São Paulo",
                "state": "SP",
                "country": "BR",
            },
            {
                "id": 2,
                "name": "Estação Leste",
                "latitude": -23.5489,
                "longitude": -46.5810,
                "city": "São Paulo",
                "state": "SP",
                "country": "BR",
            },
        ]

    # --- Estações ---
    async def get_stations(self) -> List[Dict[str, Any]]:
        return list(self._stations)

    async def get_station_by_id(self, station_id: int) -> Optional[Dict[str, Any]]:
        for s in self._stations:
            if s["id"] == station_id:
                return s
        return None

    # --- Séries históricas ---
    async def historical_data(self, station_id: int, days: int = 7) -> List[Dict[str, Any]]:
        return generate_historical_data(station_id, days)

    # --- Predições ---
    async def save_prediction(self, payload: Dict[str, Any]) -> None:
        data = dict(payload)
        data["created_at"] = datetime.utcnow().isoformat()
        self._predictions.append(data)
        log.debug("Prediction salva: %s", data)

    async def list_predictions(self) -> List[Dict[str, Any]]:
        return list(self._predictions)


# Instância global (módulo):
mock_db = MockDB()
