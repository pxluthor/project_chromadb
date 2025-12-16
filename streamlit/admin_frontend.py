import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Admin - RAG Multimídia",
    page_icon="🎬",
    layout="wide"
)

# URL da API
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8005"

API_URL = st.session_state.api_url

# ============================================================================
# FUNÇÕES AUXILIARES (API CALLS)
# ============================================================================
def check_api_status():
    """Verifica se a API está online"""
    try:
        response = requests.get(f"{API_URL}/health")
        return response.status_code == 200
    except:
        return False

def get_stats():
    """Busca estatísticas e lista de arquivos PDF disponíveis"""
    try:
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Erro ao buscar stats: {e}")
        return {}

def list_associations():
    """Lista todas as associações de mídia cadastradas"""
    try:
        response = requests.get(f"{API_URL}/multimedia/associations")
        if response.status_code == 200:
            return response.json().get("associations", [])
        return []
    except Exception as e:
        st.error(f"Erro ao listar associações: {e}")
        return []

def create_association(payload):
    """Envia a nova associação para a API"""
    try:
        response = requests.post(f"{API_URL}/multimedia/associations", json=payload)
        if response.status_code == 201:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def search_documents(query):
    """Busca genérica no ChromaDB"""
    try:
        payload = {"query": query, "k": 5}
        response = requests.post(f"{API_URL}/search", json=payload)
        if response.status_code == 200:
            return response.json().get("chunks", [])
        return []
    except Exception as e:
        st.error(f"Erro na busca: {e}")
        return []

def get_local_files(category):
    """Busca lista de arquivos locais na API (videos ou images)"""
    try:
        # category deve ser 'videos' ou 'images'
        response = requests.get(f"{API_URL}/multimedia/files/{category}")
        if response.status_code == 200:
            return response.json().get("files", [])
        return []
    except Exception as e:
        st.error(f"Erro ao listar arquivos locais: {e}")
        return []

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

# --- Sidebar ---
with st.sidebar:
    st.title("🔧 Configurações")
    status = check_api_status()
    if status:
        st.success(f"API Online: {API_URL}")
    else:
        st.error(f"API Offline: {API_URL}")
        st.warning("Certifique-se de rodar: `uvicorn api.main:app --reload`")
    
    st.divider()
    st.info("Use este painel para enriquecer seus PDFs com vídeos, imagens e GIFs.")
    st.markdown("""
    **Diretórios de Mídia Local:**
    - `data/media/videos`
    - `data/media/images`
    """)

# --- Título ---
st.title("🎬 Gerenciador de Multimídia RAG")

# Abas
tab_create, tab_explore, tab_list = st.tabs([
    "➕ Adicionar Mídia", 
    "🔍 Explorar ChromaDB", 
    "📋 Associações Existentes"
])

