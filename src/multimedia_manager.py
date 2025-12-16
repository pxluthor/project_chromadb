"""
Gerenciador de Multimídia para RAG
Associa imagens, vídeos e GIFs aos documentos
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class MediaItem:
    """Representa um item de mídia"""
    type: str  # 'image', 'video', 'gif'
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[int] = None  # Para vídeos, em segundos
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class MediaAssociation:
    """Associação entre documento e mídia"""
    document_name: str  # Nome do PDF
    page_number: Optional[int] = None  # Página específica (opcional)
    section: Optional[str] = None  # Seção/tópico (ex: "CGNAT")
    keywords: List[str] = None  # Palavras-chave para busca
    media_items: List[MediaItem] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.media_items is None:
            self.media_items = []
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['media_items'] = [item.to_dict() for item in self.media_items]
        return {k: v for k, v in data.items() if v is not None}


class MultimediaManager:
    """Gerencia associações de multimídia com documentos"""
    
    def __init__(self, config_file: Union[str, Path] = "data/multimedia_config.json"):
        """
        Inicializa o gerenciador de multimídia
        
        Args:
            config_file: Caminho para o arquivo de configuração
        """
        self.config_file = Path(config_file)
        self.associations: List[MediaAssociation] = []
        
        # Carrega configuração existente
        self._load_config()
    
    def _load_config(self) -> None:
        """Carrega configuração do arquivo JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for assoc_data in data.get('associations', []):
                        media_items = [
                            MediaItem(**item) 
                            for item in assoc_data.pop('media_items', [])
                        ]
                        
                        assoc = MediaAssociation(**assoc_data)
                        assoc.media_items = media_items
                        self.associations.append(assoc)
                
                print(f"✓ Carregadas {len(self.associations)} associações de mídia")
            except Exception as e:
                print(f"⚠️  Erro ao carregar configuração de mídia: {e}")
    
    def save_config(self) -> None:
        """Salva configuração no arquivo JSON"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'version': '1.0',
            'associations': [assoc.to_dict() for assoc in self.associations]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Configuração salva em {self.config_file}")
    
    def add_association(
        self,
        document_name: str,
        media_items: List[MediaItem],
        page_number: Optional[int] = None,
        section: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> MediaAssociation:
        """
        Adiciona uma associação de mídia
        
        Args:
            document_name: Nome do documento PDF
            media_items: Lista de itens de mídia
            page_number: Número da página (opcional)
            section: Nome da seção (opcional)
            keywords: Palavras-chave para busca (opcional)
            
        Returns:
            MediaAssociation criada
        """
        assoc = MediaAssociation(
            document_name=document_name,
            page_number=page_number,
            section=section,
            keywords=keywords or [],
            media_items=media_items
        )
        
        self.associations.append(assoc)
        return assoc
    
    def find_media_by_document_old(
        self,
        document_name: str,
        page_number: Optional[int] = None
    ) -> List[MediaItem]:
        """
        Busca mídia por documento e página
        
        Args:
            document_name: Nome do documento
            page_number: Número da página (opcional)
            
        Returns:
            Lista de itens de mídia
        """
        results = []

        for assoc in self.associations:
            if assoc.document_name == document_name:
                if page_number is None or assoc.page_number is None or assoc.page_number == page_number:
                    results.extend(assoc.media_items)
        
        return results
    
    def find_media_by_document(
        self,
        document_name: str,
        page_number: Optional[int] = None
    ) -> List[MediaItem]:
        """Busca mídia por documento e página (ignora caminhos de pasta)"""
        results = []
        
        # Normaliza o nome para pegar apenas o arquivo (ex: "data/pdfs/doc.pdf" vira "doc.pdf")
        target_name = Path(document_name).name
        
        for assoc in self.associations:
            # Compara apenas o nome do arquivo
            assoc_name = Path(assoc.document_name).name
            
            if assoc_name == target_name:
                # Lógica de página:
                # Se a busca não pede página (None), traz tudo do documento.
                # Se a associação não tem página (None), é mídia do documento todo.
                # Se ambos têm página, elas devem ser iguais.
                match_page = False
                if page_number is None:
                    match_page = True
                elif assoc.page_number is None:
                    match_page = True # Mídia global do documento aparece em todas as páginas
                elif int(assoc.page_number) == int(page_number):
                    match_page = True
                
                if match_page:
                    results.extend(assoc.media_items)
        
        return results

    def find_media_by_keywords(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Busca mídia por palavras-chave
        
        Args:
            query: Query de busca
            top_k: Número máximo de resultados
            
        Returns:
            Lista de associações com mídia relevante
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_results = []
        
        for assoc in self.associations:
            score = 0
            
            # Score por seção
            if assoc.section and assoc.section.lower() in query_lower:
                score += 10
            
            # Score por keywords
            for keyword in assoc.keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in query_lower:
                    score += 5
                
                # Score por palavras individuais
                keyword_words = set(keyword_lower.split())
                common_words = query_words & keyword_words
                score += len(common_words) * 2
            
            if score > 0:
                scored_results.append({
                    'association': assoc,
                    'score': score,
                    'media_items': assoc.media_items
                })
        
        # Ordena por score
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_results[:top_k]
    
    def find_media_for_source(
        self,
        source: str,
        page: Optional[int] = None,
        query: Optional[str] = None
    ) -> List[MediaItem]:
        """
        Busca mídia para uma fonte específica
        
        Args:
            source: Nome do arquivo fonte
            page: Número da página (opcional)
            query: Query adicional para filtrar por keywords (opcional)
            
        Returns:
            Lista de itens de mídia
        """
        # Busca por documento e página
        media_items = self.find_media_by_document(source, page)
        
        # Se há query, também busca por keywords
        if query and not media_items:
            keyword_results = self.find_media_by_keywords(query, top_k=3)
            
            # Filtra resultados do mesmo documento
            for result in keyword_results:
                assoc = result['association']
                if assoc.document_name == source:
                    media_items.extend(result['media_items'])
        
        # Remove duplicatas
        seen = set()
        unique_items = []
        for item in media_items:
            item_id = (item.type, item.url)
            if item_id not in seen:
                seen.add(item_id)
                unique_items.append(item)
        
        return unique_items
    
    def enrich_sources_with_media(
        self,
        sources: List[Dict],
        query: Optional[str] = None
    ) -> List[Dict]:
        """
        Enriquece fontes do RAG com informações de mídia
        
        Args:
            sources: Lista de fontes do RAG
            query: Query original (opcional)
            
        Returns:
            Fontes enriquecidas com mídia
        """
        enriched_sources = []
        
        for source in sources:
            source_name = source.get('source', '')
            page = source.get('page')
            
            # Busca mídia associada
            media_items = self.find_media_for_source(
                source=source_name,
                page=page,
                query=query
            )
            
            # Adiciona mídia ao source
            enriched_source = source.copy()
            if media_items:
                enriched_source['media'] = [item.to_dict() for item in media_items]
            
            enriched_sources.append(enriched_source)
        
        return enriched_sources
    
    def get_all_media_by_type(self, media_type: str) -> List[Dict]:
        """Retorna toda a mídia de um tipo específico"""
        results = []
        
        for assoc in self.associations:
            for item in assoc.media_items:
                if item.type == media_type:
                    results.append({
                        'document': assoc.document_name,
                        'section': assoc.section,
                        'media': item.to_dict()
                    })
        
        return results
    
    def remove_association(
        self,
        document_name: str,
        section: Optional[str] = None
    ) -> int:
        """
        Remove associações
        
        Returns:
            Número de associações removidas
        """
        before = len(self.associations)
        
        self.associations = [
            assoc for assoc in self.associations
            if not (
                assoc.document_name == document_name and
                (section is None or assoc.section == section)
            )
        ]
        
        removed = before - len(self.associations)
        return removed
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas sobre a mídia"""
        total_associations = len(self.associations)
        total_media = sum(len(a.media_items) for a in self.associations)
        
        by_type = {}
        for assoc in self.associations:
            for item in assoc.media_items:
                by_type[item.type] = by_type.get(item.type, 0) + 1
        
        documents = set(a.document_name for a in self.associations)
        
        return {
            'total_associations': total_associations,
            'total_media_items': total_media,
            'media_by_type': by_type,
            'documents_with_media': len(documents),
            'documents': sorted(list(documents))
        }


