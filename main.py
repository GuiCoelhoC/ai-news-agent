import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents.news_agents import NewsAgents
from src.tasks.news_tasks import NewsTasks
from src.tools.email_tool import EmailTool
from src.utils.NewsParser import NewsParser
from src.utils.NewsProcessor import NewsProcessor

load_dotenv()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_analyst_output(output_text: str) -> int:
    """Conta notícias aprovadas pelo analyst (Score >= 7)."""
    approved_pattern = r'Score:\s*([7-9]|10)'
    return len(re.findall(approved_pattern, output_text))


def save_log(content: str) -> str:
    """Guarda o output do run num ficheiro de log e devolve o caminho."""
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/run_{timestamp}.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n📝 Log guardado em: {log_file}")
    return log_file


# ---------------------------------------------------------------------------
# Pipeline (CrewAI) — será substituído por LangGraph numa fase futura
# ---------------------------------------------------------------------------

def run_pipeline(periodo_str: str) -> str:
    """
    Executa o pipeline de notícias e devolve o resultado bruto como string.
    Esta função será o ponto de troca quando migrarmos para LangGraph.
    """
    agents = NewsAgents()
    tasks = NewsTasks()

    data_engineer = agents.researcher(periodo_str)
    analyst = agents.analyst()
    editor = agents.writer()

    task_collect = tasks.search_task(data_engineer, periodo_str)
    task_analyze = tasks.analyze_task(analyst, context=[task_collect])
    task_write = tasks.write_task(editor, context=[task_analyze])

    crew = Crew(
        agents=[data_engineer, analyst, editor],
        tasks=[task_collect, task_analyze, task_write],
        process=Process.sequential,
        memory=True,
        verbose=True,
    )

    print("\n⏳ Executando pipeline...\n")
    result = crew.kickoff()
    return str(result.raw_output) if hasattr(result, "raw_output") else str(result)


# ---------------------------------------------------------------------------
# Pós-processamento — independente do motor de pipeline
# ---------------------------------------------------------------------------

def post_process(result_str: str) -> dict:
    """
    Parseia o output do pipeline, persiste notícias novas e devolve estatísticas.
    Esta lógica é agnóstica ao motor (CrewAI ou LangGraph).
    """
    news_parser = NewsParser()
    news_processor = NewsProcessor()

    # Limpar notícias antigas (> 90 dias)
    removed = news_processor.cleanup_old(days=90)
    if removed > 0:
        print(f"🗑️  {removed} notícias antigas removidas")

    # Parsear notícias aprovadas a partir do output
    approved_news = news_parser.parse_crew_output(result_str)
    new_count = 0
    duplicate_count = 0

    print(f"\n📥 A persistir {len(approved_news)} notícias encontradas...")
    for news in approved_news:
        registered = news_processor.register_approved_news(
            title=news["title"],
            url=news["url"],
            source=news["source"],
            score=8,
        )
        if registered:
            new_count += 1
            print(f"  ✅ Nova: {news['title'][:60]}...")
        else:
            duplicate_count += 1
            print(f"  ⏭️  Duplicada: {news['title'][:60]}...")

    db_stats = news_processor.get_database_stats()

    return {
        "total_approved": parse_analyst_output(result_str),
        "new_persisted": new_count,
        "duplicates": duplicate_count,
        "db_total": db_stats["total_processed"],
        "db_last_update": db_stats["last_update"],
        "db_by_source": db_stats["by_source"],
    }


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def run():
    data_hoje = datetime.now()
    data_inicio = data_hoje - timedelta(days=7)
    periodo_str = f"{data_inicio.strftime('%Y-%m-%d')} a {data_hoje.strftime('%Y-%m-%d')}"

    print("🚀 A INICIAR MOTOR DE INGESTÃO DE DADOS")
    print(f"📅 Período de Análise: {periodo_str}")
    print("=" * 60)

    # 1. Executar pipeline
    result_str = run_pipeline(periodo_str)

    # 2. Persistir e obter estatísticas
    stats = post_process(result_str)

    # 3. Guardar log
    log_file = save_log(result_str)

    # 4. Enviar email
    email_tool = EmailTool()
    email_result = email_tool._run(result_str)

    # 5. Sumário final
    print(f"""
╔══════════════════════════════════════╗
║        📊 EXECUÇÃO TERMINADA         ║
╚══════════════════════════════════════╝

✅ Notícias aprovadas (Score >= 7): {stats['total_approved']}
💾 Novas persistidas:              {stats['new_persisted']}
⏭️  Duplicatas ignoradas:           {stats['duplicates']}
📊 Total no banco de dados:        {stats['db_total']}
📝 Log: {log_file}
📧 Email: {email_result}
""")


if __name__ == "__main__":
    run()