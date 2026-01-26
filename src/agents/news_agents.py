from crewai import Agent
from src.tools.DataIngestion import DevToTool, RSSFeedTool
from src.tools.summarizer_tool import SummarizerTool
from src.tools.validator_tool import ValidatorTool

class NewsAgents:
    def __init__(self):
        # Instancia as ferramentas de ingestão
        self.devto_tool = DevToTool()
        self.rss_tool = RSSFeedTool()
        self.summarizer_tool = SummarizerTool()
        self.validator_tool = ValidatorTool()

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
            backstory='Recebes dados estruturados e transformas em relatório HTML/Markdown legível. '
                      'Mantém o formato: Título → Link → Impacto → Score. '
                      'Se não há dados, escreves "Sem atualizações".',
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
                      'Usa a ferramenta Summarizer para resumir textos longos. '
                      'Usa a ferramenta Validator para verificar se links funcionam. '
                      'Sê rigoroso. Qualidade > Quantidade.',
            verbose=True,
            memory=True,
            tools=[self.summarizer_tool, self.validator_tool],
            allow_delegation=False
        )