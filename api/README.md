# 🚀 PDF RAG API - Documentação

API REST para consulta de documentos PDF usando RAG (Retrieval-Augmented Generation). Ideal para integração com agentes de IA e sistemas externos.

## 📋 Índice

- [Instalação](#instalação)
- [Iniciando a API](#iniciando-a-api)
- [Endpoints](#endpoints)
- [Exemplos de Uso](#exemplos-de-uso)
- [Cliente Python](#cliente-python)
- [Integração com Agentes de IA](#integração-com-agentes-de-ia)
- [Autenticação](#autenticação)
- [Rate Limiting](#rate-limiting)

## 🔧 Instalação

### 1. Instalar dependências adicionais

```bash
# Com uv (recomendado)
uv pip install fastapi uvicorn pydantic requests

# Ou com pip
pip install fastapi uvicorn[standard] pydantic requests
```

### 2. Estrutura de diretórios

```bash
# Crie o diretório da API
mkdir api examples

# Crie __init__.py
touch api/__init__.py examples/__init__.py
```

### 3. Copiar arquivos

Copie os seguintes arquivos para a estrutura:

- `api/main.py` - Aplicação FastAPI principal
- `api/models.py` - Modelos Pydantic
- `api/dependencies.py` - Injeção de dependências
- `api/chat_manager.py` - Gerenciador de sessões
- `examples/api_client.py` - Cliente exemplo

## 🚀 Iniciando a API

### Opção 1: Comando direto

```bash
python api/main.py
```

### Opção 2: Uvicorn (recomendado para produção)

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Opção 3: Com configurações customizadas

```bash
uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

**Saída esperada:**
```
🚀 Iniciando PDF RAG API...
✓ Configuração carregada
✓ VectorStore inicializado
✓ RAG Engine inicializado
✓ Chat Manager inicializado
✓ 1250 chunks indexados
✅ API pronta para receber requisições

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Acessar documentação interativa

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📡 Endpoints

### 1. Health Check

**GET** `/health`

Verifica status da API e componentes.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "vectorstore": "ok",
    "rag_engine": "ok",
    "chat_manager": "ok"
  },
  "total_documents": 1250
}
```

### 2. Estatísticas

**GET** `/stats`

Retorna estatísticas do banco vetorial.

```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "total_chunks": 1250,
  "unique_sources": 5,
  "sources": [
    "manual.pdf",
    "guide.pdf",
    "handbook.pdf"
  ],
  "collection_name": "pdf_documents"
}
```

### 3. Query (Principal)

**POST** `/query`

Faz uma pergunta e retorna resposta baseada nos documentos.

**Request:**
```json
{
  "question": "O que é machine learning?",
  "k": 6,
  "include_sources": true
}
```

**Response:**
```json
{
  "question": "O que é machine learning?",
  "answer": "Machine learning é um subcampo da inteligência artificial que permite que sistemas aprendam e melhorem a partir da experiência sem serem explicitamente programados...",
  "sources": [
    {
      "source": "ai_handbook.pdf",
      "page": 12,
      "title": "AI Handbook",
      "excerpt": "Machine learning permite que sistemas..."
    }
  ],
  "num_sources": 4
}
```

**Exemplo cURL:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "O que é machine learning?",
    "k": 6,
    "include_sources": true
  }'
```

### 4. Search

**POST** `/search`

Busca chunks similares sem gerar resposta.

**Request:**
```json
{
  "query": "neural networks",
  "k": 5,
  "filter": {
    "source": "ml_guide.pdf"
  }
}
```

**Response:**
```json
{
  "query": "neural networks",
  "chunks": [
    {
      "content": "Redes neurais são modelos computacionais inspirados no cérebro humano...",
      "metadata": {
        "source": "ml_guide.pdf",
        "page": 8,
        "title": "ML Guide",
        "chunk_id": 5
      }
    }
  ],
  "total_results": 5
}
```

### 5. Chat

**POST** `/chat`

Chat conversacional com histórico de sessão.

**Request:**
```json
{
  "session_id": "user-123",
  "message": "O que são transformers?",
  "k": 6
}
```

**Response:**
```json
{
  "session_id": "user-123",
  "message": "O que são transformers?",
  "response": "Transformers são uma arquitetura de rede neural introduzida em 2017...",
  "sources": [...],
  "num_sources": 4
}
```

### 6. Chat History

**GET** `/chat/{session_id}/history`

Retorna histórico de uma sessão.

```bash
curl http://localhost:8000/chat/user-123/history
```

### 7. Clear Chat Session

**DELETE** `/chat/{session_id}`

Limpa o histórico de uma sessão.

```bash
curl -X DELETE http://localhost:8000/chat/user-123
```

## 💡 Exemplos de Uso

### Python com requests

```python
import requests

# Query simples
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "Qual é o tema principal?",
        "k": 6,
        "include_sources": True
    }
)

result = response.json()
print(result['answer'])
```

### JavaScript/TypeScript

```javascript
// Query com fetch
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'O que é deep learning?',
    k: 6,
    include_sources: true
  })
});

const data = await response.json();
console.log(data.answer);
```

### cURL

```bash
# Query básica
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Explique redes neurais", "k": 6}'

# Busca com filtro
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deep learning",
    "k": 5,
    "filter": {"source": "manual.pdf"}
  }'

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-456",
    "message": "Olá, pode me ajudar?",
    "k": 6
  }'
```

## 🤖 Cliente Python

Usando o cliente fornecido:

```python
from examples.api_client import PDFRAGClient

# Inicializa cliente
client = PDFRAGClient(base_url="http://localhost:8000")

# Verifica saúde
health = client.health_check()
print(health)

# Faz pergunta
result = client.query(
    question="O que é inteligência artificial?",
    k=6,
    include_sources=True
)
print(result['answer'])

# Busca chunks
chunks = client.search(
    query="machine learning",
    k=5
)

# Chat conversacional
response = client.chat(
    session_id="meu-usuario",
    message="Explique redes neurais"
)
print(response['response'])
```

### Executar exemplos

```bash
# Certifique-se que a API está rodando
python api/main.py

# Em outro terminal
python examples/api_client.py
```

## 🤖 Integração com Agentes de IA

### Exemplo: Agente LangChain

```python
from langchain.tools import Tool
from examples.api_client import PDFRAGClient

# Cria cliente
client = PDFRAGClient()

# Define ferramenta para o agente
pdf_search_tool = Tool(
    name="PDF Knowledge Base",
    func=lambda q: client.query(q, k=6)['answer'],
    description="Busca informações na base de conhecimento de documentos PDF. Use esta ferramenta quando precisar de informações específicas dos documentos."
)

# Usar no agente
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools=[pdf_search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Executar
response = agent.run("Pesquise sobre machine learning nos documentos")
```

### Exemplo: Workflow de Atendimento ao Cliente

```python
class CustomerServiceAgent:
    def __init__(self):
        self.pdf_client = PDFRAGClient()
    
    def handle_customer_query(self, customer_id: str, question: str):
        """Responde pergunta do cliente usando documentos"""
        
        # 1. Buscar contexto relevante
        search_result = self.pdf_client.search(
            query=question,
            k=5
        )
        
        # 2. Gerar resposta contextualizada
        response = self.pdf_client.chat(
            session_id=customer_id,
            message=question,
            k=6
        )
        
        # 3. Formatar resposta para o cliente
        return {
            "answer": response['response'],
            "confidence": "high" if response['num_sources'] > 3 else "medium",
            "sources": [s['source'] for s in response['sources'][:2]]
        }

# Uso
agent = CustomerServiceAgent()
result = agent.handle_customer_query(
    customer_id="customer-789",
    question="Como faço para configurar o produto?"
)
```

### Exemplo: RAG com OpenAI Function Calling

```python
import openai
from examples.api_client import PDFRAGClient

client = PDFRAGClient()

# Define função para OpenAI
functions = [
    {
        "name": "search_documents",
        "description": "Busca informações em documentos PDF da base de conhecimento",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Pergunta ou tópico a buscar"
                }
            },
            "required": ["query"]
        }
    }
]

# Chamada com function calling
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Me explique sobre deep learning"}
    ],
    functions=functions,
    function_call="auto"
)

# Se chamou a função, executa
if response.choices[0].message.get("function_call"):
    function_args = json.loads(
        response.choices[0].message.function_call.arguments
    )
    
    # Busca nos documentos
    docs_result = client.query(
        question=function_args["query"],
        k=6
    )
    
    # Envia resultado de volta
    final_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "Me explique sobre deep learning"},
            response.choices[0].message,
            {
                "role": "function",
                "name": "search_documents",
                "content": json.dumps(docs_result)
            }
        ]
    )
    
    print(final_response.choices[0].message.content)
```

## 🔐 Autenticação (Recomendado para Produção)

Para adicionar autenticação básica:

```python
# Em api/main.py, adicione:

from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verifica token de autenticação"""
    token = credentials.credentials
    
    # Valide seu token aqui
    if token != "seu-token-secreto":
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )
    return token

# Adicione como dependência nos endpoints
@app.post("/query")
async def query_documents(
    request: QueryRequest,
    rag: RAGEngine = Depends(get_rag_engine),
    token: str = Depends(verify_token)  # ← Adiciona autenticação
):
    ...
```

## ⚡ Rate Limiting (Recomendado para Produção)

```bash
# Instalar slowapi
uv pip install slowapi

# Adicionar em api/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/query")
@limiter.limit("10/minute")  # 10 requests por minuto
async def query_documents(request: Request, ...):
    ...
```

## 🐳 Deploy com Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependências
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt

# Copia código
COPY . .

# Expõe porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

```bash
# Build e run
docker-compose up -d

# Logs
docker-compose logs -f api
```

## 📊 Monitoramento

### Prometheus + Grafana

```python
# Instalar
uv pip install prometheus-fastapi-instrumentator

# Em api/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## 🧪 Testes da API

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query():
    response = client.post(
        "/query",
        json={
            "question": "Teste",
            "k": 3,
            "include_sources": True
        }
    )
    assert response.status_code == 200
    assert "answer" in response.json()

# Executar
pytest tests/test_api.py -v
```

## 📞 Suporte

Para problemas ou dúvidas:

- **Issues:** [GitHub Issues](https://github.com/seu-repo/issues)
- **Documentação:** http://localhost:8000/docs
- **Email:** suporte@seu-dominio.com

---

**Versão:** 1.0.0  
**Última Atualização:** Dezembro 2025