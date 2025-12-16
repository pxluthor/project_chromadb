
# 📄 PDF RAG Analyzer

Sistema avançado de análise de documentos PDF usando RAG (Retrieval-Augmented Generation) com ChromaDB, LangChain e OpenAI.

## 🎯 Características

- ✅ **Extração robusta de texto** com PyMuPDF
- ✅ **Busca semântica** usando embeddings OpenAI
- ✅ **Banco vetorial persistente** com ChromaDB
- ✅ **Suporte a múltiplos PDFs** - processe pastas inteiras
- ✅ **Respostas contextualizadas** com GPT-4o/GPT-3.5
- ✅ **Citação de fontes** - rastreie de qual documento veio cada resposta
- ✅ **Pipeline RAG completo** - pronto para produção

## 🏗️ Arquitetura

```
PDF → Extração de Texto → Chunking → Embeddings → ChromaDB
                                                      ↓
                                           Busca Semântica
                                                      ↓
                                              LLM (GPT-4o)
                                                      ↓
                                          Resposta + Fontes
```

## 📋 Pré-requisitos

- Python 3.10+
- Chave da API OpenAI
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes rápido)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd rag_teste
```

### 2. Instale o uv (se ainda não tiver)

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Crie o ambiente virtual e instale as dependências

```bash
# Cria ambiente virtual
uv venv

# Ativa o ambiente
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instala as dependências
uv pip install langchain-core langchain-text-splitters langchain-openai langchain-chroma pymupdf chromadb openai
```
# 🚀 Guia de Instalação - PDF RAG System

## 📁 Estrutura do Projeto

Primeiro, crie a estrutura de diretórios:

```bash
pdf_rag_system/
├── src/
│   ├── __init__.py              # Criar arquivo vazio
│   ├── config.py                # ✅ Criado
│   ├── pdf_extractor.py         # ✅ Criado
│   ├── vectorstore.py           # ✅ Criado
│   ├── rag_engine.py            # ✅ Criado
│   └── chat_interface.py        # ✅ Criado
├── scripts/
│   ├── __init__.py              # Criar arquivo vazio
│   ├── ingest_pdfs.py           # ✅ Criado
│   └── test_system.py           # ✅ Criado
├── data/
│   ├── pdfs/                    # Criar diretório
│   └── chroma_db/               # Criado automaticamente
├── chat.py                      # ✅ Criado
├── .env                         # Criar baseado em .env.example
├── .env.example                 # ✅ Criado
├── .gitignore                   # ✅ Criado
├── requirements.txt             # ✅ Criado
└── README.md                    # ✅ Criado anteriormente
```

## 📦 Passo a Passo da Instalação

### 1. Criar a estrutura

```bash
# Crie o diretório principal
mkdir pdf_rag_system
cd pdf_rag_system

# Crie os subdiretórios
mkdir -p src scripts data/pdfs

# Crie arquivos __init__.py vazios
touch src/__init__.py
touch scripts/__init__.py
```

### 2. Copiar os arquivos

Copie todos os arquivos gerados para seus respectivos diretórios:

- `src/config.py`
- `src/pdf_extractor.py`
- `src/vectorstore.py`
- `src/rag_engine.py`
- `src/chat_interface.py`
- `scripts/ingest_pdfs.py`
- `scripts/test_system.py`
- `chat.py`
- `.env.example`
- `.gitignore`
- `requirements.txt`

### 3. Instalar dependências com uv

```bash
# Instale o uv se ainda não tiver
# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Crie o ambiente virtual
uv venv

# Ative o ambiente virtual
# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate

# Instale as dependências
uv pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
# Copie o exemplo
cp .env.example .env

# Edite o arquivo .env
# Windows:
notepad .env

