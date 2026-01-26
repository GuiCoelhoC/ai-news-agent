from dataclasses import dataclass, asdict
from typing import List
from json import dumps

@dataclass
class NewsItem:
    """Representa uma notícia individual estruturada"""
    title: str
    link: str
    impact: str  # Descrição do impacto
    score: int   # 1-10
    source: str  # "Kubernetes Blog", "Dev.to", etc
    reason: str  # Porquê teve este score
    
    def to_dict(self):
        return asdict(self)
    
    def to_json(self):
        return dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class NewsSection:
    """Agrupa notícias por fonte/tipo"""
    section_title: str  # "BLOGS TÉCNICOS (RSS)" ou "ARTIGOS COMUNIDADE (Dev.to)"
    source: str         # "Kubernetes Blog", "CNCF", etc
    news_items: List[NewsItem]
    
    def to_dict(self):
        return {
            "section_title": self.section_title,
            "source": self.source,
            "news_items": [item.to_dict() for item in self.news_items]
        }
    
    def to_json(self):
        return dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class NewsReport:
    """Relatório completo com todas as notícias aprovadas"""
    period: str              # "2026-01-19 a 2026-01-26"
    sections: List[NewsSection]
    total_collected: int     # Total de notícias coletadas antes de filtrar
    total_approved: int      # Total após análise
    approval_rate: float     # Percentagem (ex: 26.7)
    
    def to_dict(self):
        return {
            "period": self.period,
            "sections": [section.to_dict() for section in self.sections],
            "total_collected": self.total_collected,
            "total_approved": self.total_approved,
            "approval_rate": self.approval_rate
        }
    
    def to_json(self):
        return dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def stats_summary(self) -> str:
        """Retorna resumo das métricas em texto"""
        return f"""
=== 📊 RUN STATS ===
Total coletadas: {self.total_collected}
Aprovadas (score >= 7): {self.total_approved}
Taxa aprovação: {self.approval_rate:.1f}%
Período: {self.period}
"""
