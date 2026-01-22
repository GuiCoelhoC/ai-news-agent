# 📰 AI News Agent - Persistência de Notícias

## O que foi adicionado?

### 1. **NewsDatabase.py** (`src/tools/NewsDatabase.py`)
Sistema de persistência que evita duplicatas de notícias.

**Funcionalidades:**
- ✅ Armazena notícias em `data/processed_news.json`
- ✅ Detecta duplicatas por hash (título + URL)
- ✅ Rastreia data de processamento
- ✅ Calcula score de cada notícia
- ✅ Limpa notícias antigas (> 90 dias)
- ✅ Fornece estatísticas por fonte

**Métodos principais:**
```python
from src.tools.NewsDatabase import NewsDatabase

db = NewsDatabase()

# Verificar se é duplicata
is_dup = db.is_duplicate("Título", "https://exemplo.com")

# Adicionar notícia
db.add_news(title="...", url="...", source="RSS", score=8)

# Obter estatísticas
stats = db.get_stats()

# Limpar antigas
removed = db.cleanup_old_entries(days=90)
```

### 2. **NewsProcessor.py** (`src/utils/NewsProcessor.py`)
Orquestra o processamento de notícias com persistência.

**Funcionalidades:**
- Integra `NewsDatabase`
- Registra notícias aprovadas
- Fornece estatísticas do pipeline

### 3. **Integração em main.py**
O `run()` agora:
1. Coleta notícias via API
2. Analisa e filtra (score >= 7)
3. **Escreve relatório**
4. **Limpa notícias antigas** (> 90 dias)
5. **Registra processamento no BD**
6. Guarda logs
7. Envia email

### 4. **inspect_database.py** (Script Utilitário)
Ferramenta para ver estatísticas do BD.

```bash
python inspect_database.py
```

Exemplo de output:
```
============================================================
📊 ESTATÍSTICAS DO BANCO DE DADOS DE NOTÍCIAS
============================================================

📝 Total de notícias processadas: 42
🕐 Última atualização: 2026-01-22T15:30:45.123456

📍 Distribuição por fonte:
   - RSS: 25 notícias
   - DEV.TO: 17 notícias

📰 Últimas 5 notícias processadas:
   1. Kubernetes 1.40 Released with New Security Features...
   ...
```

---

## Estrutura de Dados

### `data/processed_news.json`
```json
{
  "processed_news": [
    {
      "title": "Notícia...",
      "url": "https://...",
      "source": "RSS",
      "score": 8,
      "processed_date": "2026-01-22T15:30:45.123456",
      "hash": "abc123def456..."
    }
  ],
  "metadata": {
    "last_update": "2026-01-22T15:30:45.123456"
  }
}
```

---

## Próximos Passos

### ⏰ Agendamento Automático
Para executar semanalmente:

```bash
pip install schedule
```

Adicionar ao `main.py`:
```python
import schedule
import time

schedule.every().monday.at("09:00").do(run)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 🐳 Docker (Para Deployment)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

### 📊 Melhorias Futuras
- [ ] Banco de dados SQLite (mais escalável)
- [ ] Dashboard web para visualizar notícias
- [ ] Enviar apenas notícias novas no email
- [ ] Sistema de preferências do utilizador
- [ ] API REST para queriar notícias

---

## Como Testar?

1. **Executar o pipeline:**
   ```bash
   python main.py
   ```

2. **Verificar BD:**
   ```bash
   python inspect_database.py
   ```

3. **Executar novamente:**
   ```bash
   python main.py
   ```
   
   Verá que notícias duplicadas são ignoradas (se URLs/títulos forem iguais).

