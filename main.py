import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents.news_agents import NewsAgents
from src.tasks.news_tasks import NewsTasks
from src.tools.email_tool import EmailTool

load_dotenv()

def parse_analyst_output(output_text: str) -> int:
    """
    Extrai estatísticas do output do analyst.
    Retorna: total_notícias aprovadas
    """
    # Conta quantas notícias foram aprovadas (padrão: "Score: [7-10]")
    approved_pattern = r'Score:\s*([7-9]|10)'
    approved_matches = re.findall(approved_pattern, output_text)
    total_approved = len(approved_matches)
    
    return total_approved

def save_log(content: str):
    """Guarda o output do último run num ficheiro log"""
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/run_{timestamp}.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n📝 Log guardado em: {log_file}")
    return log_file

def run():
    data_hoje = datetime.now()
    data_inicio = data_hoje - timedelta(days=7)
    periodo_str = f"{data_inicio.strftime('%Y-%m-%d')} a {data_hoje.strftime('%Y-%m-%d')}"

    print(f"🚀 A INICIAR MOTOR DE INGESTÃO DE DADOS")
    print(f"📅 Período de Análise: {periodo_str}")
    print("=" * 60)

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

    print("\n⏳ Executando pipeline...\n")
    result = crew.kickoff()
    
    # Converter CrewOutput para string
    result_str = str(result.raw_output) if hasattr(result, 'raw_output') else str(result)
    
    # Extrai estatísticas do analyst
    total_approved = parse_analyst_output(result_str)
    
    # --- 6. GUARDAR LOG ---
    log_file = save_log(result_str)
    
    # --- 7. ENVIO DE EMAIL (código direto, não agent) ---
    email_tool = EmailTool()
    email_result = email_tool._run(result_str)
    
    # --- 8. PRINT STATS ---
    stats = f"""
╔══════════════════════════════════════╗
║        📊 EXECUÇÃO TERMINADA         ║
╚══════════════════════════════════════╝

✅ Notícias aprovadas (Score >= 7): {total_approved}
📝 Log: {log_file}
📧 Email: {email_result}

{'─' * 60}
RESULTADO DO PIPELINE:
{'─' * 60}
"""
    
    print(stats)
    print(result_str)

if __name__ == "__main__":
    run()
            url=news['url'],
            source=news['source'],
            score=8  # Score 8 = aprovada pela crew
        )
        if was_registered:
            new_news_count += 1
            print(f"  ✅ Nova: {news['title'][:60]}...")
        else:
            duplicate_count += 1
            print(f"  ⏭️  Duplicada: {news['title'][:60]}...")
    
    # Limpar notícias antigas (> 90 dias)
    removed = news_processor.cleanup_old(days=90)
    if removed > 0:
        print(f"\n🗑️  {removed} notícias antigas removidas do banco de dados")
    
    # Estatísticas do banco de dados
    print(f"\n📊 Estatísticas do Banco de Dados:")
    db_stats = news_processor.get_database_stats()
    print(f"   Total de notícias processadas: {db_stats['total_processed']}")
    print(f"   Novas neste run: {new_news_count}")
    print(f"   Duplicatas neste run: {duplicate_count}")
    print(f"   Última atualização: {db_stats['last_update']}")
    print(f"   Por fonte: {db_stats['by_source']}")
    
    # --- 7. GUARDAR LOG ---
    log_file = save_log(result_str)
    
    # --- 8. ENVIO DE EMAIL (código direto, não agent) ---
    email_tool = EmailTool()
    email_result = email_tool._run(result_str)
    
    print("\n\n########################")
    print("✅ EXECUÇÃO TERMINADA COM SUCESSO")
    print("########################\n")
    print(result_str)
    print("\n📧 " + email_result)

if __name__ == "__main__":
    run()