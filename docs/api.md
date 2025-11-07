# Documentação da API

## Visão Geral

A API de Predição da Qualidade do Ar fornece endpoints REST para realizar predições da qualidade do ar baseadas em dados climáticos. A API é construída com FastAPI e oferece documentação interativa automática.

## URLs Base

- **Desenvolvimento**: `http://localhost:8000`
- **Produção**: `https://seu-dominio.com`
- **Documentação Interativa**: `/docs` (Swagger UI)
- **Documentação Alternativa**: `/redoc` (ReDoc)

## Autenticação

Atualmente, a API não requer autenticação. Em versões futuras, será implementada autenticação via JWT tokens.

## Endpoints Principais

### 1. Health Check

#### `GET /api/v1/health`

Verifica o status de saúde da API.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "versao": "1.0.0",
  "modelo_carregado": true,
  "banco_conectado": true,
  "uptime": 3600.5
}
```

#### `GET /api/v1/health/detailed`

Retorna métricas detalhadas do sistema.

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "versao": "1.0.0",
  "modelo_carregado": true,
  "banco_conectado": true,
  "uptime": 3600.5,
  "system_metrics": {
    "cpu_usage_percent": 15.2,
    "memory": {
      "total_gb": 8.0,
      "available_gb": 4.5,
      "used_percent": 43.75
    },
    "disk": {
      "total_gb": 100.0,
      "free_gb": 75.2,
      "used_percent": 24.8
    }
  }
}
```

### 2. Predição Individual

#### `POST /api/v1/predict`

Realiza predição da qualidade do ar para um conjunto de dados climáticos.

**Parâmetros:**
```json
{
  "cidade": "São Paulo",
  "dados_climaticos": {
    "temperatura": 25.5,
    "umidade": 65.0,
    "vento_velocidade": 15.2,
    "vento_direcao": 180.0,
    "precipitacao": 0.0,
    "pressao_atmosferica": 1013.25
  },
  "data_predicao": "2024-01-15",
  "incluir_historico": false
}
```

**Resposta:**
```json
{
  "cidade": "São Paulo",
  "data_predicao": "2024-01-15",
  "timestamp": "2024-01-15T10:30:00Z",
  "pm25": {
    "valor": 25.5,
    "unidade": "µg/m³",
    "nivel_qualidade": "moderada",
    "confianca": 0.85
  },
  "pm10": {
    "valor": 45.2,
    "unidade": "µg/m³",
    "nivel_qualidade": "moderada",
    "confianca": 0.82
  },
  "no2": {
    "valor": 35.8,
    "unidade": "µg/m³",
    "nivel_qualidade": "boa",
    "confianca": 0.78
  },
  "qualidade_geral": "moderada",
  "indice_qualidade": 75.5,
  "modelo_versao": "1.0.0",
  "confianca_geral": 0.83
}
```

### 3. Predição em Lote

#### `POST /api/v1/predict/batch`

Realiza múltiplas predições em uma única requisição.

**Parâmetros:**
```json
{
  "cidade": "São Paulo",
  "dados_climaticos": [
    {
      "temperatura": 25.5,
      "umidade": 65.0,
      "vento_velocidade": 15.2,
      "vento_direcao": 180.0,
      "precipitacao": 0.0,
      "pressao_atmosferica": 1013.25
    },
    {
      "temperatura": 28.0,
      "umidade": 70.0,
      "vento_velocidade": 12.0,
      "vento_direcao": 200.0,
      "precipitacao": 2.5,
      "pressao_atmosferica": 1015.0
    }
  ],
  "datas_predicao": ["2024-01-15", "2024-01-16"]
}
```

**Resposta:**
```json
{
  "cidade": "São Paulo",
  "total_predicoes": 2,
  "predicoes": [
    {
      "cidade": "São Paulo",
      "data_predicao": "2024-01-15",
      "timestamp": "2024-01-15T10:30:00Z",
      "pm25": {
        "valor": 25.5,
        "unidade": "µg/m³",
        "nivel_qualidade": "moderada",
        "confianca": 0.85
      },
      "qualidade_geral": "moderada",
      "indice_qualidade": 75.5,
      "modelo_versao": "1.0.0",
      "confianca_geral": 0.83
    }
  ],
  "tempo_processamento": 0.25
}
```

### 4. Dados Históricos

#### `POST /api/v1/historical`

Recupera dados históricos de qualidade do ar.

**Parâmetros:**
```json
{
  "cidade": "São Paulo",
  "data_inicio": "2024-01-01",
  "data_fim": "2024-01-31",
  "poluentes": ["pm25", "pm10", "no2"]
}
```

