import re
from typing import List, Dict, Tuple
from urllib.parse import urlparse

class NewsParser:
    """Faz parsing do output bruto da Crew para extrair notícias estruturadas."""
    
    def __init__(self):
        # Padrões regex para diferentes formatos
        self.url_pattern = r'https?://[^\s)\]]*'
        self.markdown_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    def parse_crew_output(self, raw_output: str) -> List[Dict]:
        """
        Analisa o output bruto da crew e extrai notícias.
        
        Procura por padrões como:
        - URLs com contexto (Dev.to, RSS)
        - Links Markdown [Título](URL)
        - Secções com títulos e URLs
        
        Args:
            raw_output: Texto bruto do output da crew
        
        Returns:
            Lista de dicts com notícias: [{"title": "...", "url": "...", "source": "..."}, ...]
        """
        news_list = []
        
        # Estratégia 1: Procurar por Markdown links [título](url)
        markdown_matches = re.findall(self.markdown_link_pattern, raw_output)
        for title, url in markdown_matches:
            if self._is_valid_url(url):
                source = self._extract_source(url)
                news_list.append({
                    "title": title.strip(),
                    "url": url.strip(),
                    "source": source
                })
        
        # Estratégia 2: Procurar por URLs isoladas com contexto
        url_matches = re.finditer(self.url_pattern, raw_output)
        for match in url_matches:
            url = match.group(0)
            
            # Evitar duplicatas
            if any(news["url"] == url for news in news_list):
                continue
            
            # Extrair contexto (texto antes da URL)
            start_pos = max(0, match.start() - 200)
            context_text = raw_output[start_pos:match.start()]
            
            # Procurar título próximo
            title = self._extract_title_from_context(context_text)
            if not title:
                title = urlparse(url).netloc  # Fallback para domain
            
            source = self._extract_source(url)
            
            news_list.append({
                "title": title,
                "url": url,
                "source": source
            })
        
        # Remover duplicatas (mesma URL)
        seen_urls = set()
        unique_news = []
        for news in news_list:
            if news["url"] not in seen_urls:
                seen_urls.add(news["url"])
                unique_news.append(news)
        
        return unique_news
    
    def _extract_source(self, url: str) -> str:
        """Extrai a fonte da URL (dev.to, kubernetes.io, etc)."""
        domain = urlparse(url).netloc.lower()
        
        # Mapeamento de domínios para nomes amigáveis
        source_map = {
            "dev.to": "DEV.TO",
            "kubernetes.io": "Kubernetes",
            "cncf.io": "CNCF",
            "huggingface.co": "Hugging Face",
        }
        
        for domain_key, source_name in source_map.items():
            if domain_key in domain:
                return source_name
        
        return domain  # Retorna domínio como fallback
    
    def _extract_title_from_context(self, context: str) -> str:
        """Extrai um título probable do contexto (texto anterior à URL)."""
        # Procurar pela última linha com conteúdo
        lines = [line.strip() for line in context.split('\n') if line.strip()]
        
        if not lines:
            return ""
        
        # Pegar a última linha que não seja muito curta
        for line in reversed(lines):
            if len(line) > 10 and len(line) < 200:
                # Limpar marcadores e caracteres especiais
                line = re.sub(r'^[-*•]\s+', '', line)
                line = re.sub(r'^\d+\.\s+', '', line)
                return line
        
        return ""
    
    def _is_valid_url(self, url: str) -> bool:
        """Valida se é uma URL válida."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def parse_by_source(self, news_list: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Agrupa notícias por fonte.
        
        Returns:
            Dict com sources como keys e listas de notícias como values
        """
        grouped = {}
        for news in news_list:
            source = news.get("source", "Unknown")
            if source not in grouped:
                grouped[source] = []
            grouped[source].append(news)
        return grouped
    
    def filter_by_length(self, news_list: List[Dict], min_title_length: int = 10) -> List[Dict]:
        """Filtra notícias com títulos muito curtos (possivelmente inválidos)."""
        return [
            news for news in news_list
            if len(news.get("title", "")) >= min_title_length
        ]


# Exemplo de uso (para testes):
if __name__ == "__main__":
    sample_output = """
    📝 DEV.TO [kubernetes]: Deploy Kubernetes on AWS [https://dev.to/article/k8s-aws-guide]
    Resumo: Guia completo para deploy em produção
    
    📰 RSS [Kubernetes]: New Security Features in 1.40 (https://kubernetes.io/blog/2026/01/k8s-1-40-released)
    Snippet: Breaking changes and improvements...
    
    📝 DEV.TO [ai]: Building LLMs Locally [https://dev.to/article/local-llms]
    """
    
    parser = NewsParser()
    articles = parser.parse_crew_output(sample_output)
    
    print("Notícias extraídas:")
    for news in articles:
        print(f"  - {news['title']}")
        print(f"    URL: {news['url']}")
        print(f"    Source: {news['source']}\n")
