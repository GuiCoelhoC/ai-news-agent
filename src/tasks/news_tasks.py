from crewai import Task

class NewsTasks:
    def search_task(self, agent, periodo):
        return Task(
            description=(
                f"Usa as tuas ferramentas de API para coletar dados recentes ({periodo}):\n\n"
                
                f"1. **GITHUB RELEASES** (Usa GitHubTool):\n"
                f"   - Repos: 'kubernetes/kubernetes, cilium/cilium, langchain-ai/langchain, crewAIInc/crewAI'\n\n"
                
                f"2. **BLOGS TÉCNICOS** (Usa RSSFeedTool):\n"
                f"   - Kubernetes Blog: 'https://kubernetes.io/feed.xml'\n"
                f"   - CNCF Blog: 'https://www.cncf.io/feed/'\n"
                f"   - Hugging Face Blog: 'https://huggingface.co/blog/feed.xml'\n\n"
                
                f"3. **ARTIGOS COMUNIDADE** (Usa DevToTool):\n"
                f"   - Tags: 'kubernetes, artificial-intelligence, devops'\n\n"
                
                f"OUTPUT ESPERADO: Uma lista crua com todos os dados coletados das 3 fontes."
            ),
            expected_output="Lista de dados brutos (JSON/RSS text) das APIs.",
            agent=agent
        )

    # ... (As tarefas write_task e audit_task mantêm-se iguais) ...
    def write_task(self, agent, context):
        return Task(
            description="Transforma os dados brutos das APIs num relatório legível em Markdown. Agrupa por 'Oficial' (GitHub/RSS) e 'Comunidade' (Dev.to).",
            expected_output='Relatório Markdown.',
            agent=agent,
            context=context
        )
    
    def audit_task(self, agent, context):
         return Task(
            description="Envia o email.",
            expected_output='Email enviado.',
            agent=agent,
            context=context
        )