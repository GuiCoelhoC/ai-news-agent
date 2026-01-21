import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents.news_agents import NewsAgents
from src.tasks.news_tasks import NewsTasks
from src.tools.email_tool import EmailTool

load_dotenv()

def run():
    data_hoje = datetime.now()
    data_inicio = data_hoje - timedelta(days=7)
    periodo_str = f"{data_inicio.strftime('%Y-%m-%d')} a {data_hoje.strftime('%Y-%m-%d')}"

    print(f"A INICIAR MOTOR DE INGESTÃO DE DADOS")
    print(f"Período de Análise: {periodo_str}")

    # --- 2. INSTANCIAR FÁBRICAS ---
    agents = NewsAgents()
    tasks = NewsTasks()

    # --- 3. CRIAR AGENTES (EQUIPA) ---
    data_engineer = agents.researcher(periodo_str) 
    analyst = agents.analyst()
    editor = agents.writer()

    # --- 4. CRIAR TAREFAS (WORKFLOW) ---
    # Passo 1: Coletar dados brutos das APIs (RSS, Dev.to)
    task_collect = tasks.search_task(data_engineer, periodo_str)

    # Passo 2: Analisar e filtrar por impacto
    task_analyze = tasks.analyze_task(analyst, context=[task_collect])

    # Passo 3: Escrever o relatório baseado SÓ nas notícias aprovadas
    task_write = tasks.write_task(editor, context=[task_analyze])

    # --- 5. EXECUÇÃO DA CREW ---
    crew = Crew(
        agents=[data_engineer, analyst, editor],
        tasks=[task_collect, task_analyze, task_write],
        process=Process.sequential, # Sequencial: Coleta -> Análise -> Escrita
        memory=True,                # Ativa a persistência para evitar repetições
        verbose=True                # Logs no terminal
    )

    result = crew.kickoff()
    
    # --- 6. ENVIO DE EMAIL (código direto, não agent) ---
    email_tool = EmailTool()
    email_result = email_tool._run(result)
    
    print("\n\n########################")
    print("✅ EXECUÇÃO TERMINADA COM SUCESSO")
    print("########################\n")
    print(result)
    print("\n📧 " + email_result)

if __name__ == "__main__":
    run()