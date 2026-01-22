#!/usr/bin/env python3
"""
Script utilitário para inspecionar o banco de dados de notícias processadas.
Use: python inspect_database.py
"""

import json
import os
from datetime import datetime
from src.tools.NewsDatabase import NewsDatabase

def main():
    db = NewsDatabase()
    stats = db.get_stats()
    
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS DE NOTÍCIAS")
    print("="*60)
    print(f"\n📝 Total de notícias processadas: {stats['total_processed']}")
    print(f"🕐 Última atualização: {stats['last_update']}")
    
    if stats['by_source']:
        print(f"\n📍 Distribuição por fonte:")
        for source, count in stats['by_source'].items():
            print(f"   - {source}: {count} notícias")
    
    # Mostrar as últimas 5 notícias
    if db.data['processed_news']:
        print(f"\n📰 Últimas 5 notícias processadas:")
        for i, news in enumerate(db.data['processed_news'][-5:], 1):
            print(f"\n   {i}. {news['title'][:60]}...")
            print(f"      URL: {news['url']}")
            print(f"      Fonte: {news['source']}")
            print(f"      Score: {news['score']}")
            print(f"      Data: {news['processed_date'][:10]}")
    else:
        print("\n⚠️  Nenhuma notícia processada ainda.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
