from crewai import Task

class NewsTasks:
    def search_task(self, agent, periodo):
        return Task(
            description=(
        f"Search for CONCRETE NEWS (last 14 days) on:\n"
        f"1. **Kubernetes**: GitHub releases, security updates (CVE), new features, breaking changes, "
        f"networking tools (Cilium, eBPF), Gateway API updates, storage/security announcements\n"
        f"2. **AI Agents**: Framework releases (LangChain, CrewAI, AutoGen, Claude SDK), "
        f"model releases (HuggingFace), security updates, deployment patterns, enterprise adoption\n"
        f"\n"
        f"RULES:\n"
        f"- Focus on ANNOUNCEMENTS, RELEASES, SECURITY UPDATES - not tutorials\n"
        f"- Scrape full articles when possible\n"
        f"- Skip: Opinion pieces, paywalls, outdated content, generic 'how-to' posts\n"
        f"- Prefer: GitHub releases, HuggingFace announcements, official security advisories, "
        f"tech news aggregators (DevOps.com, InfoQ, The Register)\n"
        f"- DEDUPLICATION: Se encontrares a mesma notícia em múltiplas fontes, "
        f"guarda apenas a FONTE OFICIAL (GitHub > Official Blog > Tech News). Ignore duplicatas."
    ),
    expected_output=(
        "Structured list (deduplicated, NEWS ONLY):\n"
        "## Kubernetes News (2-3 UNIQUE concrete items)\n"
        "- Title | Source | What changed | Why it matters\n\n"
        "## AI Agents News (2-3 UNIQUE concrete items)\n"
        "- Title | Source | What changed | Why it matters\n\n"
        "Note: Each item is a REAL announcement/release/update, not documentation"
    ),
    agent=researcher,
    tools=[search_tool, scrape_tool]
        )

    def write_task(self, agent, context):
        return Task(
            description=(
                "Escreve o relatório final com esta estrutura EXATA:\n"
                "# 🐳 Atualizações Kubernetes\n"
                "- **Título da Notícia**: [Link](url_completo) - O QUE mudou e PORQUE importa (1-2 frases técnicas)\n"
                "- **Título da Notícia**: [Link](url_completo) - O QUE mudou e PORQUE importa (1-2 frases técnicas)\n\n"
                "# 🤖 O Mundo dos Agentes AI\n"
                "- **Título da Notícia**: [Link](url_completo) - O QUE mudou e PORQUE importa (1-2 frases técnicas)\n"
                "- **Título da Notícia**: [Link](url_completo) - O QUE mudou e PORQUE importa (1-2 frases técnicas)\n"
                "\nRegras: \n"
                "1. CADA notícia deve ter 50-100 palavras explicando 'O QUE' e 'PORQUE IMPORTA'\n"
                "2. TODOS os links devem ser URLs completos e verificados\n"
                "3. Não uses links 'genéricos' - devem apontar exatamente para a notícia/release"
            ),
            expected_output='Newsletter completa em Markdown com links diretos às notícias (formato: [Título](https://...)).',
            agent=writer,
            context=[task_search]
        )

    def audit_task(self, agent, context):
        return Task(
            description=(
                "Valida:\n"
                "1. Existem as 2 secções (K8s e AI)? SIM/NÃO\n"
                "2. Cada item tem [Link](url) em formato Markdown válido? SIM/NÃO\n"
                "3. Cada item explica O QUE mudou e PORQUE importa? SIM/NÃO\n"
                "4. Não há duplicatas entre secções? SIM/NÃO\n"
                "5. Todos os links são URLs diretos (não genéricos)? SIM/NÃO\n"
                "\nSe TODOS forem SIM: envia o email.\n"
                "Se ALGUM for NÃO: rejeita e explica qual falhou (não tentes 'consertar', apenas rejeita)."
    ),
    expected_output='Email enviado com conteúdo validado OU erro explicado (sem tentar corrigir).',
    agent=auditor,
    context=[task_write]
        )