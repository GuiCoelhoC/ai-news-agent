import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew, Process

# Importar as nossas novas classes modulares
from src.agents.news_agents import NewsAgents
from src.tasks.news_tasks import NewsTasks

load_dotenv()

def run():
    # 1. Setup de Datas
    data_hoje = datetime.now()
    data_inicio = data_hoje - timedelta(days=7)
    periodo_str = f"{data_inicio.strftime('%Y-%m-%d')} a {data_hoje.strftime('%Y-%m-%d')}"

    # 2. Instanciar as classes
    agents = NewsAgents()
    tasks = NewsTasks()

    # 3. Criar os Agentes
    researcher = agents.researcher(periodo_str)
    writer = agents.writer()
    auditor = agents.auditor()

    # 4. Criar as Tarefas
    search = tasks.search_task(researcher, periodo_str)
    write = tasks.write_task(writer, [search])
    audit = tasks.audit_task(auditor, [write])

    # 5. Criar e Correr a Crew
    crew = Crew(
        agents=[researcher, writer, auditor],
        tasks=[search, write, audit],
        process=Process.sequential,
        memory=True,
        verbose=True
    )

    print(f"### A INICIAR BUSCA HÍBRIDA MODULAR ###")
    result = crew.kickoff()
    print("########################\nTERMINADO\n########################")

if __name__ == "__main__":
    run()