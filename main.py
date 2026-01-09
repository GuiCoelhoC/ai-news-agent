import os
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
# Garante que tens estas bibliotecas instaladas: pip install crewai crewai-tools markdown python-dotenv
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from crewai.tools import BaseTool


# 0. CARREGAR SEGREDOS
load_dotenv()

# --- 1. FERRAMENTA DE EMAIL ---
class EmailTool(BaseTool):
    name: str = "Ferramenta de Envio de Email"
    description: str = "Envia o corpo do texto (formatado em HTML) para a lista de distribuição."

    def _run(self, body: str) -> str:
        sender_email = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("EMAIL_PASSWORD")
        receivers_str = os.getenv("EMAIL_RECEIVERS")
        
        if not all([sender_email, sender_password, receivers_str]):
            return "Erro: Faltam variáveis de ambiente."

        receivers_list = [email.strip() for email in receivers_str.split(',')]
        html_content = markdown.markdown(body)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email 
        msg['Subject'] = f"Briefing AI (Com Fontes): {datetime.now().strftime('%d/%m')}"

        html_body = f"""
        <html>
          <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto;">
            <div style="background-color: #1a252f; padding: 20px; text-align: center;">
              <h2 style="color: #ffffff; margin: 0;">📰 Relatório de Inteligência</h2>
            </div>
            <div style="padding: 30px; border: 1px solid #ddd;">
              {html_content} 
            </div>
            <div style="text-align: center; padding-top: 20px; font-size: 12px; color: #999;">
              <p>Fontes verificadas e datadas.</p>
            </div>
          </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receivers_list, msg.as_string())
            server.quit()
            return f"Email enviado para {len(receivers_list)} destinatários."
        except Exception as e:
            return f"Erro SMTP: {str(e)}"

# --- 2. CONFIGURAÇÃO TEMPORAL (Janela de 45 dias) ---
data_hoje = datetime.now()
data_inicio = data_hoje - timedelta(days=45)
periodo_str = f"{data_inicio.strftime('%Y-%m-%d')} a {data_hoje.strftime('%Y-%m-%d')}"


#--- Ferramentas ---
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
email_tool = EmailTool()

# --- 3. AGENTES ---

# O "Aspira" que traz tudo o que encontra
researcher = Agent(
    role='Analista de Inteligência Profunda',
    goal=f'Ler o CONTEÚDO REAL das páginas sobre Kubernetes e Agentic AI ({periodo_str}).',
    backstory='Não confias em manchetes. Quando encontras um link interessante no Google, USAS O SCRAPER para ler o artigo completo e extrair os detalhes técnicos reais.',
    verbose=True,
    memory=True,
    tools=[search_tool, scrape_tool],
    allow_delegation=False
)

# O Jornalista rigoroso
writer = Agent(
    role='Editor Técnico',
    goal='Sintetizar a informação profunda em bullets claros.',
    backstory='Recebes relatórios detalhados. O teu trabalho é limpar o ruído e escrever o resumo final. Obrigatório manter os LINKS originais.',
    verbose=True,
    memory=True,
    allow_delegation=False
)

auditor = Agent(
    role='Auditor de Qualidade',
    goal='Garantir links e envio.',
    backstory='Verificas se existem links. Se sim, envias.',
    verbose=True,
    memory=True,
    tools=[email_tool],
    allow_delegation=False
)

# --- TAREFAS ---

task_search = Task(
    description=(
        f"1. Usa o Search para encontrar 4 a 5 URLs recentes sobre 'Kubernetes Gateway API' ou 'Agentic AI Patterns'.\n"
        f"2. IMPORTANTE: Para CADA URL promissor, usa a ferramenta 'ScrapeWebsiteTool' para ler o conteúdo da página.\n"
        f"3. Extrai: O problema que a ferramenta resolve e exemplos de código se houver."
    ),
    expected_output='Relatório detalhado baseado no CONTEÚDO COMPLETO dos sites, com URLs.',
    agent=researcher
)

task_write = Task(
    description=(
        "Escreve a newsletter baseada na pesquisa profunda.\n"
        "Formato:\n"
        "## Título (Data)\n"
        "* **O que é:** Resumo técnico.\n"
        "* **Por que importa:** Impacto real.\n"
        "* [Ler Fonte Completa](URL)"
    ),
    expected_output='Newsletter rica em detalhes técnicos e formatada em Markdown.',
    agent=writer,
    context=[task_search]
)

task_audit = Task(
    description="Valida se tem links e envia o email.",
    expected_output='Email enviado.',
    agent=auditor,
    context=[task_write]
)

crew = Crew(
    agents=[researcher, writer, auditor],
    tasks=[task_search, task_write, task_audit],
    process=Process.sequential
)

print(f"### A CORRER COM SCRAPING REAL ###")
crew.kickoff()