# Linux/macOS:
nano .env
# ou
vim .env
```

**Conteúdo do .env:**
```bash
OPENAI_API_KEY=sk-sua-chave-real-aqui
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
TEMPERATURE=0.0
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEFAULT_K=6
COLLECTION_NAME=pdf_documents
MAX_HISTORY=10
```

### 5. Adicionar PDFs

```bash
# Copie seus PDFs para a pasta data/pdfs/
cp /caminho/seus/pdfs/*.pdf data/pdfs/
```

### 6. Testar o sistema

```bash
# Execute os testes
python scripts/test_system.py
```

**Resultado esperado:**
```
🚀 TESTES DO SISTEMA PDF RAG
================================================================================

🧪 Teste 1: Configuração
================================================================================
✓ Configuração carregada com sucesso
  LLM Model: gpt-4o
  ...

📊 RESUMO DOS TESTES
================================================================================
  ✅ PASSOU - Configuração
  ✅ PASSOU - Conexão OpenAI
  ⚠️  AVISO - Extração de PDF (nenhum PDF encontrado)
  ...
```

### 7. Indexar documentos

```bash
# Indexar um arquivo único
python scripts/ingest_pdfs.py data/pdfs/documento.pdf

# Indexar uma pasta inteira
python scripts/ingest_pdfs.py data/pdfs/

# Indexar recursivamente (incluindo subpastas)
python scripts/ingest_pdfs.py data/pdfs/ --recursive

# Limpar banco e reindexar
python scripts/ingest_pdfs.py data/pdfs/ --clear
```

**Saída esperada:**
```
🚀 INDEXAÇÃO DE DOCUMENTOS PDF
================================================================================

📋 Configurações:
  Collection: pdf_documents
  Chunk size: 1000
  Chunk overlap: 200

📄 Extraindo texto de: data/pdfs
✓ Extraídos 3 documento(s)

✅ INDEXAÇÃO CONCLUÍDA
================================================================================
  Documentos processados: 3
  Total de páginas: 45
  Total de chunks: 127
```

### 8. Iniciar o chat

```bash
python chat.py
```

**Interface do chat:**
```
💬 CHAT CONVERSACIONAL - PDF RAG SYSTEM
================================================================================
Converse com seus documentos de forma natural!

Comandos disponíveis:
  /help     - Mostra ajuda
  /stats    - Estatísticas
  /history  - Histórico
  /clear    - Limpa histórico
  /export   - Exporta conversa
  /quit     - Sai

✓ Sistema carregado com sucesso!
  Modelo: gpt-4o
  Documentos indexados: 3
  Total de chunks: 127

Digite sua pergunta ou /help para ajuda

👤 Você: 
```

## 🎮 Comandos Úteis

### Gerenciar documentos

```bash
# Ver estatísticas dos documentos
python chat.py
# Depois digite: /stats

# Reindexar tudo do zero
python scripts/ingest_pdfs.py data/pdfs/ --clear

# Adicionar mais documentos (sem reindexar existentes)
python scripts/ingest_pdfs.py data/pdfs/ novos_pdfs/
```

### Testar componentes individuais

```bash
# Testar só a configuração
python -c "from src.config import load_config; c = load_config(); print(c)"

# Testar extração de PDF
python -c "from src.pdf_extractor import PDFExtractor; e = PDFExtractor(); doc = e.extract_from_file('data/pdfs/teste.pdf'); print(f'Páginas: {doc.total_pages}')"

# Testar conexão OpenAI
python -c "from openai import OpenAI; import os; client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print(client.models.list().data[0])"
```

### Desenvolvimento

```bash
# Formatar código com Black
uv pip install black
black src/ scripts/ chat.py

# Verificar código com flake8
uv pip install flake8
flake8 src/ scripts/ chat.py --max-line-length=100

# Executar testes
python scripts/test_system.py
```

## 🐛 Solução de Problemas Comuns

### Erro: "OPENAI_API_KEY não encontrada"

**Solução:**
```bash
# Verifique se o arquivo .env existe
ls -la .env

# Verifique o conteúdo
cat .env

# Configure manualmente
export OPENAI_API_KEY="sk-sua-chave"
```

### Erro: "No module named 'src'"

**Solução:**
```bash
# Certifique-se de estar no diretório raiz do projeto
pwd

# Verifique se __init__.py existe
ls src/__init__.py

# Execute os scripts do diretório raiz
python scripts/test_system.py  # ✓ Correto
cd scripts && python test_system.py  # ✗ Errado
```

### Erro: "Nenhum documento indexado"

**Solução:**
```bash
# 1. Verifique se há PDFs
ls data/pdfs/

# 2. Indexe os documentos
python scripts/ingest_pdfs.py data/pdfs/

# 3. Verifique o banco
python -c "from src.config import load_config; from src.vectorstore import VectorStore; vs = VectorStore(load_config()); print(vs.get_collection_stats())"
```

### Erro: "ChromaDB não persiste dados"

**Solução:**
```bash
# Verifique permissões
ls -ld data/chroma_db/

# Recrie o diretório
rm -rf data/chroma_db/
mkdir data/chroma_db/
python scripts/ingest_pdfs.py data/pdfs/ --clear
```

### PDFs não extraem texto corretamente

**Solução:**
```bash
# Verifique se o PDF tem texto (não é imagem)
python -c "import fitz; doc = fitz.open('data/pdfs/seu.pdf'); print(doc[0].get_text())"

# Para PDFs escaneados, use OCR antes
# Instale tesseract e pdf2image
```

## 📊 Monitoramento e Logs

### Ver estatísticas do sistema

```bash
# Dentro do chat
/stats

# Via script
python -c "
from src.config import load_config
from src.vectorstore import VectorStore
vs = VectorStore(load_config())
import json
print(json.dumps(vs.get_collection_stats(), indent=2))
"
```

### Exportar conversas

```bash
# Dentro do chat
/export

# Isso cria: chat_export_YYYYMMDD_HHMMSS.json
```

## 🔒 Segurança

- ✅ Nunca commite `.env` no Git (já está no `.gitignore`)
- ✅ Use variáveis de ambiente em produção
- ✅ Rotacione suas API keys regularmente
- ✅ Limite acesso aos PDFs sensíveis
- ✅ Monitore uso da API OpenAI

## 🚀 Próximos Passos

Após a instalação:

1. ✅ Teste o sistema: `python scripts/test_system.py`
2. ✅ Indexe seus PDFs: `python scripts/ingest_pdfs.py data/pdfs/`
3. ✅ Inicie o chat: `python chat.py`
4. ✅ Experimente diferentes perguntas
5. ✅ Use `/stats` para ver métricas
6. ✅ Exporte conversas úteis com `/export`

## 📚 Documentação Adicional

- [README.md](README.md) - Documentação principal
- [Exemplos de uso](README.md#exemplos-de-uso)
- [Configurações avançadas](README.md#configurações-avançadas)
- [API Reference](README.md#api-reference)

---

✅ Sistema instalado com sucesso! Comece a conversar com seus documentos.