# ============================================================================
# TAB 1: ADICIONAR MÍDIA
# ============================================================================
with tab_create:
    stats = get_stats()
    available_docs = stats.get("sources", [])

    if not available_docs:
        st.warning("Nenhum documento encontrado no ChromaDB. Faça a ingestão primeiro.")
    else:
        col_form, col_preview = st.columns([1, 1])

        # --- Coluna da Esquerda: Formulário ---
        with col_form:
            st.subheader("1. Contexto do Documento")
            
            selected_doc = st.selectbox("Selecione o PDF", available_docs)
            
            c1, c2 = st.columns(2)
            with c1:
                page_num = st.number_input("Número da Página", min_value=1, value=1, step=1)
            with c2:
                section_name = st.text_input("Nome da Seção (Opcional)", help="Ex: Introdução, CGNAT, etc.")
            
            # --- FEATURE: Espiar texto do Chroma ---
            if st.button("📖 Ver texto indexado desta página"):
                with st.spinner("Buscando no ChromaDB..."):
                    try:
                        # Busca filtrada por metadados
                        payload = {
                            "query": ".", 
                            "k": 5, 
                            "filter": {"source": selected_doc, "page": int(page_num)}
                        }
                        res = requests.post(f"{API_URL}/search", json=payload)
                        if res.status_code == 200:
                            chunks = res.json().get("chunks", [])
                            if chunks:
                                st.success(f"Encontrados {len(chunks)} trechos:")
                                for chunk in chunks:
                                    st.text_area("Conteúdo", chunk['content'], height=100)
                            else:
                                st.warning("Nenhum texto encontrado para esta página exata.")
                        else:
                            st.error("Erro na busca filtrada.")
                    except Exception as e:
                        st.error(f"Erro: {e}")

            keywords_input = st.text_input("Palavras-chave (Separadas por vírgula)", help="Ex: tutorial, configuração, erro")
            
            st.divider()
            st.subheader("2. Detalhes da Mídia")
            
            media_type = st.selectbox("Tipo de Mídia", ["video", "image", "gif"])
            
            # --- FEATURE: Seleção de Origem (URL vs Local) ---
            source_option = st.radio("Origem do Arquivo", ["🔗 URL Externa (YouTube, Web)", "📂 Arquivo Local (data/media)"], horizontal=True)
            
            final_media_url = ""
            
            if "Arquivo Local" in source_option:
                # Define categoria da pasta
                folder_category = "videos" if media_type == "video" else "images"
                if media_type == "gif": folder_category = "images"

                local_files = get_local_files(folder_category)
                
                if not local_files:
                    st.warning(f"Nenhum arquivo encontrado em `data/media/{folder_category}`")
                    st.caption("Adicione arquivos na pasta do projeto para vê-los aqui.")
                else:
                    selected_file = st.selectbox(f"Selecione o arquivo ({folder_category})", local_files)
                    if selected_file:
                        # Monta URL da API
                        final_media_url = f"{API_URL}/media/{folder_category}/{selected_file}"
                        st.success(f"Arquivo selecionado: {selected_file}")
            else:
                # URL Externa
                final_media_url = st.text_input("URL da Mídia", placeholder="https://youtube.com/watch?v=...")

            media_title = st.text_input("Título da Mídia", placeholder="Ex: Vídeo explicativo sobre X")
            media_desc = st.text_area("Descrição (Opcional)")
            
            if media_type == "video":
                media_duration = st.number_input("Duração (segundos)", min_value=0, step=10)
            else:
                media_duration = None

            # Botão de Salvar
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Salvar Associação", type="primary", use_container_width=True):
                if not final_media_url:
                    st.error("A URL da mídia é obrigatória. Selecione um arquivo ou digite um link.")
                else:
                    keywords_list = [k.strip() for k in keywords_input.split(",") if k.strip()]
                    
                    payload = {
                        "document_name": selected_doc,
                        "page_number": int(page_num),
                        "section": section_name if section_name else None,
                        "keywords": keywords_list,
                        "media_items": [
                            {
                                "type": media_type,
                                "url": final_media_url,
                                "title": media_title if media_title else "Mídia sem título",
                                "description": media_desc if media_desc else None,
                                "duration": media_duration
                            }
                        ]
                    }
                    
                    success, msg = create_association(payload)
                    if success:
                        st.balloons()
                        st.success("Associação criada com sucesso!")
                    else:
                        st.error(f"Erro ao criar: {msg}")

        # --- Coluna da Direita: Preview do PDF ---
        with col_preview:
            # st.subheader("👁️ Visualização do PDF")
            
            # if selected_doc:
            #     safe_filename = quote(selected_doc)
            #     pdf_url = f"{API_URL}/pdfs/{safe_filename}#page={page_num}"
                
            #     st.caption(f"Visualizando: {selected_doc} - Página {page_num}")
            #     st.markdown(f"[Abrir em nova aba]({pdf_url})")
                
            #     # --- CORREÇÃO PARA VISUALIZAÇÃO DO PDF (HTML INJECTION) ---
            #     pdf_display = f'''
            #         <iframe src="{pdf_url}" 
            #                 width="100%" 
            #                 height="800px" 
            #                 type="application/pdf"
            #                 style="border: 1px solid #ccc; border-radius: 5px;">
            #         </iframe>
            #     '''
            #     st.markdown(pdf_display, unsafe_allow_html=True)
            with col_preview:
                st.subheader("👁️ Visualização")
            
            if selected_doc:
                # 1. VISUALIZAÇÃO DO PDF
                safe_filename = quote(selected_doc)
                pdf_url = f"{API_URL}/pdfs/{safe_filename}#page={page_num}"
                
                st.caption(f"Documento: {selected_doc} - Página {page_num}")
                st.markdown(f"[Abrir PDF em nova aba]({pdf_url})")
                
                pdf_display = f'''
                    <iframe src="{pdf_url}" 
                            width="100%" 
                            height="600px" 
                            type="application/pdf"
                            style="border: 1px solid #ccc; border-radius: 5px;">
                    </iframe>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)

                # 2. LISTAGEM DE MÍDIAS JÁ ASSOCIADAS
                st.divider()
                st.subheader(f"📂 Mídias nesta página ({page_num})")
                
                all_assocs = list_associations()
                items_found = []

                for assoc in all_assocs:
                    if assoc.get("document_name") == selected_doc:
                        assoc_page = assoc.get("page_number")
                        if assoc_page is not None and int(assoc_page) == int(page_num):
                            items_found.extend(assoc.get("media_items", []))

                if not items_found:
                    st.info("Nenhuma mídia associada a esta página ainda.")
                else:
                    for i, item in enumerate(items_found):
                        with st.container(border=True):
                            c1, c2 = st.columns([1, 3])
                            with c1:
                                st.caption(f"#{i+1} [{item.get('type')}]")
                            with c2:
                                st.markdown(f"**{item.get('title')}**")
                            
                            url = item.get("url")
                            m_type = item.get("type")
                            
                            try:
                                if m_type == "video":
                                    # TRATAMENTO ESPECIAL PARA GOOGLE DRIVE
                                    if "drive.google.com" in url:
                                        # Tenta extrair o ID do arquivo
                                        try:
                                            # Pega o que está depois de /d/ e antes da próxima barra
                                            file_id = url.split('/d/')[1].split('/')[0]
                                            # Cria URL de embed
                                            drive_embed = f"https://drive.google.com/file/d/{file_id}/preview"
                                            
                                            st.markdown(f'''
                                                <iframe src="{drive_embed}" width="100%" height="300" allow="autoplay"></iframe>
                                            ''', unsafe_allow_html=True)
                                        except:
                                            st.error("Link do Drive inválido")
                                            st.markdown(f"🔗 [Abrir no Drive]({url})")
                                    else:
                                        # YouTube ou Arquivo Local
                                        st.video(url)

                                elif m_type in ["image", "gif"]:
                                    st.image(url, use_column_width=True)
                                else:
                                    st.markdown(f"🔗 [Link]({url})")
                            except Exception as e:
                                st.error("Erro ao carregar preview")
                                st.markdown(f"🔗 [Link]({url})")
# ============================================================================
# TAB 2: EXPLORAR CHROMADB
# ============================================================================
with tab_explore:
    st.header("Busca no Banco Vetorial")
    st.info("Use esta aba para encontrar em qual página está determinado assunto.")
    
    search_query = st.text_input("O que você procura?", placeholder="Ex: configuração de rede, cgnat...")
    
    if st.button("Buscar no Chroma"):
        if search_query:
            results = search_documents(search_query)
            st.write(f"Encontrados {len(results)} trechos relevantes:")
            
            for doc in results:
                meta = doc.get("metadata", {})
                with st.expander(f"{meta.get('source')} - Pág. {meta.get('page')} (Score similiaridade)"):
                    st.markdown(f"**Trecho:**")
                    st.text(doc.get("content", "")[:500] + "...")
                    st.markdown(f"**Metadados:** `{meta}`")
                    st.caption(f"💡 Dica: Vá na aba 'Adicionar Mídia' e selecione {meta.get('source')} pág {meta.get('page')}")

# ============================================================================
# TAB 3: ASSOCIAÇÕES EXISTENTES
# ============================================================================
with tab_list:
    st.header("Associações Cadastradas")
    
    if st.button("🔄 Atualizar Lista"):
        st.rerun()
        
    assocs = list_associations()
    
    if not assocs:
        st.info("Nenhuma associação cadastrada ainda.")
    else:
        # Tabela
        data = []
        for a in assocs:
            for m in a.get("media_items", []):
                data.append({
                    "Documento": a.get("document_name"),
                    "Página": a.get("page_number"),
                    "Seção": a.get("section"),
                    "Tipo": m.get("type"),
                    "Título Mídia": m.get("title"),
                    "URL": m.get("url"),
                    "Keywords": ", ".join(a.get("keywords", []))
                })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("Raw JSON")
        st.json(assocs)