from crewai import Task

class NewsTasks:
    def search_task(self, agent, periodo):
        return Task(
            description=(
                f"Coleta dados recentes sobre Kubernetes e AI ({periodo}):\n\n"
                
                f"1. **BLOGS TÉCNICOS (RSS)**:\n"
                f"   - Kubernetes Blog: 'https://kubernetes.io/feed.xml'\n"
                f"   - CNCF Blog: 'https://www.cncf.io/feed/'\n"
                f"   - Hugging Face Blog: 'https://huggingface.co/blog/feed.xml'\n\n"
                
                f"2. **ARTIGOS COMUNIDADE (Dev.to)**:\n"
                f"   - Tags: 'kubernetes, artificial-intelligence, devops'\n\n"
                
                f"OUTPUT ESPERADO: Lista COMPLETA de TODOS os dados coletados (antes de filtrar).\n"
                f"Inclui título, link, resumo/descrição, e fonte de cada notícia."
            ),
            expected_output="Lista de todas as notícias coletadas (dados brutos).",
            agent=agent
        )

    def analyze_task(self, agent, context):
        return Task(
            description=(
                "Analisa CRITICAMENTE CADA notícia coletada e retorna dados estruturados:\n\n"
                
                "PARA CADA NOTÍCIA:\n"
                "1. Lê título + descrição/resumo\n"
                "2. Avalia impacto numa escala 1-10\n"
                "3. Resume o impacto em 1-2 frases (usa Summarizer tool se texto > 200 chars)\n"
                "4. Aprova (Score >= 7) ou rejeita (Score < 7)\n\n"
                
                "CRITÉRIOS DE SCORE ALTO (7-10):\n"
                "- Breaking news ou anúncios importantes\n"
                "- Mudanças arquitectónicas/paradigma\n"
                "- Novas features com real value\n"
                "- Trends emergentes\n\n"
                
                "CRITÉRIOS DE REJEIÇÃO (< 7):\n"
                "- Releases triviais (bug fixes normais)\n"
                "- Marketing/promotional content\n"
                "- Tutoriais básicos ou duplicados\n"
                "- Anúncios de eventos sem valor técnico\n\n"
                
                "OUTPUT OBRIGATÓRIO (para CADA notícia aprovada):\n"
                "Title: [título]\n"
                "Link: [url]\n"
                "Impact: [resumo 1-2 frases do impacto]\n"
                "Score: [7-10]\n"
                "Source: [fonte da notícia]\n"
                "Reason: [porquê merecia este score]\n"
                "---"
            ),
            expected_output="Notícias estruturadas APENAS as com Score >= 7, com título, link, impacto, score, fonte e justificação.",
            agent=agent,
            context=context
        )

    def write_task(self, agent, context):
        return Task(
            description=(
                "Transforma as notícias estruturadas num relatório MARKDOWN legível.\n\n"
                
                "FORMATO OBRIGATÓRIO (mantém exatamente este padrão):\n"
                "# Relatório de Notícias de Impacto\n\n"
                "## [NOME FONTE]\n"
                "### [Fonte Sub-categoria]\n\n"
                "1. [Título]\n"
                "   - Link: [url]\n"
                "   - Impacto: [resumo do impacto]\n"
                "   - Score: [X]\n\n"
                
                "INSTRUÇÕES:\n"
                "- Agrupa notícias por FONTE (Kubernetes Blog, CNCF Blog, etc)\n"
                "- Para cada notícia: Título → Link → Impacto → Score\n"
                "- Mantém ordem de scores (maior para menor)\n"
                "- Título DEVE ser uma frase clara, não vaga\n"
                "- Se sem notícias aprovadas, escreve: 'Sem atualizações de impacto neste período'"
            ),
            expected_output='Relatório Markdown formatado, agrupado por fonte, com título, link, impacto e score.',
            agent=agent,
            context=context
        )