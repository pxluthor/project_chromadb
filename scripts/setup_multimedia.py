#!/usr/bin/env python3
"""
Script para configurar multimídia no sistema RAG
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.multimedia_manager import MultimediaManager, MediaItem


def setup_example_multimedia():
    """Configura exemplos de multimídia"""
    
    print("="*80)
    print("🎬 CONFIGURAÇÃO DE MULTIMÍDIA")
    print("="*80)
    
    manager = MultimediaManager()
    
    examples = [
        {
            "document": "manual_redes.pdf",
            "section": "CGNAT",
            "keywords": ["CGNAT", "Carrier Grade NAT", "NAT444", "compartilhamento de IP", "IPv4"],
            "media": [
                {
                    "type": "video",
                    "url": "https://www.youtube.com/watch?v=exemplo-cgnat",
                    "title": "O que é CGNAT? - Explicação Completa",
                    "description": "Entenda como funciona o Carrier Grade NAT e por que ele é usado",
                    "thumbnail_url": "https://img.youtube.com/vi/exemplo-cgnat/maxresdefault.jpg",
                    "duration": 180
                },
                {
                    "type": "image",
                    "url": "https://exemplo.com/diagrams/cgnat-architecture.png",
                    "title": "Arquitetura CGNAT",
                    "description": "Diagrama mostrando a arquitetura de rede com CGNAT"
                },
                {
                    "type": "gif",
                    "url": "https://exemplo.com/animations/cgnat-flow.gif",
                    "title": "Fluxo de Dados no CGNAT",
                    "description": "Animação mostrando como os pacotes atravessam o CGNAT"
                }
            ]
        },
        {
            "document": "manual_tecnico.pdf",
            "section": "Configuração de Router",
            "page": 42,
            "keywords": ["router", "configuração", "mikrotik", "cisco", "setup inicial"],
            "media": [
                {
                    "type": "video",
                    "url": "https://www.youtube.com/watch?v=exemplo-router-config",
                    "title": "Configuração Básica de Router - Passo a Passo",
                    "description": "Tutorial completo de configuração inicial",
                    "duration": 600
                },
                {
                    "type": "image",
                    "url": "https://exemplo.com/screenshots/router-interface.png",
                    "title": "Interface de Configuração",
                    "description": "Screenshot da tela de configuração do router"
                }
            ]
        },
        {
            "document": "manual_tecnico.pdf",
            "section": "VLAN",
            "keywords": ["VLAN", "Virtual LAN", "segmentação de rede", "802.1Q"],
            "media": [
                {
                    "type": "gif",
                    "url": "https://exemplo.com/animations/vlan-segmentation.gif",
                    "title": "Segmentação de Rede com VLAN",
                    "description": "Animação mostrando como VLANs segmentam a rede"
                },
                {
                    "type": "video",
                    "url": "https://www.youtube.com/watch?v=exemplo-vlan",
                    "title": "Entendendo VLANs",
                    "duration": 420
                }
            ]
        },
        {
            "document": "troubleshooting_guide.pdf",
            "section": "Diagnóstico de Conexão",
            "keywords": ["ping", "traceroute", "diagnóstico", "troubleshooting", "conectividade"],
            "media": [
                {
                    "type": "video",
                    "url": "https://www.youtube.com/watch?v=exemplo-diagnostic",
                    "title": "Ferramentas de Diagnóstico de Rede",
                    "description": "Como usar ping, traceroute e outras ferramentas",
                    "duration": 480
                },
                {
                    "type": "image",
                    "url": "https://exemplo.com/screenshots/wireshark-analysis.png",
                    "title": "Análise de Pacotes com Wireshark",
                    "description": "Exemplo de captura e análise de tráfego"
                }
            ]
        }
    ]
    
    # Adiciona cada exemplo
    for i, example in enumerate(examples, 1):
        print(f"\n[{i}/{len(examples)}] Adicionando: {example['section']}")
        
        media_items = [MediaItem(**media) for media in example['media']]
        
        manager.add_association(
            document_name=example['document'],
            section=example['section'],
            page_number=example.get('page'),
            keywords=example['keywords'],
            media_items=media_items
        )
        
        print(f"    ✓ {len(media_items)} item(ns) de mídia adicionado(s)")
    
    # Salva configuração
    manager.save_config()
    
    # Exibe estatísticas
    print("\n" + "="*80)
    print("📊 ESTATÍSTICAS")
    print("="*80)
    
    stats = manager.get_statistics()
    print(f"\n✓ Total de associações: {stats['total_associations']}")
    print(f"✓ Total de itens de mídia: {stats['total_media_items']}")
    print(f"\n📁 Mídia por tipo:")
    for media_type, count in stats['media_by_type'].items():
        print(f"   • {media_type}: {count}")
    
    print(f"\n📄 Documentos com mídia ({stats['documents_with_media']}):")
    for doc in stats['documents']:
        print(f"   • {doc}")
    
    print("\n" + "="*80)
    print("✅ CONFIGURAÇÃO CONCLUÍDA")
    print("="*80)
    print(f"\nArquivo de configuração: {manager.config_file}")
    print("\n💡 Dicas:")
    print("   • A mídia agora será retornada automaticamente nas queries")
    print("   • Use a API /multimedia para gerenciar associações")
    print("   • Edite data/multimedia_config.json para personalizar")
    
    return manager


def test_multimedia_search():
    """Testa busca de multimídia"""
    
    print("\n" + "="*80)
    print("🔍 TESTE DE BUSCA DE MULTIMÍDIA")
    print("="*80)
    
    manager = MultimediaManager()
    
    test_queries = [
        "O que é CGNAT?",
        "Como configurar router?",
        "VLAN segmentação",
        "Diagnóstico de rede"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        results = manager.find_media_by_keywords(query, top_k=3)
        
        if results:
            print(f"   Encontrados {len(results)} resultado(s):\n")
            for i, result in enumerate(results, 1):
                assoc = result['association']
                print(f"   [{i}] Score: {result['score']}")
                print(f"       Documento: {assoc.document_name}")
                print(f"       Seção: {assoc.section}")
                print(f"       Mídia:")
                for media in result['media_items']:
                    print(f"         • {media.type}: {media.title}")
                print()
        else:
            print("   ⚠️  Nenhum resultado encontrado")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Configura multimídia no sistema RAG"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Testa busca de multimídia"
    )
    
    args = parser.parse_args()
    
    try:
        if args.test:
            test_multimedia_search()
        else:
            setup_example_multimedia()
            
            # Pergunta se quer testar
            response = input("\n🔍 Deseja testar a busca de multimídia? (s/n): ")
            if response.lower() == 's':
                test_multimedia_search()
        
        print("\n✅ Concluído!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()