from crewai import Task

class NewsTasks:
    def search_task(self, agent, periodo):
        return Task(
            description=(
                f"Usa as tuas ferramentas de API para coletar dados recentes ({periodo}):\n\n"
                
                f"1. **BLOGS TÉCNICOS** (Usa RSSFeedTool):\n"
                f"   - Kubernetes Blog: 'https://kubernetes.io/feed.xml'\n"
                f"   - CNCF Blog: 'https://www.cncf.io/feed/'\n"
                f"   - Hugging Face Blog: 'https://huggingface.co/blog/feed.xml'\n\n"
                
                f"2. **ARTIGOS COMUNIDADE** (Usa DevToTool):\n"
                f"   - Tags: 'kubernetes, artificial-intelligence, devops'\n\n"
                
                f"OUTPUT ESPERADO: Uma lista crua com todos os dados coletados das 2 fontes."
            ),
            expected_output="Lista de dados brutos (RSS text) das APIs.",
            agent=agent
        )

    def analyze_task(self, agent, context):
        return Task(
            description=(
                "Analisa CRITICAMENTE as notícias coletadas e filtra por impacto real:\n\n"
                "1. Lê cada notícia/artigo\n"
                "2. Avalia impacto numa escala 1-10 (Score)\n"
                "3. Aprova só as com Score >= 7\n\n"
                "Critérios de impacto ALTO:\n"
                "- Breaking news ou anúncios importantes\n"
                "- Mudanças arquitectónicas ou de paradigma\n"
                "- Novas features/APIs com real value\n"
                "- Trends emergentes na indústria\n\n"
                "Critérios de impacto BAIXO (REJEITA):\n"
                "- Releases triviais sem mudanças significativas\n"
                "- Artigos de marketing ou promocionais\n"
                "- Tutoriais básicos ou duplicados\n"
                "- Anúncios de eventos sem conteúdo técnico\n\n"
                "OUTPUT: Lista FILTRADA (só as boas) com justificação do score."
            ),
            expected_output="Notícias filtradas por impacto, com scores e justificação.",
            agent=agent,
            context=context
        )

    def write_task(self, agent, context):
        return Task(
            description="Transforma as notícias FILTRADAS e analisadas num relatório legível em Markdown. Agrupa por fonte e destaca o impacto.",
            expected_output='Relatório Markdown de notícias de impacto.',
            agent=agent,
            context=context
        )