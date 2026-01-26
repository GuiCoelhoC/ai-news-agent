import requests
from crewai.tools import BaseTool

class ValidatorTool(BaseTool):
    name: str = "Link Validator"
    description: str = "Valida se um URL funciona e é acessível. Retorna status do link."

    def _run(self, url: str) -> str:
        """
        Valida se um link é acessível.
        
        Args:
            url: URL a validar
        
        Returns:
            Status do link (válido ou inválido)
        """
        if not url:
            return "❌ URL vazia"
        
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return f"✅ Link válido (HTTP {response.status_code})"
            else:
                return f"⚠️ Link retorna HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return "❌ Link timeout (resposta muito lenta)"
        except requests.exceptions.ConnectionError:
            return "❌ Link inacessível (erro de conexão)"
        except Exception as e:
            return f"⚠️ Erro ao validar: {str(e)[:50]}"
