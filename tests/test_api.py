import pytest
from fastapi.testclient import TestClient
from datetime import date
import json

from src.api.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

class TestHealthEndpoints:
    """Testes para endpoints de health check."""

    def test_health_check(self, client):
        """Testa o endpoint básico de health check."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "versao" in data
        assert "modelo_carregado" in data
        assert "banco_conectado" in data
        assert "uptime" in data

    def test_detailed_health_check(self, client):
        """Testa o endpoint detalhado de health check."""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "system_metrics" in data

        # Verificar métricas do sistema
        metrics = data["system_metrics"]
        assert "cpu_usage_percent" in metrics
        assert "memory" in metrics
        assert "disk" in metrics

    def test_readiness_check(self, client):
        """Testa o endpoint de readiness."""
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "components" in data

    def test_liveness_check(self, client):
        """Testa o endpoint de liveness."""
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "alive"


class TestPredictionEndpoints:
    """Testes para endpoints de predição."""

    def test_predict_valid_data(self, client):
        """Testa predição com dados válidos."""
        payload = {
            "dados_climaticos": {
                "temperatura": 25.5,
                "umidade": 65.0,
                "vento_velocidade": 15.2,
                "vento_direcao": 180.0,
                "precipitacao": 0.0,
                "pressao_atmosferica": 1013.25
            }
        }

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "cidade" in data
        assert "data_predicao" in data
        assert "timestamp" in data
        assert "pm25" in data
        assert "qualidade_geral" in data
        assert "indice_qualidade" in data
        assert "modelo_versao" in data
        assert "confianca_geral" in data

        # Verificar estrutura do PM2.5
        pm25 = data["pm25"]
        assert "valor" in pm25
        assert "unidade" in pm25
        assert "nivel_qualidade" in pm25
        assert "confianca" in pm25

    def test_predict_with_city(self, client):
        """Testa predição especificando cidade."""
        payload = {
            "cidade": "Rio de Janeiro",
            "dados_climaticos": {
                "temperatura": 28.0,
                "umidade": 75.0,
                "vento_velocidade": 20.0,
                "precipitacao": 5.0
            }
        }

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["cidade"] == "Rio de Janeiro"

    def test_predict_with_date(self, client):
        """Testa predição especificando data."""
        payload = {
            "dados_climaticos": {
                "temperatura": 22.0,
                "umidade": 60.0,
                "vento_velocidade": 10.0,
                "precipitacao": 0.0
            },
            "data_predicao": "2024-12-25"
        }

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["data_predicao"] == "2024-12-25"

    def test_predict_invalid_temperature(self, client):
        """Testa predição com temperatura inválida."""
        payload = {
            "dados_climaticos": {
                "temperatura": 100.0,  # Muito alta
                "umidade": 65.0,
                "vento_velocidade": 15.2,
                "precipitacao": 0.0
            }
        }

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422  # Validation error

    def test_predict_invalid_humidity(self, client):
        """Testa predição com umidade inválida."""
        payload = {
            "dados_climaticos": {
                "temperatura": 25.0,
                "umidade": 150.0,  # Muito alta
                "vento_velocidade": 15.2,
                "precipitacao": 0.0
            }
        }

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422

    def test_predict_missing_required_field(self, client):
        """Testa predição com campo obrigatório faltando."""
        payload = {
            "dados_climaticos": {
                "temperatura": 25.0,
                # umidade faltando
                "vento_velocidade": 15.2,
                "precipitacao": 0.0
            }
        }

        response = client.post("/api/v1/predict", json=payload)
        assert response.status_code == 422


class TestBatchPrediction:
    """Testes para predições em lote."""

    def test_batch_predict_valid_data(self, client):
        """Testa predição em lote com dados válidos."""
        payload = {
            "dados_climaticos": [
                {
                    "temperatura": 25.5,
                    "umidade": 65.0,
                    "vento_velocidade": 15.2,
                    "precipitacao": 0.0
                },
                {
                    "temperatura": 28.0,
                    "umidade": 70.0,
                    "vento_velocidade": 12.0,
                    "precipitacao": 2.5
                }
            ]
        }

        response = client.post("/api/v1/predict/batch", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "total_predicoes" in data
        assert "predicoes" in data
        assert "tempo_processamento" in data

        assert data["total_predicoes"] == 2
        assert len(data["predicoes"]) == 2

    def test_batch_predict_with_dates(self, client):
        """Testa predição em lote com datas específicas."""
        payload = {
            "dados_climaticos": [
                {
                    "temperatura": 25.5,
                    "umidade": 65.0,
                    "vento_velocidade": 15.2,
                    "precipitacao": 0.0
                }
            ],
            "datas_predicao": ["2024-01-15"]
        }

        response = client.post("/api/v1/predict/batch", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["predicoes"][0]["data_predicao"] == "2024-01-15"

    def test_batch_predict_mismatched_dates(self, client):
        """Testa predição em lote com número de datas incompatível."""
        payload = {
            "dados_climaticos": [
                {
                    "temperatura": 25.5,
                    "umidade": 65.0,
                    "vento_velocidade": 15.2,
                    "precipitacao": 0.0
                }
            ],
            "datas_predicao": ["2024-01-15", "2024-01-16"]  # Mais datas que dados
        }

        response = client.post("/api/v1/predict/batch", json=payload)
        assert response.status_code == 422


class TestHistoricalData:
    """Testes para dados históricos."""

    def test_historical_data_valid_request(self, client):
        """Testa requisição válida de dados históricos."""
        payload = {
            "cidade": "São Paulo",
            "data_inicio": "2024-01-01",
            "data_fim": "2024-01-31"
        }

        response = client.post("/api/v1/historical", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "cidade" in data
        assert "periodo" in data
        assert "total_registros" in data
        assert "dados" in data

        assert data["cidade"] == "São Paulo"
        assert data["periodo"]["inicio"] == "2024-01-01"
        assert data["periodo"]["fim"] == "2024-01-31"

    def test_historical_data_with_pollutants(self, client):
        """Testa dados históricos com poluentes específicos."""
        payload = {
            "cidade": "São Paulo",
            "data_inicio": "2024-01-01",
            "data_fim": "2024-01-31",
            "poluentes": ["pm25", "pm10"]
        }

        response = client.post("/api/v1/historical", json=payload)
        assert response.status_code == 200

    def test_historical_data_invalid_date_range(self, client):
        """Testa dados históricos com intervalo de datas inválido."""
        payload = {
            "cidade": "São Paulo",
            "data_inicio": "2024-01-31",
            "data_fim": "2024-01-01"  # Data fim antes da data início
        }

        response = client.post("/api/v1/historical", json=payload)
        assert response.status_code == 422

    def test_historical_data_invalid_pollutants(self, client):
        """Testa dados históricos com poluentes inválidos."""
        payload = {
            "cidade": "São Paulo",
            "data_inicio": "2024-01-01",
            "data_fim": "2024-01-31",
            "poluentes": ["pm25", "invalid_pollutant"]
        }

        response = client.post("/api/v1/historical", json=payload)
        assert response.status_code == 422


class TestRootEndpoint:
    """Testes para endpoint raiz."""

    def test_root_endpoint(self, client):
        """Testa o endpoint raiz da API."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data


