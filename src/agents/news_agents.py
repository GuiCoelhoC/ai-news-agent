from crewai import Agent
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from src.tools.email_tool import EmailTool

class NewsAgents:
    def __init__(self):
        self.search_tool = SerperDevTool()
        self.scrape_tool = ScrapeWebsiteTool()
        self.email_tool = EmailTool()

    def researcher(self, periodo):
        return Agent(
            role='Investigador de Notícias Tech',
    goal=f'Encontrar NOTÍCIAS CONCRETAS sobre Kubernetes e AI Agents ({periodo_str}). Releases, security updates, announcements.',
    backstory='Procuras notícias REAIS e tangíveis, não tutoriais ou docs genéricas. Preferências: '
          'GitHub Releases, HuggingFace Model Releases, Security Advisories (CVE), '
          'Announcements de frameworks (LangChain, CrewAI updates), '
          'CNCF Blog Posts sobre features novas, '
          'Tech news sites confiáveis (TechCrunch, The Register, DevOps.com para K8s). '
          'Se um site der erro de JavaScript, tenta outro. '
          'SE NÃO ENCONTRARES 2+ notícias DIFERENTES por secção, tenta queries mais largas. '
          'IMPORTANTE: Lembra-te das notícias que já encontraste antes para não repetir.',
    verbose=True,
    memory=True,
    tools=[self.search_tool, self.scrape_tool],
    allow_delegation=False
        )

    def writer(self):
        return Agent(
            role='Editor Técnico Sénior',
            goal='Compilar um relatório OBRIGATORIAMENTE dividido em duas secções.',
            backstory='A tua regra de ouro é a diversidade. Não podes enviar o email só com Kubernetes. Tens de ter a secção de "Agentic AI". Se o texto estiver curto, és despedido. '
            'Lembra-te dos estilos e formatos que usaste antes para manter consistência.',
            verbose=True,
            memory=True,
            allow_delegation=False
        )

    def auditor(self):
        return Agent(
                role='Gatekeeper',
                goal='Garantir que existem as DUAS secções antes de enviar.',
                backstory='Verificas se há notícias de AI e notícias de K8s. Se faltar uma, falhas a task. Se estiver tudo bem, envias. '
                'Lembra-te dos critérios de validação anteriores para manter padrões.',
                verbose=True,
                memory=True,
                tools=[email_tool],
                allow_delegation=False
        )