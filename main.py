import os
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool 
from crewai.tools import BaseTool

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
        msg['Subject'] = f"Relatório Híbrido: K8s + AI Agents ({datetime.now().strftime('%d/%m')})"

        html_body = f"""
        <html>
          <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto;">
            <div style="background-color: #2c3e50; padding: 20px; text-align: center;">
              <h2 style="color: #ffffff; margin: 0;">🧠 HomeLab Intelligence</h2>
            </div>
            <div style="padding: 30px; border: 1px solid #ddd;">
              {html_content} 
            </div>
            <div style="text-align: center; padding-top: 20px; font-size: 12px; color: #999;">
              <p>Fontes verificadas. Paywalls ignorados.</p>
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

# --- 2. CONFIGURAÇÃO TEMPORAL ---
data_hoje = datetime.now()
data_inicio = data_hoje - timedelta(days=14) # Aumentei a janela para apanhar mais coisas
periodo_str = f"{data_inicio.strftime('%Y-%m-%d')} a {data_hoje.strftime('%Y-%m-%d')}"

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
email_tool = EmailTool()

# --- 3. AGENTES (ESPECIALIZADOS) ---

researcher = Agent(
    role='Investigador de GitHub e Docs',
    goal=f'Encontrar ferramentas REAIS e Updates REAIS sobre Kubernetes e AI Agents ({periodo_str}).',
    backstory='Odeias artigos de opinião do Medium ou LinkedIn. Só queres saber de: '
          'GitHub Repos, HuggingFace Papers, CNCF Blog Posts e Documentação Oficial. '
          'Se um site der erro de JavaScript, tenta outro. '
          'SE NÃO ENCONTRARES 2+ artigos por secção, tenta queries mais largas.',
    verbose=True,
    memory=True,
    tools=[search_tool, scrape_tool],
    allow_delegation=False
)

writer = Agent(
    role='Editor Técnico Sénior',
    goal='Compilar um relatório OBRIGATORIAMENTE dividido em duas secções.',
    backstory='A tua regra de ouro é a diversidade. Não podes enviar o email só com Kubernetes. Tens de ter a secção de "Agentic AI". Se o texto estiver curto, és despedido.',
    verbose=True,
    memory=True,
    allow_delegation=False
)

auditor = Agent(
    role='Gatekeeper',
    goal='Garantir que existem as DUAS secções antes de enviar.',
    backstory='Verificas se há notícias de AI e notícias de K8s. Se faltar uma, falhas a task. Se estiver tudo bem, envias.',
    verbose=True,
    memory=True,
    tools=[email_tool],
    allow_delegation=False
)

# --- 4. TAREFAS (DIVIDIR PARA CONQUISTAR) ---

task_search = Task(
    description=(
        f"Search for recent news (last 14 days) on:\n"
        f"1. **Kubernetes**: Focus on new features, security updates, Gateway API, networking tools\n"
        f"2. **AI Agents**: Focus on frameworks (LangChain, CrewAI, AutoGen), deployment patterns\n"
        f"\n"
        f"RULES:\n"
        f"- Scrape full articles when possible (GitHub releases, official blogs)\n"
        f"- Skip: Medium paywalls, opinion pieces, outdated docs\n"
        f"- Prefer: GitHub releases, HuggingFace papers, CNCF blog, official framework docs\n"
        f"- DEDUPLICATION: Se encontrares a mesma notícia em múltiplas fontes, "
        f"guarda apenas a FONTE OFICIAL (GitHub > CNCF > outras). Ignore duplicatas."
    ),
    expected_output=(
        "Structured list (deduplicated):\n"
        "## Kubernetes (2-3 UNIQUE items)\n"
        "- Title | Primary Source | 1-line summary\n\n"
        "## AI Agents (2-3 UNIQUE items)\n"
        "- Title | Primary Source | 1-line summary\n\n"
        "Note: Each item from a DIFFERENT topic/announcement (not duplicates)"
    ),
    agent=researcher,
    tools=[search_tool, scrape_tool]
)

task_write = Task(
    description=(
        "Escreve o relatório final com esta estrutura EXATA:\n"
        "# 🐳 Atualizações Kubernetes\n"
        "- **Título**: [Link](url_completo_aqui) - Parágrafo com 1-2 frases sobre PORQUE é importante\n"
        "- **Título**: [Link](url_completo_aqui) - Parágrafo com 1-2 frases técnicas\n\n"
        "# 🤖 O Mundo dos Agentes AI\n"
        "- **Título**: [Link](url_completo_aqui) - Parágrafo com 1-2 frases sobre PORQUE é importante\n"
        "- **Título**: [Link](url_completo_aqui) - Parágrafo com 1-2 frases técnicas\n"
        "\nRegra: CADA notícia deve ter 50-100 palavras explicando utilidade. Não sejas vago. "
        "TODOS os links devem ser URLs completos (ex: https://github.com/kubernetes/kubernetes/releases)."
    ),
    expected_output='Newsletter completa em Markdown com links funcionais (formato: [Título](https://...)).',
    agent=writer,
    context=[task_search]
)

task_audit = Task(
    description=(
        "Valida:\n"
        "1. Existem as 2 secções (K8s e AI)? SIM/NÃO\n"
        "2. Cada item tem [Link](url) em formato Markdown? SIM/NÃO\n"
        "3. Cada item tem 1-2 frases explicando PORQUE é importante? SIM/NÃO\n"
        "4. Não há duplicatas entre secções? SIM/NÃO\n"
        "\nSe TODOS forem SIM: envia o email.\n"
        "Se ALGUM for NÃO: rejeita e explica qual falhou."
    ),
    expected_output='Email enviado com conteúdo validado OU erro explicado.',
    agent=auditor,
    context=[task_write]
)

crew = Crew(
    agents=[researcher, writer, auditor],
    tasks=[task_search, task_write, task_audit],
    process=Process.sequential
)

# No final, antes de crew.kickoff():
try:
    print(f"### A INICIAR BUSCA HÍBRIDA (K8s + AI) ###")
    crew.kickoff()
except Exception as e:
    print(f"❌ Erro na execução: {str(e)}")