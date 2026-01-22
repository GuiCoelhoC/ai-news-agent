from src.tools.NewsDatabase import NewsDatabase
from typing import List, Dict

class NewsProcessor:
    """Orquestra a coleta, deduplicação e armazenamento de notícias."""
    
    def __init__(self):
        self.db = NewsDatabase()
    
    def process_and_save(self, raw_content: str, source: str = "crew_output") -> Dict:
        """
        Processa output da crew e salva notícias únicas no banco de dados.
        
        Args:
            raw_content: Output bruto da crew (resultado do pipeline)
            source: Origem dos dados (padrão: "crew_output")
        
        Returns:
            Dicionário com estatísticas do processamento
        """
        stats = {
            "total_articles": 0,
            "new_articles": 0,
            "duplicates": 0,
            "articles": []
        }
        
        # Aqui você pode parsear o raw_content para extrair artigos
        # Por agora, apenas registamos que foi processado
        stats["source"] = source
        stats["processed_date"] = __import__('datetime').datetime.now().isoformat()
        
        return stats
    
    def register_approved_news(self, title: str, url: str, source: str, score: int = 8):
        """Registra uma notícia aprovada pela crew no banco de dados."""
        if not self.db.is_duplicate(title, url):
            self.db.add_news(title, url, source, score)
            return True
        return False
    
    def get_database_stats(self) -> Dict:
        """Retorna estatísticas do banco de dados."""
        return self.db.get_stats()
    
    def cleanup_old(self, days: int = 90) -> int:
        """Remove notícias antigas do banco de dados."""
        return self.db.cleanup_old_entries(days)