**Resposta:**
```json
{
  "cidade": "São Paulo",
  "periodo": {
    "inicio": "2024-01-01",
    "fim": "2024-01-31"
  },
  "total_registros": 31,
  "dados": [
    {
      "data": "2024-01-15",
      "poluentes": {
        "pm25": 25.5,
        "pm10": 45.2,
        "no2": 35.8
      },
      "clima": {
        "temperatura": 25.5,
        "umidade": 65.0,
        "vento_velocidade": 15.2
      },
      "qualidade": "moderada"
    }
  ],
  "estatisticas": {
    "pm25_media": 23.8,
    "pm25_max": 45.2,
    "pm25_min": 12.1
  }
}
```

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 400 | Requisição inválida |
| 422 | Erro de validação |
| 500 | Erro interno do servidor |
| 503 | Serviço indisponível |

## Tratamento de Erros

### Formato de Erro Padrão

```json
{
  "error": true,
  "message": "Descrição do erro",
  "status_code": 400,
  "details": {
    "field": "temperatura",
    "issue": "Valor fora do intervalo permitido"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Erros Comuns

#### 400 - Bad Request
```json
{
  "error": true,
  "message": "Dados de entrada inválidos",
  "status_code": 400,
  "details": {
    "temperatura": "Deve estar entre -50 e 60 graus Celsius"
  }
}
```

#### 503 - Service Unavailable
```json
{
  "error": true,
  "message": "Serviço indisponível: modelo não carregado",
  "status_code": 503
}
```

## Validação de Dados

### Dados Climáticos

| Campo | Tipo | Obrigatório | Intervalo | Descrição |
|-------|------|-------------|-----------|-----------|
| temperatura | float | Sim | -50 a 60 | Temperatura em °C |
| umidade | float | Sim | 0 a 100 | Umidade relativa em % |
| vento_velocidade | float | Sim | 0 a 200 | Velocidade do vento em km/h |
| vento_direcao | float | Não | 0 a 360 | Direção do vento em graus |
| precipitacao | float | Sim | 0 a 1000 | Precipitação em mm |
| pressao_atmosferica | float | Não | 800 a 1200 | Pressão em hPa |

### Níveis de Qualidade do Ar

| Nível | Descrição | PM2.5 (µg/m³) |
|-------|-----------|----------------|
| excelente | Qualidade excelente | 0-12 |
| boa | Qualidade boa | 12-25 |
| moderada | Qualidade moderada | 25-37.5 |
| ruim | Qualidade ruim | 37.5-75 |
| muito_ruim | Qualidade muito ruim | 75-150 |
| perigosa | Qualidade perigosa | >150 |

## Rate Limiting

- **Limite padrão**: 100 requisições por hora por IP
- **Headers de resposta**:
  - `X-RateLimit-Limit`: Limite total
  - `X-RateLimit-Remaining`: Requisições restantes
  - `X-RateLimit-Reset`: Timestamp do reset

## Exemplos de Uso

### Python com requests

```python
import requests

# Predição simples
url = "http://localhost:8000/api/v1/predict"
data = {
    "dados_climaticos": {
        "temperatura": 25.5,
        "umidade": 65.0,
        "vento_velocidade": 15.2,
        "precipitacao": 0.0
    }
}

response = requests.post(url, json=data)
result = response.json()
print(f"PM2.5 predito: {result['pm25']['valor']} µg/m³")
```

### JavaScript com fetch

```javascript
const url = 'http://localhost:8000/api/v1/predict';
const data = {
  dados_climaticos: {
    temperatura: 25.5,
    umidade: 65.0,
    vento_velocidade: 15.2,
    precipitacao: 0.0
  }
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(result => {
  console.log(`PM2.5 predito: ${result.pm25.valor} µg/m³`);
});
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "dados_climaticos": {
      "temperatura": 25.5,
      "umidade": 65.0,
      "vento_velocidade": 15.2,
      "precipitacao": 0.0
    }
  }'
```

## Versionamento

A API segue versionamento semântico (SemVer):
- **v1.x.x**: Versão atual estável
- **Mudanças breaking**: Nova versão major (v2.x.x)
- **Novas funcionalidades**: Nova versão minor (v1.x.x)
- **Bug fixes**: Nova versão patch (v1.x.x)

## Suporte e Contato

- **Documentação**: `/docs` na API
- **Issues**: Repositório GitHub
- **Email**: suporte@exemplo.com

---

*Documentação atualizada em: Janeiro 2024*
