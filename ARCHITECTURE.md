# 🔗 Arquitetura - Como os Ficheiros se Conectam

## Diagrama do Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                         main.py (Orquestrador)                      │
│                     Ponto de entrada do programa                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌─────────────┐ ┌──────────────┐
        │ NewsAgents       │ │ NewsTasks   │ │ EmailTool    │
        │ (3 agentes)      │ │ (workflow)  │ │ (envio)      │
        └──────────────────┘ └─────────────┘ └──────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   Crew (CrewAI Framework)     │
                    │  - Coordena 3 agentes        │
                    │  - Executa 3 tarefas sequencialmente
                    └───────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
    TAREFA 1              TAREFA 2              TAREFA 3
    Researcher            Analyst               Writer
    (Coleta dados)        (Filtra por score)    (Escreve relatório)
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    result_str (texto bruto)
                              │
                              ▼
                    ┌──────────────────────────┐
                    │  NewsProcessor (nova!)   │
                    │  src/utils/NewsProcessor │
                    └──────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
        1. Limpar dados  2. Registar stats  3. Verificar dupes
        antigos (>90d)     do processamento
        cleanup_old()      get_database_stats()
                │
                ▼
        ┌──────────────────────────────┐
        │   NewsDatabase (base!)       │
        │  src/tools/NewsDatabase      │
        │  (Camada de persistência)    │
        └──────────────────────────────┘
                │
        ┌───────┼───────┐
        │       │       │
        ▼       ▼       ▼
    add_news()  is_duplicate()  get_stats()
        │           │               │
        └───────────┼───────────────┘
                    │
                    ▼
        📄 data/processed_news.json
           (Banco de dados em JSON)
```

---

## 📦 Hierarquia de Componentes

### **Camada 1: Interface/Main**
```
main.py
├─ Importa: NewsProcessor, NewsAgents, NewsTasks, EmailTool
├─ Responsabilidade: Orquestrar o fluxo completo
└─ Chama:
   ├─ Crew.kickoff() → executa agentes/tarefas
   └─ NewsProcessor() → gerencia persistência
```

### **Camada 2: Negócio/Orquestração**
```
NewsProcessor (src/utils/NewsProcessor.py)
├─ Importa: NewsDatabase
├─ Responsabilidade: Interface de alto nível
└─ Métodos:
   ├─ process_and_save() → registra run
   ├─ register_approved_news() → add notícia aprovada
   ├─ get_database_stats() → estatísticas
   └─ cleanup_old() → remove antigos
```

### **Camada 3: Dados/Persistência**
```
NewsDatabase (src/tools/NewsDatabase.py)
├─ Responsabilidade: Gerenciar arquivo JSON
└─ Métodos:
   ├─ add_news() → escreve no disco
   ├─ is_duplicate() → valida duplicata
   ├─ get_stats() → estatísticas
   └─ cleanup_old_entries() → limpa dados
```

### **Camada 4: Armazenamento**
```
data/processed_news.json (Arquivo físico)
├─ Estrutura: JSON com lista de notícias
└─ Conteúdo:
   ├─ processed_news[] → array de artigos
   └─ metadata → info de atualização
```

---

## 🔄 Fluxo de Dados Detalhado

### **EXECUÇÃO (main.py → line 52)**
```python
# Step 1: Crew executa tarefas
result = crew.kickoff()
result_str = str(result.raw_output)  # "Notícia X... Notícia Y..."
```

### **PERSISTÊNCIA (main.py → lines 55-71)**
```python
# Step 2: Criar processor (instancia NewsDatabase automaticamente)
news_processor = NewsProcessor()
  │
  └─→ NewsDatabase.__init__()
      │
      └─→ _load() → lê data/processed_news.json do disco
