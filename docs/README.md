# 📄 PDF RAG System

> Sistema profissional de análise de documentos PDF usando RAG (Retrieval-Augmented Generation) com ChromaDB, LangChain e OpenAI.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Características

- 🤖 **Chat Conversacional Inteligente** - Converse naturalmente com seus documentos
- 📚 **Processamento de Múltiplos PDFs** - Indexe pastas inteiras de documentos
- 🔍 **Busca Semântica Avançada** - Encontra informações relevantes automaticamente
- 💾 **Banco Vetorial Persistente** - ChromaDB com armazenamento local
- 🎨 **Interface CLI Profissional** - Chat interativo com comandos úteis
- 📊 **Rastreamento de Fontes** - Cita documentos e páginas nas respostas
- 🧪 **Suite de Testes Completa** - Validação automatizada do sistema
- ⚙️ **Altamente Configurável** - Personalize via variáveis de ambiente

## 📋 Índice

- [Instalação Rápida](#-instalação-rápida)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Uso Básico](#-uso-básico)
- [Arquitetura](#-arquitetura)
- [Comandos e Scripts](#-comandos-e-scripts)
- [Configuração](#-configuração)
- [Exemplos Avançados](#-exemplos-avançados)
- [Testes](#-testes)
- [Troubleshooting](#-troubleshooting)
- [Custos Estimados](#-custos-estimados)
- [API Reference](#-api-reference)

## 🚀 Instalação Rápida

### Pré-requisitos

- Python 3.10 ou superior
- Chave da API OpenAI
- [uv](https://github.com/astral-sh/uv) (recomendado)

### Instalação em 5 minutos

```bash
# 1. Clone e entre no diretório
git clone <seu-repo>
cd pdf_rag_system

# 2. Crie a estrutura
mkdir -p data/pdfs
touch src/__init__.py scripts/__init__.py

# 3. Instale dependências com uv
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

uv pip install -r requirements.txt

# 4. Configure a API key
cp .env.example .env
echo "OPENAI_API_KEY=sua-chave-aqui" >> .env

# 5. Adicione seus PDFs
cp /caminho/seus/pdfs/*.pdf data/pdfs/

# 6. Indexe os documentos
python scripts/ingest_pdfs.py data/pdfs/

# 7. Inicie o chat!
python chat.py
```

> 💡 **Guia detalhado:** Veja [SETUP.md](SETUP.md) para instruções completas

## 📁 Estrutura do Projeto

```
pdf_rag_system/
├── src/                          # Código fonte modular
│   ├── __init__.py
│   ├── config.py                # Configurações centralizadas
│   ├── pdf_extractor.py         # Extração de texto de PDFs
│   ├── vectorstore.py           # Gerenciamento ChromaDB
│   ├── rag_engine.py            # Engine RAG
│   └── chat_interface.py        # Interface de chat
│
├── scripts/                      # Scripts utilitários
│   ├── __init__.py
│   ├── ingest_pdfs.py           # Indexação de PDFs
│   └── test_system.py           # Testes automatizados
│
├── data/
│   ├── pdfs/                    # Seus documentos PDF
│   └── chroma_db/               # Banco vetorial (auto-criado)
│
├── chat.py                       # Interface CLI do chat
├── .env                          # Configurações (não commitado)
├── .env.example                  # Template de configuração
├── .gitignore                    
├── requirements.txt              
├── README.md                     # Este arquivo
└── SETUP.md                      # Guia de instalação detalhado
```

## 💬 Uso Básico

### 1. Indexar Documentos

```bash
# Indexar um único PDF
python scripts/ingest_pdfs.py data/pdfs/documento.pdf

# Indexar uma pasta inteira
python scripts/ingest_pdfs.py data/pdfs/

# Indexar recursivamente (subpastas)
python scripts/ingest_pdfs.py data/pdfs/ --recursive

# Limpar banco e reindexar
python scripts/ingest_pdfs.py data/pdfs/ --clear

# Usar collection customizada
python scripts/ingest_pdfs.py data/pdfs/ --collection meus_docs
```

**Saída:**
```
🚀 INDEXAÇÃO DE DOCUMENTOS PDF
================================================================================
✓ Extraídos 5 documento(s)
✓ Indexação concluída
  Documentos processados: 5
  Total de páginas: 234
  Total de chunks: 567
```

### 2. Iniciar o Chat

```bash
python chat.py
```

**Exemplo de interação:**

```
💬 CHAT CONVERSACIONAL - PDF RAG SYSTEM
================================================================================

👤 Você: Qual é o tema principal dos documentos?

🤖 Assistente: Com base nos documentos indexados, os temas principais são:
1. Inteligência Artificial e Machine Learning
2. Processamento de Linguagem Natural
3. Sistemas de Recomendação

📚 Fontes consultadas (4 chunks):
  [1] ai_handbook.pdf - Página 12
  [2] ml_guide.pdf - Página 5
  [3] nlp_intro.pdf - Página 8

👤 Você: Me explique mais sobre o tema 2

🤖 Assistente: O Processamento de Linguagem Natural (NLP) é...
```

### 3. Comandos do Chat

| Comando | Descrição |
|---------|-----------|
| `/help` | Mostra todos os comandos disponíveis |
| `/stats` | Estatísticas dos documentos indexados |
| `/history` | Exibe o histórico completo da conversa |
| `/clear` | Limpa o histórico (nova conversa) |
| `/export` | Exporta a conversa para JSON |
| `/quit` | Sai do chat |

### 4. Executar Testes

```bash
python scripts/test_system.py
```

**Saída:**
```
🚀 TESTES DO SISTEMA PDF RAG
================================================================================

🧪 Teste 1: Configuração
✓ Configuração carregada com sucesso

🧪 Teste 2: Conexão OpenAI
✓ Conexão com OpenAI estabelecida

...

📊 RESUMO DOS TESTES
================================================================================
  ✅ PASSOU - Configuração
  ✅ PASSOU - Conexão OpenAI
  ✅ PASSOU - Extração de PDF
  ✅ PASSOU - VectorStore
  ✅ PASSOU - RAG Engine
  ✅ PASSOU - Chat Interface

Resultado: 6/6 testes passaram
🎉 Todos os testes passaram! Sistema funcionando corretamente.
```

## 🏗️ Arquitetura

### Pipeline RAG

```
┌─────────────────────────────────────────────────────────────┐
│                     PIPELINE RAG                            │
└─────────────────────────────────────────────────────────────┘

1. INGESTÃO
   PDF → PyMuPDF → Texto Limpo

2. CHUNKING
   Texto → RecursiveCharacterTextSplitter → Chunks (1000 chars)

3. EMBEDDINGS
   Chunks → OpenAI Embeddings → Vetores (1536 dims)

4. ARMAZENAMENTO
   Vetores → ChromaDB → Persistência Local

5. RETRIEVAL
   Pergunta → Busca Semântica → Top K Chunks

6. GERAÇÃO
   Chunks + Pergunta + Histórico → GPT-4o → Resposta
```

### Componentes Principais

#### **1. PDFExtractor** (`src/pdf_extractor.py`)
- Extração robusta de texto com PyMuPDF
- Limpeza e normalização de texto
- Metadados completos (autor, título, páginas)
- Suporte a múltiplos arquivos e diretórios

#### **2. VectorStore** (`src/vectorstore.py`)
- Gerenciamento do ChromaDB
- Chunking inteligente com overlap
- Embeddings OpenAI
- Busca por similaridade com filtros

#### **3. RAGEngine** (`src/rag_engine.py`)
- Geração de respostas contextualizadas
- Prompt engineering otimizado
- Citação automática de fontes
- Suporte a chat conversacional

#### **4. ChatInterface** (`src/chat_interface.py`)
- Histórico de conversa
- Comandos úteis
- Exportação de sessões
- Estatísticas em tempo real

## 🛠️ Comandos e Scripts

### Scripts de Ingestão

```bash
# Opções do ingest_pdfs.py
python scripts/ingest_pdfs.py --help

# Exemplos práticos
python scripts/ingest_pdfs.py data/pdfs/                    # Básico
python scripts/ingest_pdfs.py data/pdfs/ --recursive        # Recursivo
python scripts/ingest_pdfs.py data/pdfs/ --clear            # Limpar e reindexar
python scripts/ingest_pdfs.py data/pdfs/ --collection docs  # Collection custom
```

### Scripts de Teste

```bash
# Executar todos os testes
python scripts/test_system.py

# Testes individuais via Python
python -c "from scripts.test_system import test_configuration; test_configuration()"
python -c "from scripts.test_system import test_openai_connection; test_openai_connection()"
```

### Chat Interativo

```bash
# Iniciar chat padrão
python chat.py

# Dentro do chat
/help      # Ajuda completa
/stats     # Ver estatísticas
/history   # Ver conversa completa
/clear     # Nova conversa
/export    # Salvar conversa
/quit      # Sair
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# Obrigatório
OPENAI_API_KEY=sk-sua-chave-aqui

# Modelos (opcional)
LLM_MODEL=gpt-4o                        # ou gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small  # ou text-embedding-3-large
TEMPERATURE=0.0                         # 0.0 = determinístico, 1.0 = criativo

# Chunking (opcional)
CHUNK_SIZE=1000        # Tamanho dos chunks
CHUNK_OVERLAP=200      # Sobreposição entre chunks

# Retrieval (opcional)
DEFAULT_K=6            # Número de chunks a recuperar

# ChromaDB (opcional)
COLLECTION_NAME=pdf_documents

# Chat (opcional)
MAX_HISTORY=10         # Máximo de mensagens no histórico
```

### Configuração Programática

```python
from src.config import Config

# Carregar do ambiente
config = Config.from_env()

# Ou criar manualmente
config = Config(
    openai_api_key="sua-chave",
    llm_model="gpt-4o",
    chunk_size=1500,
    default_k=8
)
```

## 📚 Exemplos Avançados

### Uso Programático

```python
from src.config import load_config
from src.pdf_extractor import PDFExtractor
from src.vectorstore import VectorStore
from src.rag_engine import RAGEngine

# Inicialização
config = load_config()
extractor = PDFExtractor()
vectorstore = VectorStore(config)
rag_engine = RAGEngine(config, vectorstore)

# Extrair e indexar
docs = extractor.extract_from_directory("data/pdfs/")
stats = vectorstore.add_documents(docs)
print(f"Indexados {stats['total_chunks']} chunks")

# Fazer perguntas
result = rag_engine.query(
    "Qual é o tema principal?",
    k=5,
    include_sources=True
)

print(result['answer'])
for source in result['sources']:
    print(f"  - {source['source']}, p. {source['page']}")
```

### Chat com Histórico

```python
from src.chat_interface import ChatInterface

chat = ChatInterface(config, vectorstore, rag_engine)

# Primeira pergunta
response1 = chat.send_message("O que é RAG?")
print(response1['answer'])

# Pergunta de follow-up (usa contexto)
response2 = chat.send_message("Como isso funciona?")
print(response2['answer'])

# Exportar conversa
chat.export_conversation("minha_conversa.json")
```

### Busca Semântica Direta

```python
# Buscar chunks similares sem gerar resposta
chunks = vectorstore.search(
    "inteligência artificial",
    k=10
)

for chunk in chunks:
    print(f"Arquivo: {chunk.metadata['source']}")
    print(f"Página: {chunk.metadata['page']}")
    print(f"Texto: {chunk.page_content[:200]}...\n")
```

### Filtrar por Documento Específico

```python
# Buscar apenas em um documento específico
chunks = vectorstore.search(
    "machine learning",
    k=5,
    filter_dict={"source": "ai_handbook.pdf"}
)
```

### Busca com Scores de Similaridade

```python
results = vectorstore.search_with_scores("deep learning", k=3)

for doc, score in results:
    print(f"Score: {score:.4f}")
    print(f"Fonte: {doc.metadata['source']}")
    print(f"Texto: {doc.page_content[:150]}...\n")
```

## 🧪 Testes

### Executar Suite Completa

```bash
python scripts/test_system.py
```

### Testes Disponíveis

1. **test_configuration** - Validação de configurações
2. **test_openai_connection** - Conectividade com OpenAI
3. **test_pdf_extraction** - Extração de PDFs
4. **test_vectorstore** - Funcionamento do ChromaDB
5. **test_rag_engine** - Engine RAG completo
6. **test_chat_interface** - Interface de chat

### Teste Manual Rápido

```bash
# Testar configuração
python -c "from src.config import load_config; print(load_config())"

# Testar extração
python -c "from src.pdf_extractor import PDFExtractor; e=PDFExtractor(); print(e.extract_from_file('data/pdfs/teste.pdf').total_pages)"

# Testar OpenAI
python -c "from openai import OpenAI; import os; c=OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('OK')"
```

## 🐛 Troubleshooting

### Erro: "OPENAI_API_KEY não encontrada"

```bash
# Verifique se .env existe e está correto
cat .env

# Configure manualmente
export OPENAI_API_KEY="sk-sua-chave"

# Ou adicione ao .env
echo "OPENAI_API_KEY=sk-sua-chave" >> .env
```

### Erro: "No module named 'src'"

```bash
# Certifique-se de estar no diretório raiz
pwd

# Verifique se __init__.py existe
ls src/__init__.py scripts/__init__.py

# Execute sempre do diretório raiz
cd /caminho/para/pdf_rag_system
python chat.py  # ✓ Correto
```

### Erro: "Nenhum documento indexado"

```bash
# 1. Verifique se há PDFs
ls data/pdfs/

# 2. Indexe os documentos
python scripts/ingest_pdfs.py data/pdfs/

# 3. Verifique o banco
python -c "from src.vectorstore import VectorStore; from src.config import load_config; print(VectorStore(load_config()).get_collection_stats())"
```

### PDFs não extraem texto

```bash
# Verifique se o PDF tem texto (não é só imagem)
python -c "import fitz; doc=fitz.open('data/pdfs/seu.pdf'); print(doc[0].get_text()[:200])"

# Para PDFs escaneados, use OCR antes de processar
```

### ChromaDB não persiste dados

```bash
# Verifique permissões
ls -ld data/chroma_db/

# Recrie o banco
rm -rf data/chroma_db/
python scripts/ingest_pdfs.py data/pdfs/ --clear
```

### Respostas de baixa qualidade

```python
# Ajuste o número de chunks recuperados
# Em .env:
DEFAULT_K=10  # Aumente para mais contexto

# Ou na query:
result = rag_engine.query("sua pergunta", k=10)
```

## 💰 Custos Estimados

### Embeddings (text-embedding-3-small)
- **Preço:** $0.02 por 1M tokens
- **Estimativa:** ~1000 páginas = ~$0.10

### GPT-4o
- **Input:** $2.50 por 1M tokens
- **Output:** $10.00 por 1M tokens
- **Pergunta típica:** ~2000 tokens input = ~$0.005

### Exemplo: Projeto com 100 PDFs

```
📊 Custos Estimados (100 PDFs, ~10,000 páginas)

Indexação (uma vez):
  Embeddings: ~$1.00

Uso mensal (1000 perguntas):
  GPT-4o: ~$5-10

Total mensal: ~$6-11
```

### Dicas para Economizar

1. Use `gpt-3.5-turbo` ao invés de `gpt-4o` (10x mais barato)
2. Ajuste `DEFAULT_K` para recuperar menos chunks
3. Use `text-embedding-3-small` ao invés de `large`
4. Cache perguntas frequentes

## 📖 API Reference

### Config

```python
from src.config import Config, load_config

# Carregar configuração
config = load_config()

# Atributos disponíveis
config.openai_api_key
config.llm_model
config.embedding_model
config.chunk_size
config.chunk_overlap
config.default_k
config.pdfs_dir
config.chroma_dir
config.collection_name
```

### PDFExtractor

```python
from src.pdf_extractor import PDFExtractor

extractor = PDFExtractor()

# Extrair um arquivo
doc = extractor.extract_from_file("documento.pdf")
print(doc.total_pages)
print(doc.metadata)

# Extrair diretório
docs = extractor.extract_from_directory("data/pdfs/", recursive=True)
```

### VectorStore

```python
from src.vectorstore import VectorStore

vectorstore = VectorStore(config)

# Adicionar documentos
stats = vectorstore.add_documents(pdf_documents)

# Buscar
results = vectorstore.search("query", k=5)
results_with_scores = vectorstore.search_with_scores("query", k=5)

# Estatísticas
stats = vectorstore.get_collection_stats()

# Limpar
vectorstore.clear_all_data()
```

### RAGEngine

```python
from src.rag_engine import RAGEngine

rag = RAGEngine(config, vectorstore)

# Query simples
result = rag.query("pergunta", k=6, include_sources=True)

# Query com histórico (chat)
result = rag.chat_query(
    question="pergunta",
    chat_history=[{"role": "user", "content": "oi"}],
    k=6
)
```

### ChatInterface

```python
from src.chat_interface import ChatInterface

chat = ChatInterface(config, vectorstore, rag_engine)

# Enviar mensagem
response = chat.send_message("sua pergunta")

# Histórico
history = chat.get_history()

# Estatísticas da sessão
session_info = chat.get_session_info()

# Limpar histórico
chat.clear_history()

# Exportar
chat.export_conversation("conversa.json")
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Guidelines

- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação
- Use `black` para formatação
- Use `flake8` para linting

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🙏 Agradecimentos

- [Anthropic](https://anthropic.com) - Claude AI
- [OpenAI](https://openai.com) - GPT-4 e Embeddings
- [LangChain](https://langchain.com) - Framework RAG
- [ChromaDB](https://trychroma.com) - Banco vetorial
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Extração de PDFs

## 📞 Contato

**Autor:** Seu Nome

- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Perfil](https://linkedin.com/in/seu-perfil)
- Email: seu.email@exemplo.com

## 🔗 Links Úteis

- [Documentação Completa](https://docs.seu-site.com)
- [SETUP.md](SETUP.md) - Guia de Instalação Detalhado
- [Changelog](CHANGELOG.md) - Histórico de Versões
- [Issues](https://github.com/seu-usuario/pdf-rag-system/issues) - Reportar Bugs

---

⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!

**Versão:** 1.0.0  
**Última Atualização:** Dezembro 2024