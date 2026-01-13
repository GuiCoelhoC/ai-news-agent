import requests
import feedparser
import os
from crewai.tools import BaseTool

# --- FERRAMENTA 1: GitHub Releases (A Verdade Oficial) ---
class GitHubTool(BaseTool):
    name: str = "GitHub Releases Fetcher"
    description: str = "Busca as releases OFICIAIS de um repositório. Use para obter versões exatas e changelogs."

    def _run(self, repo_names: str) -> str:
        """repo_names: Lista separada por vírgula (ex: 'kubernetes/kubernetes,langchain-ai/langchain')"""
        token = os.getenv("GITHUB_TOKEN")
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        results = []
        
        for repo in [r.strip() for r in repo_names.split(',')]:
            try:
                url = f"https://api.github.com/repos/{repo}/releases/latest"
                response = requests.get(url, headers=headers)
                if response.status_code == 404:
                    results.append(f"❌ {repo}: Sem release encontrada.")
                    continue
                response.raise_for_status()
                data = response.json()
                results.append(f"✅ GITHUB {repo} [{data.get('tag_name')}]: {data.get('html_url')}\nCHANGELOG: {data.get('body')[:1000]}...")
            except Exception as e:
                results.append(f"⚠️ Erro GitHub {repo}: {str(e)}")
        return "\n\n".join(results)

# --- FERRAMENTA 2: Dev.to API (Artigos de Engenharia) ---
class DevToTool(BaseTool):
    name: str = "Dev.to Articles Fetcher"
    description: str = "Busca artigos técnicos recentes no Dev.to por tag. Use para encontrar tendências de engenharia."

    def _run(self, tags: str) -> str:
        """tags: Lista separada por vírgula (ex: 'kubernetes,ai,devops')"""
        results = []
        for tag in [t.strip() for t in tags.split(',')]:
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

# --- FERRAMENTA 3: RSS Feed Reader (Blogs Oficiais) ---
class RSSFeedTool(BaseTool):
    name: str = "RSS Feed Reader"
    description: str = "Lê as últimas entradas de um Blog Técnico via RSS. Use para blogs da CNCF, Kubernetes, etc."

    def _run(self, feed_urls: str) -> str:
        """feed_urls: URLs de RSS separados por vírgula"""
        results = []
        for url in [u.strip() for u in feed_urls.split(',')]:
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