```

### **LIMPEZA (main.py → lines 59-61)**
```python
# Step 3: Remover notícias antigas
removed = news_processor.cleanup_old(days=90)
  │
  └─→ NewsDatabase.cleanup_old_entries(days=90)
      │
      ├─→ Calcula data limite (90 dias atrás)
      ├─→ Filtra processed_news[] que são > 90 dias
      ├─→ _save() → escreve data/processed_news.json
      │
      └─→ Retorna quantidade removida
```

### **REGISTO (main.py → lines 64-70)**
```python
# Step 4: Obter estatísticas
db_stats = news_processor.get_database_stats()
  │
  └─→ NewsDatabase.get_stats()
      │
      ├─→ Conta total de notícias processadas
      ├─→ Lê last_update de metadata
      ├─→ Conta notícias por source (RSS, DEV.TO, etc)
      │
      └─→ Retorna dict com estatísticas
```

---

## 📊 Exemplo de Fluxo Real

### **Cenário: Primeira Execução**

```
TEMPO: Semana 1, Segunda-feira 09:00

1️⃣  main.py executa:
    - Crew coleta 50 artigos (Dev.to, RSS)
    - Analyst filtra e aprova 15 (score >= 7)
    - Writer gera relatório com 15 aprovadas
    - result_str = "Notícia 1...\n Notícia 2...\n..."

2️⃣  NewsProcessor instantaneamente:
    - Cria NewsDatabase()
    - Carrega data/processed_news.json (vazio)

3️⃣  Limpeza (nada para remover):
    - removed = 0
    - Nenhuma notícia com > 90 dias

4️⃣  Registar stats:
    - db_stats = {
        "total_processed": 0,  ← antes
        "last_update": "2026-01-22T09:00:00",
        "by_source": {}
      }

5️⃣  Enviar email com as 15 notícias
    Resultado final: data/processed_news.json ← continua vazio!
    ⚠️  (Notícias ainda não estão persistidas)
```

### **Cenário: Segunda Execução**

```
TEMPO: Semana 2, Segunda-feira 09:00 (7 dias depois)

1️⃣  main.py executa:
    - Crew coleta 60 artigos (some são iguais à semana anterior)
    - Analyst aprova 18 notícias

2️⃣  NewsProcessor instantaneamente:
    - Cria NewsDatabase()
    - Carrega data/processed_news.json (ainda vazio!)

3️⃣  Limpeza:
    - removed = 0 (nada para remover)

4️⃣  Registar stats:
    - db_stats = {
        "total_processed": 0,  ← Continuou vazio!
        "last_update": "2026-01-22T09:00:00"
      }

⚠️  PROBLEMA OBSERVADO:
    As notícias não estão sendo persistidas!
    A NewsDatabase.add_news() nunca é chamada.
```

---

## 🐛 Código que Falta

Atualmente, o fluxo **não salva notícias individuais**. 

### Para completar a persistência, precisa:

```python
# Em main.py, linha 65-70, após obter db_stats:

# Extrair notícias aprovadas do resultado
from src.tools.DataIngestion import DevToTool, RSSFeedTool

# Se tiver um parser de notícias:
approved_news = parse_approved_news(result_str)

# Registar cada uma no BD
for news in approved_news:
    news_processor.register_approved_news(
        title=news['title'],
        url=news['url'],
        source=news['source'],
        score=8  # Foram aprovadas
    )
```

---

## 📋 Resumo das Conexões

| Ficheiro | Responsabilidade | Importa | Salva em |
|----------|------------------|---------|----------|
| `main.py` | Orquestrador | NewsProcessor, NewsAgents, NewsTasks, EmailTool | `logs/` |
| `NewsProcessor` | Interface negócio | NewsDatabase | - (delega) |
| `NewsDatabase` | Gerenciar dados | json, os, datetime | `data/processed_news.json` |
| `data/processed_news.json` | Armazenamento | - | Disco |

---

## 🎯 Próximo Passo

Para completar a persistência, precisa **parsear o output da Crew** e chamar:
```python
news_processor.register_approved_news(title, url, source, score)
```

Quer que eu implemente isso?
