from crewai import Agent
from src.tools.DataIngestion import DevToTool, RSSFeedTool 

class NewsAgents:
    def __init__(self):
        # Instancia as ferramentas de ingestão
        self.devto_tool = DevToTool()
        self.rss_tool = RSSFeedTool()

    def researcher(self, periodo):
        return Agent(
            role='Engenheiro de Dados de Inteligência',
            goal=f'Coletar dados brutos via API sobre Kubernetes e AI ({periodo}).',
            backstory='Tu não pesquisas no Google. Tu consultas APIs e Feeds oficiais. '
                      'A tua função é agregar dados estruturados de Dev.to e Blogs Oficiais. '
                      'Se a API der erro, reportas o erro, não inventas nada.',
            verbose=True,
            memory=True,
            tools=[self.devto_tool, self.rss_tool], 
            allow_delegation=False
        )

    def writer(self):
        
        return Agent(
            role='Editor Técnico Sénior',
            goal='Compilar um relatório baseado EXCLUSIVAMENTE nos dados fornecidos.',
            backstory='Recebes dados brutos de APIs. Transformas JSON e RSS em texto legível. '
                      'Se o Researcher disser que não há dados, tu escreves "Sem atualizações".',
            verbose=True,
            memory=True,
            allow_delegation=False
        )

    def analyst(self):
        return Agent(
            role='Analista de Impacto Técnico',
            goal='Avaliar e filtrar notícias por relevância e impacto real na indústria.',
            backstory='Tu recebes notícias brutas e avalias CRITICAMENTE o impacto delas. '
                      'Ignoras releases vazias, anúncios triviais e content marketing. '
                      'Só aprova notícias que têm valor real: breaking news, arquitectura importante, '
                      'trends emergentes, mudanças de paradigma. Score 1-10, aprova só as com score >= 7. '
                      'Sê rigoroso. Qualidade > Quantidade.',
            verbose=True,
            memory=True,
            allow_delegation=False
        )