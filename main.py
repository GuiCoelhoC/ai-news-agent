import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents.news_agents import NewsAgents
from src.tasks.news_tasks import NewsTasks

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
    editor = agents.writer()
    auditor = agents.auditor()

    # --- 4. CRIAR TAREFAS (WORKFLOW) ---
    # Passo 1: Coletar dados brutos das APIs (GitHub, RSS, Dev.to)
    task_collect = tasks.search_task(data_engineer, periodo_str)

    # Passo 2: Escrever o relatório baseado SÓ no que foi coletado
    # O contexto diz ao CrewAI: "Espera pelo output da task_collect antes de começar"
    task_write = tasks.write_task(editor, context=[task_collect])

    # Passo 3: Validar e Enviar Email
    task_audit = tasks.audit_task(auditor, context=[task_write])

    # --- 5. EXECUÇÃO DA CREW ---
    crew = Crew(
        agents=[data_engineer, editor, auditor],
        tasks=[task_collect, task_write, task_audit],
        process=Process.sequential, # Sequencial é obrigatório aqui (Coleta -> Escrita -> Envio)
        memory=True,                # Ativa a persistência para evitar repetições em execuções futuras
        verbose=True                # Para veres os logs bonitos no terminal
    )

    result = crew.kickoff()
    
    print("\n\n########################")
    print("✅ EXECUÇÃO TERMINADA COM SUCESSO")
    print("########################\n")
    print(result)

if __name__ == "__main__":
    run()