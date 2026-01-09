import os
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
# CORREÇÃO DO IMPORT (Caso ainda tenhas o erro da screenshot anterior)
from crewai_tools import SerperDevTool 
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

search_tool = SerperDevTool()
email_tool = EmailTool()

# --- 3. AGENTES (REESTRUTURADOS) ---

# O "Aspira" que traz tudo o que encontra
researcher = Agent(
    role='Analista de Dados Brutos',
    goal=f'Mapear TODAS as novidades relevantes sobre Kubernetes e Agentic AI ({periodo_str}).',
    backstory='A tua função é criar uma base de dados. Não resumes nada. Copias o Título, a URL, a Data e um excerto técnico. Preferes excesso de informação a falta dela.',
    verbose=True,
    memory=True,
    tools=[search_tool],
    allow_delegation=False
)

# O Jornalista rigoroso
writer = Agent(
    role='Editor de Newsletter Técnica',
    goal='Criar um relatório onde CADA afirmação tem uma fonte clicável.',
    backstory='Odeias textos vagos. Se escreves sobre uma "nova feature", tens de colocar o link para o GitHub ou Release Note. O teu formato é denso mas rico em referências.',
    verbose=True,
    memory=True,
    allow_delegation=False
)

# O Auditor (Para garantir que os links estão lá)
auditor = Agent(
    role='Auditor de Fontes',
    goal='Garantir que o email não sai sem links e datas.',
    backstory='És um robô de validação. Se o texto não tiver links [Fonte](url), bloqueias. Se tiver "palha" motivacional, mandas cortar. Só aprovas factos.',
    verbose=True,
    memory=True,
    tools=[email_tool],
    allow_delegation=False
)

# --- 4. TAREFAS (COM FORMATAÇÃO FORÇADA) ---

task_search = Task(
    description=(
        f"Realiza uma pesquisa exaustiva sobre 'Kubernetes Releases', 'Kubernetes CVE {data_hoje.year}', 'Agentic AI Frameworks' e 'LLM Agents Tools'.\n"
        f"Janela de tempo: {periodo_str}.\n"
        "Coleta no mínimo 6 a 8 itens relevantes. Para cada item, guarda: Título, URL Oficial, Data e Resumo Técnico."
    ),
    expected_output='Uma lista crua com URLs e dados técnicos.',
    agent=researcher
)

task_write = Task(
    description=(
        "Escreve a newsletter final em Markdown.\n"
        "REGRAS RÍGIDAS DE FORMATO:\n"
        "1. Usa este formato para cada notícia:\n"
        "   - **Título da Notícia** (Data: DD/MM)\n"
        "   - Resumo de 2 linhas explicando o impacto técnico.\n"
        "   - [Ler Fonte Oficial](URL_AQUI) <--- OBRIGATÓRIO\n\n"
        "2. Agrupa por categorias: 'Kubernetes & Cloud Native' e 'Ecossistema Agentic AI'.\n"
        "3. Se não houver data exata, marca como (Recente).\n"
        "4. NÃO expliques o que é Kubernetes. O leitor já sabe."
    ),
    expected_output='Newsletter formatada em Markdown com links funcionais.',
    agent=writer,
    context=[task_search]
)

task_audit_and_send = Task(
    description=(
        "Verifica se o texto do Editor tem LINKS para todas as notícias. "
        "Se o texto parecer 'vazio' ou genérico, reescreve a secção problemática mantendo os links. "
        "Se estiver bom, envia usando a ferramenta de email."
    ),
    expected_output='Email enviado.',
    agent=auditor,
    context=[task_write]
)

# --- 5. EXECUÇÃO ---
crew = Crew(
    agents=[researcher, writer, auditor],
    tasks=[task_search, task_write, task_audit_and_send],
    process=Process.sequential
)

print(f"### A INICIAR NEWSLETTER V5 (MODE: FONTE OBRIGATÓRIA) ###")
result = crew.kickoff()
print("########################\nTERMINADO\n########################")
