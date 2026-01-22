import requests
import feedparser
import os
import json
from crewai.tools import BaseTool

# --- FERRAMENTA 1: Dev.to API (Artigos de Engenharia) ---
class DevToTool(BaseTool):
    name: str = "Dev.to Articles Fetcher"
    description: str = "Busca artigos técnicos recentes no Dev.to por tag. Use para encontrar tendências de engenharia."

    def _run(self, tags_source: str = "config") -> str:
        """
        tags_source: Se "config", lê do arquivo configs/news_sources.json.
                     Se tags separadas por vírgula, busca essas específicas.
        """
        tags = []
        
        if tags_source == "config":
            # Lê do arquivo de configuração
            try:
                config_path = os.path.join(os.path.dirname(__file__), "../../configs/news_sources.json")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                tags = config.get('devto_tags', [])
            except Exception as e:
                return f"⚠️ Erro ao ler configs/news_sources.json: {str(e)}"
        else:
            # Tags diretas
            tags = [t.strip() for t in tags_source.split(',')]
        
        results = []
        for tag in tags:
            try:
                # Busca top 3 artigos mais recentes da tag
                url = f"https://dev.to/api/articles?tag={tag}&per_page=3&top=7" 
                response = requests.get(url)
                response.raise_for_status()
                articles = response.json()
                
                for art in articles:
                    results.append(f"📝 DEV.TO [{tag}]: {art['title']} ({art['url']})\nResumo: {art['description']}")
            except Exception as e:
                results.append(f"⚠️ Erro Dev.to {tag}: {str(e)}")
        return "\n\n".join(results)

# --- FERRAMENTA 2: RSS Feed Reader (Blogs Oficiais) ---
class RSSFeedTool(BaseTool):
    name: str = "RSS Feed Reader"
    description: str = "Lê as últimas entradas de um Blog Técnico via RSS. Use para blogs da CNCF, Kubernetes, etc."

    def _run(self, feed_source: str = "config") -> str:
        """
        feed_source: Se "config", lê do arquivo configs/news_sources.json.
                     Se URL, busca apenas esse RSS.
        """
        urls = []
        
        if feed_source == "config":
            # Lê do arquivo de configuração
            try:
                config_path = os.path.join(os.path.dirname(__file__), "../../configs/news_sources.json")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                urls = [feed['url'] for feed in config.get('rss_feeds', [])]
            except Exception as e:
                return f"⚠️ Erro ao ler configs/news_sources.json: {str(e)}"
        else:
            # Feed URL direto
            urls = [feed_source]
        
        results = []
        for url in urls:
            try:
                feed = feedparser.parse(url)
                if feed.bozo: # Deteta XML mal formado
                    results.append(f"⚠️ Erro RSS {url}: XML Inválido")
                    continue
                
                entries = feed.entries[:3] # Só os 3 mais recentes
                for entry in entries:
                    results.append(f"📰 RSS [{feed.feed.get('title', 'Blog')}]: {entry.title} ({entry.link})\nSnippet: {entry.get('summary', '')[:300]}")
            except Exception as e:
                results.append(f"⚠️ Erro RSS {url}: {str(e)}")
        return "\n\n".join(results)