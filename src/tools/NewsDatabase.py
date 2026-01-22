import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

class NewsDatabase:
    """Gerencia persistência de notícias para evitar duplicatas."""
    
    def __init__(self, db_path: str = "data/processed_news.json"):
        self.db_path = db_path
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Carrega o banco de dados de notícias processadas."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"processed_news": [], "metadata": {}}
        return {"processed_news": [], "metadata": {}}
    
    def _save(self):
        """Salva o banco de dados em disco."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def add_news(self, title: str, url: str, source: str, score: int = 0):
        """Adiciona uma notícia processada ao banco de dados."""
        news_entry = {
            "title": title,
            "url": url,
            "source": source,
            "score": score,
            "processed_date": datetime.now().isoformat(),
            "hash": self._generate_hash(title, url)
        }
        self.data["processed_news"].append(news_entry)
        self.data["metadata"]["last_update"] = datetime.now().isoformat()
        self._save()
    
    def is_duplicate(self, title: str, url: str) -> bool:
        """Verifica se a notícia já foi processada."""
        news_hash = self._generate_hash(title, url)
        return any(news["hash"] == news_hash for news in self.data["processed_news"])
    
    def get_url_duplicates(self, url: str) -> int:
        """Conta quantas vezes a mesma URL foi processada."""
        return sum(1 for news in self.data["processed_news"] if news["url"] == url)
    
    def filter_duplicates(self, news_list: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Filtra notícias duplicadas de uma lista.
        Retorna: (new_news, duplicates)
        """
        new_news = []
        duplicates = []
        
        for news in news_list:
            if self.is_duplicate(news.get("title", ""), news.get("url", "")):
                duplicates.append(news)
            else:
                new_news.append(news)
        
        return new_news, duplicates
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas sobre notícias processadas."""
        return {
            "total_processed": len(self.data["processed_news"]),
            "last_update": self.data["metadata"].get("last_update", "Never"),
            "by_source": self._count_by_source()
        }
    
    def _count_by_source(self) -> Dict:
        """Conta notícias por fonte."""
        counts = {}
        for news in self.data["processed_news"]:
            source = news.get("source", "Unknown")
            counts[source] = counts.get(source, 0) + 1
        return counts
    
    @staticmethod
    def _generate_hash(title: str, url: str) -> str:
        """Gera um hash simples baseado em título e URL."""
        import hashlib
        combined = f"{title}|{url}".lower()
        return hashlib.md5(combined.encode()).hexdigest()
    
    def cleanup_old_entries(self, days: int = 90):
        """Remove notícias processadas há mais de N dias."""
        cutoff_date = datetime.fromisoformat(
            (datetime.now() - timedelta(days=days)).isoformat()
        )
        original_count = len(self.data["processed_news"])
        
        self.data["processed_news"] = [
            news for news in self.data["processed_news"]
            if datetime.fromisoformat(news["processed_date"]) > cutoff_date
        ]
        
        removed = original_count - len(self.data["processed_news"])
        if removed > 0:
            self._save()
        return removed
