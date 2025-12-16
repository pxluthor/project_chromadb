import streamlit as st
import requests
import pandas as pd
import base64
from urllib.parse import quote
import json

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Admin - RAG Híbrido",
    page_icon="🎬",
    layout="wide"
)

# URL da API
if "api_url" not in st.session_state:
    st.session_state.api_url = "http://10.1.254.180:8005"

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
    """Busca estatísticas, lista de arquivos e DETALHES DUAL MODE"""
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
    """Busca genérica no Vector Store (Qdrant/Chroma)"""
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
        response = requests.get(f"{API_URL}/multimedia/files/{category}")
        if response.status_code == 200:
            return response.json().get("files", [])
        return []
    except Exception as e:
        st.error(f"Erro ao listar arquivos locais: {e}")
        return []

def upload_file_api(uploaded_file):
    """Envia arquivo para a API (Vai para AMBOS os bancos no modo Dual)"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{API_URL}/documents/upload", files=files)
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except Exception as e:
        return False, str(e)

def delete_file_api(filename):
    """Solicita exclusão do arquivo (Remove de AMBOS os bancos)"""
    try:
        response = requests.delete(f"{API_URL}/documents/{filename}")
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except Exception as e:
        return False, str(e)


def render_pdf_from_api(filename, page_num=1):
    """
    Busca o PDF na API e gera um iframe HTML para exibição via Base64
    (Funciona mesmo acessando remotamente)
    """
    try:
        url = f"{API_URL}/documents/{filename}/view"
        response = requests.get(url)
        
        if response.status_code == 200:
            base64_pdf = base64.b64encode(response.content).decode('utf-8')
            # Adiciona #page=N ao final da string data URI (suporte varia por navegador)
            pdf_display = f'''
                <iframe src="data:application/pdf;base64,{base64_pdf}#page={page_num}" 
                        width="100%" 
                        height="800px" 
                        type="application/pdf"
                        style="border: 1px solid #ccc; border-radius: 5px;">
                </iframe>
            '''
            return pdf_display
        else:
            return f"<div style='color:red'>Erro ao carregar PDF da API: {response.status_code}</div>"
    except Exception as e:
        return f"<div style='color:red'>Erro de conexão: {str(e)}</div>"
    


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
    st.info("Painel Híbrido: Gerencia Qdrant (Server) e ChromaDB (Local) simultaneamente.")
    
    st.markdown("""
    **Diretórios de Mídia:**
    - `data/media/videos`
    - `data/media/images`
    """)

# --- Título ---
st.title("🎬 Gerenciador RAG (Dual Mode)")

# Abas (ADICIONEI A ABA DASHBOARD)
tab_dashboard, tab_create, tab_explore, tab_list, tab_files = st.tabs([
    "📊 Dashboard Dual",
    "➕ Adicionar Mídia", 
    "🔍 Explorar Base", 
    "📋 Associações",
    "📁 Gerenciar Arquivos"
])

# ============================================================================
# TAB 0: DASHBOARD DUAL (NOVA)
# ============================================================================
with tab_dashboard:
    st.header("Monitoramento de Sincronia")
    
    stats = get_stats()
    
    if stats:
        # Se tiver detalhes de comparação (Modo Dual)
        if "details" in stats and stats["details"]:
            details = stats["details"]
            chroma = details.get("chroma", {})
            qdrant = details.get("qdrant", {})
            
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.info("📂 **ChromaDB (Local)**")
                st.metric("Status", chroma.get("status", "Unknown").upper())
                st.metric("Chunks", chroma.get("total_chunks", 0))
                if chroma.get("status") == "online":
                    st.caption(f"Path: {chroma.get('collection_name', 'N/A')}")
            
            with c2:
                st.info("🚀 **Qdrant (Servidor)**")
                st.metric("Status", qdrant.get("status", "Unknown").upper())
                st.metric("Chunks", qdrant.get("total_chunks", 0))
                if qdrant.get("status") == "online":
                    st.caption("Host: 10.1.254.180")
            
            with c3:
                st.warning("⚙️ **Modo Operacional**")
                st.metric("Backend Ativo", stats.get("backend", "Unknown"))
                
                # Alerta de Sincronia
                chroma_count = chroma.get("total_chunks", 0)
                qdrant_count = qdrant.get("total_chunks", 0)
                
                if chroma_count != qdrant_count:
                    st.error("⚠️ Dessincronizado!")
                    st.caption("A contagem de chunks difere entre os bancos.")
                else:
                    st.success("✅ Sincronizado")
                    st.caption("Ambos os bancos possuem a mesma quantidade de dados.")
        else:
            # Modo Simples (apenas um banco)
            st.metric("Chunks Indexados", stats.get('total_chunks', 0))
            st.text(f"Backend Único: {stats.get('collection_name', 'Default')}")
    else:
        st.warning("Não foi possível obter estatísticas da API.")

# ============================================================================
# TAB 1: ADICIONAR MÍDIA
# ============================================================================
with tab_create:
    stats = get_stats()
    available_docs = stats.get("sources", [])

    if not available_docs:
        st.warning("Nenhum documento encontrado nos bancos. Faça a ingestão na aba 'Gerenciar Arquivos'.")
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
            
            # Espiar texto (Agora busca no banco ativo - Qdrant preferencialmente)
            if st.button("📖 Ver texto indexado desta página"):
                with st.spinner("Buscando no Vector Store..."):
                    try:
                        payload = {
                            "query": ".", 
                            "k": 5, 
                            "filter": {"source": selected_doc, "page": int(page_num)}
                        }
                        # Chama a função auxiliar
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
            
            source_option = st.radio("Origem do Arquivo", ["🔗 URL Externa (YouTube, Web)", "📂 Arquivo Local (data/media)"], horizontal=True)
            
            final_media_url = ""
            
            if "Arquivo Local" in source_option:
                folder_category = "videos" if media_type == "video" else "images"
                if media_type == "gif": folder_category = "images"

                local_files = get_local_files(folder_category)
                
                if not local_files:
                    st.warning(f"Nenhum arquivo encontrado em `data/media/{folder_category}`")
                    st.caption("Adicione arquivos na pasta do projeto para vê-los aqui.")
                else:
                    selected_file = st.selectbox(f"Selecione o arquivo ({folder_category})", local_files)
                    if selected_file:
                        final_media_url = f"{API_URL}/media/{folder_category}/{selected_file}"
                        st.success(f"Arquivo selecionado: {selected_file}")
            else:
                final_media_url = st.text_input("URL da Mídia", placeholder="https://youtube.com/watch?v=...")

            media_title = st.text_input("Título da Mídia", placeholder="Ex: Vídeo explicativo sobre X")
            media_desc = st.text_area("Descrição (Opcional)")
            
            if media_type == "video":
                media_duration = st.number_input("Duração (segundos)", min_value=0, step=10)
            else:
                media_duration = None

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
            st.subheader("👁️ Visualização")
            
            if selected_doc:
                # 1. VISUALIZAÇÃO DO PDF
                pdf_html = render_pdf_from_api(selected_doc, page_num=page_num)
                st.markdown(pdf_html, unsafe_allow_html=True)

                # safe_filename = quote(selected_doc)
                # pdf_url = f"{API_URL}/pdfs/{safe_filename}#page={page_num}"
                
                st.caption(f"Documento: {selected_doc} - Página {page_num}")
                #st.markdown(f"[Abrir PDF em nova aba]({pdf_url})")
                
                # pdf_display = f'''
                #     <iframe src="{pdf_url}" 
                #             width="100%" 
                #             height="600px" 
                #             type="application/pdf"
                #             style="border: 1px solid #ccc; border-radius: 5px;">
                #     </iframe>
                # '''
                # st.markdown(pdf_display, unsafe_allow_html=True)

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
                                    if "drive.google.com" in url:
                                        try:
                                            file_id = url.split('/d/')[1].split('/')[0]
                                            drive_embed = f"https://drive.google.com/file/d/{file_id}/preview"
                                            st.markdown(f'<iframe src="{drive_embed}" width="100%" height="300" allow="autoplay"></iframe>', unsafe_allow_html=True)
                                        except:
                                            st.error("Link do Drive inválido")
                                    else:
                                        st.video(url)
                                elif m_type in ["image", "gif"]:
                                    st.image(url, use_column_width=True)
                                else:
                                    st.markdown(f"🔗 [Link]({url})")
                            except Exception as e:
                                st.error("Erro ao carregar preview")

# ============================================================================
# TAB 2: EXPLORAR BASE (Antigo Explorar ChromaDB)
# ============================================================================
with tab_explore:
    st.header("Busca no Banco Vetorial")
    st.info("A busca é realizada no backend ativo (Qdrant se online, Chroma caso contrário).")
    
    search_query = st.text_input("O que você procura?", placeholder="Ex: configuração de rede, cgnat...")
    
    if st.button("Buscar"):
        if search_query:
            results = search_documents(search_query)
            st.write(f"Encontrados {len(results)} trechos relevantes:")
            
            for doc in results:
                meta = doc.get("metadata", {})
                origin = meta.get("_debug_origin", "Desconhecido")
                with st.expander(f"{meta.get('source')} - Pág. {meta.get('page')} [{origin}]"):
                    st.info(f"Fonte do Dado: **{origin}**")
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

# ============================================================================
# TAB 4: GERENCIAR ARQUIVOS (Visualização Integrada)
# ============================================================================
with tab_files:
    st.header("Gestão de Documentos PDF")
    st.info("ℹ️ As operações de Upload e Exclusão são replicadas automaticamente para **Qdrant** e **Chroma** (Dual Mode).")
    
    # Inicializa estado de visualização
    if 'selected_pdf' not in st.session_state:
        st.session_state.selected_pdf = None

    col_left, col_right = st.columns([1, 1], gap="large")
    
    # --- COLUNA ESQUERDA: UPLOAD & VISUALIZADOR ---
    with col_left:
        # 1. Área de Upload/Update
        with st.container(border=True):
            st.subheader("📤 Upload / Atualizar")
            st.info("Para **atualizar**, envie um PDF com o mesmo nome do existente.")
            
            uploaded_file = st.file_uploader("Selecione o arquivo PDF", type=['pdf'])
            
            if uploaded_file:
                stats = get_stats()
                existing_docs = stats.get("sources", [])
                is_update = uploaded_file.name in existing_docs
                
                btn_text = "🔄 Atualizar Arquivo" if is_update else "💾 Salvar Novo"
                btn_type = "primary" if not is_update else "secondary"
                
                if is_update:
                    st.warning(f"⚠️ Substituirá: '{uploaded_file.name}'")
                
                if st.button(btn_text, type=btn_type, use_container_width=True):
                    with st.spinner("Enviando para Chroma e Qdrant..."):
                        success, resp = upload_file_api(uploaded_file)
                        if success:
                            st.success("Sucesso! Sincronizado em ambos os bancos.")
                            if "stats" in resp:
                                st.json(resp["stats"])
                            st.rerun()
                        else:
                            st.error(f"Erro: {resp}")

        # 2. Área de Visualização de PDF
        if st.session_state.selected_pdf:
            st.divider()
            st.subheader(f"📄 Visualizando: {st.session_state.selected_pdf}")
            
            if st.button("Fechar Visualização", icon="❌"):
                st.session_state.selected_pdf = None
                st.rerun()
            else:
                pdf_html = render_pdf_from_api(st.session_state.selected_pdf)
                if pdf_html:
                    st.markdown(pdf_html, unsafe_allow_html=True)
                else:
                    st.error("Erro ao carregar o PDF. Verifique se o arquivo ainda existe.")

    # --- COLUNA DIREITA: LISTA DE ARQUIVOS ---
    with col_right:
        st.subheader("🗃️ Arquivos no Sistema")
        
        stats = get_stats()
        docs = stats.get("sources", [])
        
        search_term = st.text_input("🔍 Buscar", placeholder="Filtrar por nome...")
        
        if search_term:
            filtered_docs = [d for d in docs if search_term.lower() in d.lower()]
        else:
            filtered_docs = docs

        st.caption(f"Total: {len(filtered_docs)} arquivos (Base: {stats.get('backend', 'Unknown')})")
        
        with st.container(height=600, border=True):
            if not filtered_docs:
                st.info("Nenhum arquivo encontrado.")
            
            for doc in filtered_docs:
                c1, c2, c3 = st.columns([3, 0.8, 0.8])
                
                with c1:
                    if doc == st.session_state.selected_pdf:
                        st.markdown(f"👉 **{doc}**")
                    else:
                        st.markdown(f"{doc}")
                
                with c2:
                    if st.button("👁️", key=f"view_{doc}", help="Ver na esquerda"):
                        st.session_state.selected_pdf = doc
                        st.rerun()
                        
                with c3:
                    if st.button("🗑️", key=f"del_{doc}", help="Excluir de TODOS os bancos"):
                        with st.spinner("Apagando do Chroma e Qdrant..."):
                            success, msg = delete_file_api(doc)
                            if success:
                                if st.session_state.selected_pdf == doc:
                                    st.session_state.selected_pdf = None
                                st.toast("Arquivo excluído permanentemente!")
                                st.rerun()
                            else:
                                st.error("Erro ao excluir")