class TestErrorHandling:
    """Testes para tratamento de erros."""

    def test_404_endpoint(self, client):
        """Testa endpoint inexistente."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Testa requisição com JSON inválido."""
        response = client.post(
            "/api/v1/predict",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_content_type(self, client):
        """Testa requisição sem Content-Type."""
        response = client.post("/api/v1/predict", data='{"test": "data"}')
        assert response.status_code == 422


@pytest.fixture
def sample_climate_data():
    """Fixture com dados climáticos de exemplo."""
    return {
        "temperatura": 25.5,
        "umidade": 65.0,
        "vento_velocidade": 15.2,
        "vento_direcao": 180.0,
        "precipitacao": 0.0,
        "pressao_atmosferica": 1013.25
    }


@pytest.fixture
def sample_prediction_request(sample_climate_data):
    """Fixture com requisição de predição de exemplo."""
    return {
        "cidade": "São Paulo",
        "dados_climaticos": sample_climate_data,
        "data_predicao": date.today().isoformat(),
        "incluir_historico": False
    }


class TestFixtures:
    """Testes usando fixtures."""

    def test_with_sample_data(self, client, sample_prediction_request):
        """Testa predição usando fixture."""
        response = client.post("/api/v1/predict", json=sample_prediction_request)
        assert response.status_code == 200

        data = response.json()
        assert data["cidade"] == sample_prediction_request["cidade"]

