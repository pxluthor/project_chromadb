"""
Rotas da API para gerenciamento de multimídia
"""
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field

from src.multimedia_manager import MultimediaManager, MediaItem, MediaAssociation


# ============================================================================
# MODELS
# ============================================================================

class MediaItemRequest(BaseModel):
    """Request para criar item de mídia"""
    type: str = Field(..., description="Tipo: 'image', 'video', 'gif'")
    url: str = Field(..., description="URL da mídia")
    title: Optional[str] = Field(None, description="Título")
    description: Optional[str] = Field(None, description="Descrição")
    thumbnail_url: Optional[str] = Field(None, description="URL da thumbnail")
    duration: Optional[int] = Field(None, description="Duração em segundos (vídeos)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "video",
                "url": "https://youtube.com/watch?v=exemplo",
                "title": "Tutorial CGNAT",
                "description": "Explicação sobre CGNAT",
                "thumbnail_url": "https://img.youtube.com/vi/exemplo/maxresdefault.jpg",
                "duration": 180
            }
        }


class MediaAssociationRequest(BaseModel):
    """Request para criar associação de mídia"""
    document_name: str = Field(..., description="Nome do documento PDF")
    page_number: Optional[int] = Field(None, description="Número da página")
    section: Optional[str] = Field(None, description="Nome da seção")
    keywords: Optional[List[str]] = Field(None, description="Palavras-chave")
    media_items: List[MediaItemRequest] = Field(..., description="Itens de mídia")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_name": "manual_redes.pdf",
                "section": "CGNAT",
                "keywords": ["CGNAT", "NAT444", "Carrier Grade NAT"],
                "media_items": [
                    {
                        "type": "video",
                        "url": "https://youtube.com/watch?v=exemplo",
                        "title": "O que é CGNAT?",
                        "duration": 180
                    }
                ]
            }
        }


class MediaSearchRequest(BaseModel):
    """Request para buscar mídia"""
    query: str = Field(..., description="Query de busca")
    top_k: int = Field(default=5, description="Número máximo de resultados", ge=1, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "CGNAT",
                "top_k": 5
            }
        }


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/multimedia", tags=["multimedia"])

# Instância global do gerenciador
multimedia_manager = MultimediaManager()


@router.post("/associations", status_code=status.HTTP_201_CREATED)
async def create_association(request: MediaAssociationRequest):
    """
    Cria uma nova associação de mídia
    
    Associa imagens, vídeos ou GIFs a um documento específico.
    """
    try:
        # Converte MediaItemRequest para MediaItem
        media_items = [
            MediaItem(**item.model_dump())
            for item in request.media_items
        ]
        
        # Cria associação
        association = multimedia_manager.add_association(
            document_name=request.document_name,
            media_items=media_items,
            page_number=request.page_number,
            section=request.section,
            keywords=request.keywords
        )
        
        # Salva configuração
        multimedia_manager.save_config()
        
        return {
            "message": "Associação criada com sucesso",
            "association": association.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar associação: {str(e)}"
        )


@router.get("/associations")
async def list_associations(
    document_name: Optional[str] = None,
    media_type: Optional[str] = None
):
    """
    Lista todas as associações de mídia
    
    Filtra por documento ou tipo de mídia se especificado.
    """
    try:
        associations = multimedia_manager.associations
        
        # Filtra por documento
        if document_name:
            associations = [
                a for a in associations 
                if a.document_name == document_name
            ]
        
        # Filtra por tipo de mídia
        if media_type:
            filtered = []
            for assoc in associations:
                matching_media = [
                    m for m in assoc.media_items 
                    if m.type == media_type
                ]
                if matching_media:
                    filtered.append(assoc)
            associations = filtered
        
        return {
            "total": len(associations),
            "associations": [a.to_dict() for a in associations]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar associações: {str(e)}"
        )


@router.post("/search")
async def search_media(request: MediaSearchRequest):
    """
    Busca mídia por palavras-chave
    
    Retorna mídia associada relevante para a query.
    """
    try:
        results = multimedia_manager.find_media_by_keywords(
            query=request.query,
            top_k=request.top_k
        )
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "score": result['score'],
                "document": result['association'].document_name,
                "section": result['association'].section,
                "keywords": result['association'].keywords,
                "media": [item.to_dict() for item in result['media_items']]
            })
        
        return {
            "query": request.query,
            "total_results": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar mídia: {str(e)}"
        )


@router.get("/document/{document_name}")
async def get_media_by_document(
    document_name: str,
    page_number: Optional[int] = None
):
    """
    Busca mídia associada a um documento específico
    
    Opcionalmente filtra por número de página.
    """
    try:
        media_items = multimedia_manager.find_media_by_document(
            document_name=document_name,
            page_number=page_number
        )
        
        return {
            "document": document_name,
            "page": page_number,
            "total_media": len(media_items),
            "media": [item.to_dict() for item in media_items]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar mídia: {str(e)}"
        )


@router.get("/stats")
async def get_multimedia_stats():
    """
    Retorna estatísticas sobre a multimídia cadastrada
    """
    try:
        stats = multimedia_manager.get_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {str(e)}"
        )


@router.delete("/associations/{document_name}")
async def delete_associations(
    document_name: str,
    section: Optional[str] = None
):
    """
    Remove associações de mídia
    
    Remove todas as associações de um documento, ou apenas de uma seção específica.
    """
    try:
        removed = multimedia_manager.remove_association(
            document_name=document_name,
            section=section
        )
        
        if removed > 0:
            multimedia_manager.save_config()
        
        return {
            "message": f"{removed} associação(ões) removida(s)",
            "removed_count": removed
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover associações: {str(e)}"
        )


@router.get("/types/{media_type}")
async def get_by_type(media_type: str):
    """
    Retorna toda mídia de um tipo específico
    
    Tipos válidos: 'image', 'video', 'gif'
    """
    try:
        if media_type not in ['image', 'video', 'gif']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo inválido. Use: image, video ou gif"
            )
        
        media = multimedia_manager.get_all_media_by_type(media_type)
        
        return {
            "type": media_type,
            "total": len(media),
            "media": media
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar mídia: {str(e)}"
        )
    

@router.get("/files/{media_category}")
async def list_local_media_files(media_category: str):
    """
    Lista arquivos locais das pastas de mídia
    media_category: 'videos' ou 'images'
    """
    try:
        # Define o caminho base: data/media/videos ou data/media/images
        base_path = Path("data/media") / media_category
        
        if not base_path.exists():
            return {"files": [], "message": f"Diretório {media_category} não existe"}
            
        files = []
        # Extensões válidas para filtrar lixo
        valid_extensions = {
            'videos': ['.mp4', '.mov', '.avi', '.webm'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        }
        
        target_exts = valid_extensions.get(media_category, [])
        
        for file in base_path.iterdir():
            if file.is_file() and file.suffix.lower() in target_exts:
                files.append(file.name)
                
        return {"files": sorted(files), "base_url": f"/media/{media_category}"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar arquivos: {str(e)}"
        )