# ============================================================================
# EXEMPLO DE USO E CONFIGURAÇÃO
# ============================================================================

def create_example_config():
    """Cria um exemplo de configuração de multimídia"""
    
    manager = MultimediaManager("data/multimedia_config.json")
    
    # Exemplo 1: CGNAT
    manager.add_association(
        document_name="manual_redes.pdf",
        section="CGNAT",
        keywords=["CGNAT", "Carrier Grade NAT", "NAT444", "compartilhamento de IP"],
        media_items=[
            MediaItem(
                type="video",
                url="https://youtube.com/watch?v=exemplo-cgnat",
                title="O que é CGNAT?",
                description="Explicação sobre Carrier Grade NAT",
                thumbnail_url="https://img.youtube.com/vi/exemplo-cgnat/maxresdefault.jpg",
                duration=180
            ),
            MediaItem(
                type="image",
                url="https://exemplo.com/diagrams/cgnat-diagram.png",
                title="Diagrama CGNAT",
                description="Arquitetura do CGNAT"
            ),
            MediaItem(
                type="gif",
                url="https://exemplo.com/animations/cgnat-flow.gif",
                title="Fluxo de dados no CGNAT",
                description="Animação mostrando como o tráfego passa pelo CGNAT"
            )
        ]
    )
    
    # Exemplo 2: Redes Neurais
    manager.add_association(
        document_name="ai_handbook.pdf",
        page_number=15,
        section="Redes Neurais",
        keywords=["neural network", "deep learning", "perceptron", "backpropagation"],
        media_items=[
            MediaItem(
                type="video",
                url="https://youtube.com/watch?v=exemplo-nn",
                title="Como funcionam Redes Neurais",
                description="Introdução visual às redes neurais",
                duration=420
            ),
            MediaItem(
                type="gif",
                url="https://exemplo.com/animations/neural-network.gif",
                title="Propagação em Rede Neural",
                description="Animação do processo de forward propagation"
            )
        ]
    )
    
    # Exemplo 3: Configuração de Router
    manager.add_association(
        document_name="manual_tecnico.pdf",
        page_number=42,
        section="Configuração Router",
        keywords=["router", "configuração", "setup", "mikrotik", "cisco"],
        media_items=[
            MediaItem(
                type="video",
                url="https://youtube.com/watch?v=exemplo-router",
                title="Configuração Básica de Router",
                description="Passo a passo para configurar router",
                thumbnail_url="https://img.youtube.com/vi/exemplo-router/maxresdefault.jpg",
                duration=600
            ),
            MediaItem(
                type="image",
                url="https://exemplo.com/screenshots/router-config.png",
                title="Interface de Configuração",
                description="Screenshot da tela de configuração"
            )
        ]
    )
    
    # Salva configuração
    manager.save_config()
    
    print("\n✅ Configuração de exemplo criada!")
    print(f"   Arquivo: {manager.config_file}")
    print(f"\n📊 Estatísticas:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return manager


if __name__ == "__main__":
    # Cria exemplo
    manager = create_example_config()
    
    # Testa busca
    print("\n" + "="*80)
    print("🔍 TESTE DE BUSCA")
    print("="*80)
    
    query = "O que é CGNAT?"
    print(f"\nQuery: {query}")
    
    results = manager.find_media_by_keywords(query)
    
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] Score: {result['score']}")
        print(f"    Documento: {result['association'].document_name}")
        print(f"    Seção: {result['association'].section}")
        print(f"    Mídia disponível:")
        for media in result['media_items']:
            print(f"      - {media.type}: {media.title}")
            print(f"        URL: {media.url}")