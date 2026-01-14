from crewai import Agent
from src.tools.DataIngestion import GitHubTool, DevToTool, RSSFeedTool 
from src.tools.email_tool import EmailTool

class NewsAgents:
    def __init__(self):
        # Instancia as ferramentas de ingestão
        self.github_tool = GitHubTool()
        self.devto_tool = DevToTool()
        self.rss_tool = RSSFeedTool()
        self.email_tool = EmailTool()

    def researcher(self, periodo):
        return Agent(
            role='Engenheiro de Dados de Inteligência',
            goal=f'Coletar dados brutos via API sobre Kubernetes e AI ({periodo}).',
            backstory='Tu não pesquisas no Google. Tu consultas APIs e Feeds oficiais. '
                      'A tua função é agregar dados estruturados do GitHub, Dev.to e Blogs Oficiais. '
                      'Se a API der erro, reportas o erro, não inventas nada.',
            verbose=True,
            memory=True,
            tools=[self.github_tool, self.devto_tool, self.rss_tool], 
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

    def auditor(self):
        return Agent(
            role='Gatekeeper',
            goal='Garantir envio.',
            backstory='Validas e envias.',
            verbose=True,
            memory=True,
            tools=[self.email_tool],
            allow_delegation=False
        )