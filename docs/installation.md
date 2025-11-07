# Guia de Instalação e Configuração

## Pré-requisitos

### Sistema Operacional
- Linux (Ubuntu 20.04+ recomendado)
- macOS 10.15+
- Windows 10+ (com WSL2 recomendado)

### Software Necessário
- Python 3.11+
- Docker e Docker Compose (opcional, mas recomendado)
- Git
- MongoDB (local ou Atlas)

## Instalação Local

### 1. Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd projeto-qualidade-ar-completo
```

### 2. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

**Configurações mínimas necessárias:**

```env
# Banco de dados (usar MongoDB Atlas ou local)
MONGODB_URL="mongodb+srv://usuario:senha@cluster.mongodb.net/qualidade_ar"

# APIs externas (opcional)
OPENAQ_API_KEY="sua_chave_aqui"

# Ambiente
ENVIRONMENT="development"
DEBUG=true
```

### 5. Treinar Modelo Inicial

```bash
# Treinar com dados sintéticos (para desenvolvimento)
python scripts/train_model.py --synthetic

# Ou treinar com dados reais (requer APIs funcionais)
python scripts/train_model.py --cities "São Paulo" "Rio de Janeiro"
```

### 6. Executar a API

```bash
# Executar servidor de desenvolvimento
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

## Instalação com Docker

### 1. Usando Docker Compose (Recomendado)

```bash
# Construir e executar todos os serviços
docker-compose up --build

# Executar em background
docker-compose up -d --build
```

**Serviços disponíveis:**
- API: http://localhost:8000
- Dashboard: http://localhost:8501
- Jupyter: http://localhost:8888
- MongoDB: localhost:27017
- Redis: localhost:6379

### 2. Usando Docker Standalone

```bash
# Construir imagem
docker build -t qualidade-ar-api .

# Executar container
docker run -p 8000:8000 \
  -e MONGODB_URL="sua_url_mongodb" \
  -e ENVIRONMENT="development" \
  qualidade-ar-api
```

## Configuração de Produção

### 1. Variáveis de Ambiente de Produção

```env
ENVIRONMENT="production"
DEBUG=false
LOG_LEVEL="WARNING"

# Banco de dados
MONGODB_URL="mongodb+srv://prod_user:senha@cluster.mongodb.net/qualidade_ar_prod"

# CORS (especificar domínios exatos)
ALLOWED_ORIGINS="https://seu-dominio.com,https://www.seu-dominio.com"

# Segurança
SECRET_KEY="chave_secreta_muito_forte_aqui"
```

### 2. Deploy no Render

1. **Conectar repositório** ao Render
2. **Configurar serviço web:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
3. **Adicionar variáveis de ambiente** no painel do Render
4. **Deploy automático** será executado

### 3. Deploy com Docker em Produção

```bash
# Usar docker-compose para produção
docker-compose --profile production up -d
```

## Verificação da Instalação

### 1. Testar API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Teste de predição
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

### 2. Executar Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio pytest-cov

# Executar testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

### 3. Verificar Logs

```bash
# Logs do Docker Compose
docker-compose logs -f api

# Logs locais
tail -f logs/app.log
```

## Solução de Problemas

### Erro de Conexão com MongoDB

```bash
# Verificar conectividade
python -c "
import pymongo
client = pymongo.MongoClient('sua_url_mongodb')
print(client.server_info())
"
```

### Erro de Importação de Módulos

```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou instalar em modo desenvolvimento
pip install -e .
```

### Erro de Permissões (Docker)

```bash
# Ajustar permissões
sudo chown -R $USER:$USER .
chmod +x scripts/*.py
```

### Modelo Não Carregado

```bash
# Verificar se modelo existe
ls -la models/production/

# Treinar novo modelo
python scripts/train_model.py --synthetic --output models/production/modelo_qualidade_ar.pkl
```

## Desenvolvimento

### Estrutura de Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install

# Executar formatação
black src/ tests/
flake8 src/ tests/

# Executar type checking
mypy src/
```

### Executar Jupyter para Análise

```bash
# Local
jupyter lab notebooks/

# Docker
docker-compose up jupyter
# Acessar: http://localhost:8888
```

### Hot Reload para Desenvolvimento

```bash
# API com reload automático
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Dashboard com reload
streamlit run src/dashboard/app.py --server.runOnSave true
```

## Monitoramento

### Métricas da Aplicação

- **Health Check**: `/api/v1/health`
- **Métricas Detalhadas**: `/api/v1/health/detailed`
- **Documentação**: `/docs` (Swagger UI)

### Logs Estruturados

```bash
# Visualizar logs em tempo real
tail -f logs/app.log | jq '.'

# Filtrar por nível
grep "ERROR" logs/app.log | jq '.'
```

### Backup do Modelo

```bash
# Backup automático
cp models/production/modelo_qualidade_ar.pkl models/backup/modelo_$(date +%Y%m%d).pkl
```

---

Para mais informações, consulte a [documentação completa](./README.md) ou abra uma issue no repositório.
