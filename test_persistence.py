#!/usr/bin/env python3
"""
Script de teste para validar o sistema de persistência completo.
Simula o fluxo de notícias sem chamar APIs reais.
"""

from src.utils.NewsParser import NewsParser
from src.utils.NewsProcessor import NewsProcessor
from src.tools.NewsDatabase import NewsDatabase
import json

def test_parser():
    """Testa o parser com output simulado da crew."""
    print("\n" + "="*60)
    print("🧪 TESTE 1: Parser de Notícias")
    print("="*60)
    
    # Simular output da crew
    mock_crew_output = """
    Final Report: AI & Kubernetes News
    
    📝 DEV.TO [kubernetes]: Kubernetes 1.40 New Features [https://dev.to/guides/k8s-1-40]
    Resumo: Breaking changes in RBAC and new networking features
    
    📰 RSS [Kubernetes]: Security Release - CVE Patches (https://kubernetes.io/blog/2026/01/security-patches)
    Snippet: Critical security updates for production clusters
    
    📝 DEV.TO [ai]: Building with Open LLMs [https://dev.to/guides/open-llms]
    Resumo: Guide to deploying Llama 2 and Mistral locally
    
    📰 RSS [CNCF]: Cloud Native Trends 2026 (https://www.cncf.io/blog/2026/01/trends)
    Snippet: Report on emerging technologies in cloud computing
    """
    
    parser = NewsParser()
    articles = parser.parse_crew_output(mock_crew_output)
    
    print(f"\n✅ Notícias extraídas: {len(articles)}\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['url']}\n")
    
    return articles

def test_database_persistence(articles):
    """Testa a persistência das notícias no banco de dados."""
    print("\n" + "="*60)
    print("🧪 TESTE 2: Persistência em Banco de Dados")
    print("="*60)
    
    processor = NewsProcessor()
    
    print("\n📝 Registando notícias...")
    for news in articles:
        was_new = processor.register_approved_news(
            title=news['title'],
            url=news['url'],
            source=news['source'],
            score=8
        )
        status = "✅ NOVA" if was_new else "⏭️  DUPLICADA"
        print(f"{status}: {news['title'][:50]}...")
    
    return processor

def test_database_stats(processor):
    """Testa as estatísticas do banco de dados."""
    print("\n" + "="*60)
    print("🧪 TESTE 3: Estatísticas")
    print("="*60)
    
    stats = processor.get_database_stats()
    
    print(f"\n📊 Estatísticas Totais:")
    print(f"   Total de notícias: {stats['total_processed']}")
    print(f"   Última atualização: {stats['last_update']}")
    print(f"\n📍 Por fonte:")
    for source, count in stats['by_source'].items():
        print(f"   - {source}: {count} notícias")

def test_duplicates_detection(articles):
    """Testa a detecção de duplicatas."""
    print("\n" + "="*60)
    print("🧪 TESTE 4: Detecção de Duplicatas")
    print("="*60)
    
    processor = NewsProcessor()
    
    # Primeira vez - todas são novas
    print("\n🔄 Primeira execução (novo batch):")
    new_count = 0
    for news in articles[:2]:  # Primeiras 2
        if processor.register_approved_news(
            title=news['title'],
            url=news['url'],
            source=news['source'],
            score=8
        ):
            new_count += 1
            print(f"   ✅ Registada: {news['title'][:50]}...")
    
    print(f"\nTotal de NOVAS: {new_count}")
    
    # Segunda vez - tentar inserir as mesmas
    print("\n🔄 Segunda execução (batch com duplicatas):")
    dup_count = 0
    for news in articles[:2]:  # Mesmas 2
        if not processor.register_approved_news(
            title=news['title'],
            url=news['url'],
            source=news['source'],
            score=8
        ):
            dup_count += 1
            print(f"   ⏭️  Duplicata detectada: {news['title'][:50]}...")
    
    print(f"\nTotal de DUPLICATAS: {dup_count}")
    
    if dup_count == 2:
        print("\n✅ Detecção de duplicatas funcionando corretamente!")
    else:
        print("\n❌ Erro na detecção de duplicatas!")

def test_file_persistence():
    """Valida que os dados foram realmente guardados em arquivo."""
    print("\n" + "="*60)
    print("🧪 TESTE 5: Validação de Arquivo")
    print("="*60)
    
    db_path = "data/processed_news.json"
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total = len(data.get('processed_news', []))
        print(f"\n✅ Arquivo {db_path} existe e é válido!")
        print(f"   Contém {total} notícias")
        
        if total > 0:
            print(f"\n   Últimas 3 notícias registadas:")
            for news in data['processed_news'][-3:]:
                print(f"   - {news['title'][:50]}...")
                print(f"     Data: {news['processed_date'][:10]}")
    except FileNotFoundError:
        print(f"\n❌ Arquivo {db_path} não encontrado!")
    except json.JSONDecodeError:
        print(f"\n❌ Arquivo {db_path} corrompido!")

def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🚀 SUITE DE TESTES - SISTEMA DE PERSISTÊNCIA")
    print("="*60)
    
    try:
        # Teste 1: Parser
        articles = test_parser()
        
        # Teste 2: Persistência
        processor = test_database_persistence(articles)
        
        # Teste 3: Estatísticas
        test_database_stats(processor)
        
        # Teste 4: Duplicatas
        test_duplicates_detection(articles)
        
        # Teste 5: Arquivo
        test_file_persistence()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES COMPLETADOS!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO durante testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
