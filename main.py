import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents.news_agents import NewsAgents
from src.tasks.news_tasks import NewsTasks
from src.tools.email_tool import EmailTool
from src.utils.NewsProcessor import NewsProcessor
from src.utils.NewsParser import NewsParser

load_dotenv()

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
    
    # Converter CrewOutput para string
    result_str = str(result.raw_output) if hasattr(result, 'raw_output') else str(result)
    
    # --- 6. PERSISTÊNCIA DE NOTÍCIAS ---
    news_processor = NewsProcessor()
    parser = NewsParser()
    
    # Parse e extração de notícias do output da crew
    extracted_news = parser.parse_crew_output(result_str)
    extracted_news = parser.filter_by_length(extracted_news, min_title_length=10)
    
    print(f"\n📡 Notícias extraídas: {len(extracted_news)}")
    
    # Registar cada notícia aprovada no banco de dados
    new_news_count = 0
    duplicate_count = 0
    
    for news in extracted_news:
        was_registered = news_processor.register_approved_news(
            title=news['title'],
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