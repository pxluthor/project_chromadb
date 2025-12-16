# 📁 Estrutura Profissional do Projeto

```
pdf_rag_system/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configurações e variáveis de ambiente
│   ├── pdf_extractor.py       # Extração de texto de PDFs
│   ├── vectorstore.py         # Gerenciamento do ChromaDB
│   ├── rag_engine.py          # Engine RAG principal
│   └── chat_interface.py      # Interface de chat conversacional
│
├── scripts/
│   ├── __init__.py
│   ├── ingest_pdfs.py         # Script para indexar PDFs
│   └── test_system.py         # Testes do sistema
│
├── tests/
│   ├── __init__.py
│   ├── test_extractor.py
│   ├── test_vectorstore.py
│   └── test_rag.py
│
├── data/
│   ├── pdfs/                  # PDFs para indexar
│   └── chroma_db/             # Banco vetorial (gerado)
│
├── chat.py                    # CLI do chat conversacional
├── .env.example               # Exemplo de variáveis de ambiente
├── .gitignore
├── requirements.txt
├── pyproject.toml             # Configuração do projeto
└── README.md
```

## 📋 Arquivos a Criar

Vou gerar cada arquivo separadamente:

1. ✅ `src/config.py` - Configurações centralizadas
2. ✅ `src/pdf_extractor.py` - Extração de PDFs
3. ✅ `src/vectorstore.py` - Gerenciamento ChromaDB
4. ✅ `src/rag_engine.py` - Engine RAG
5. ✅ `src/chat_interface.py` - Chat conversacional
6. ✅ `scripts/ingest_pdfs.py` - Script de indexação
7. ✅ `scripts/test_system.py` - Testes
8. ✅ `chat.py` - Interface CLI
9. ✅ `.env.example` - Exemplo de configuração
10. ✅ `requirements.txt` - Dependências

### Executar Suite Completa

```bash
python scripts/test_system.py
```