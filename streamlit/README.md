Com certeza. Baseado no código do `streamlit/admin_frontend.py` e nas funcionalidades que implementamos recentemente (Gestão de PDFs, Associações de Mídia e Busca), aqui está um `README.md` profissional para a pasta `streamlit/`.

Você pode salvar este conteúdo como `streamlit/README.md`.

---

#🖥️ Admin Frontend - RAG MultimídiaInterface administrativa construída com [Streamlit](https://streamlit.io/) para gerenciar o sistema RAG, ingestão de PDFs e enriquecimento de conteúdo com multimídia.

##🎯 FuncionalidadesEste painel oferece uma interface visual para interagir com a API do sistema:

* **📁 Gerenciar Arquivos (Novo):**
* **Upload:** Envie novos PDFs para indexação no ChromaDB.
* **Atualização:** Substitua PDFs existentes (mantendo o mesmo nome) com reindexação automática.
* **Exclusão:** Remova PDFs do banco vetorial e do disco.


* **🎬 Adicionar Multimídia:**
* Associe vídeos (YouTube, Google Drive, Local), imagens e GIFs a páginas ou seções específicas dos PDFs.
* Visualize o PDF e a mídia lado a lado.


* **🔍 Explorar ChromaDB:**
* Realize buscas semânticas para testar o que o RAG está recuperando.
* Inspecione os metadados e o conteúdo dos chunks indexados.


* **📋 Listar Associações:**
* Visualize e gerencie todas as mídias já cadastradas no sistema.



##🛠️ Pré-requisitosCertifique-se de que o backend (API) esteja rodando, pois o frontend precisa se comunicar com ele.

1. **API Rodando:**
```bash
# Em um terminal separado, na raiz do projeto:
uvicorn api.main:app --host 0.0.0.0 --port 8005 --reload

```


2. **Dependências do Frontend:**
As dependências necessárias são `streamlit`, `requests` e `pandas`.
Se estiver usando `uv`:
```bash
uv pip install streamlit requests pandas

```


Ou via pip padrão:
```bash
pip install streamlit requests pandas

```



##🚀 Como RodarA partir da **raiz do projeto**, execute o comando:

```bash
streamlit run streamlit/admin_frontend.py

```

O painel abrirá automaticamente no seu navegador padrão (geralmente em `http://localhost:8501`).

##⚙️ Configuração###URL da APIPor padrão, o frontend tenta conectar na API em `http://localhost:8005`.

Se você precisar alterar a porta ou o host da API, edite a variável `API_URL` no início do arquivo `streamlit/admin_frontend.py`:

```python
# URL da API
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8005" 

```

###Mídia LocalPara que a seleção de arquivos locais funcione na aba "Adicionar Mídia", certifique-se de que seus arquivos de vídeo/imagem estejam nas pastas corretas do projeto:

* `data/media/videos/`
* `data/media/images/`

---

##📸 Visão Geral das Abas1. **Adicionar Mídia:** Formulário principal para enriquecer o RAG. Selecione o PDF, a página e preencha os dados da mídia.
2. **Explorar ChromaDB:** Debugger para ver se seus documentos foram "picotados" (chunking) corretamente.
3. **Associações Existentes:** Tabela geral de tudo que foi cadastrado.
4. **Gerenciar Arquivos:** Painel de controle (CRUD) dos documentos PDF.