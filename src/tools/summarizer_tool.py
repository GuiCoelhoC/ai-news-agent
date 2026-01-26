import re
from crewai.tools import BaseTool

class SummarizerTool(BaseTool):
    name: str = "Text Summarizer"
    description: str = "Resume um texto longo para 1-2 frases mantendo a essência. Usa para textos acima de 200 caracteres."

    def _run(self, text: str, max_length: int = 200) -> str:
        """
        Resume texto de forma inteligente.
        
        Args:
            text: Texto a resumir
            max_length: Tamanho máximo do resumo (default 200 chars)
        
        Returns:
            Texto resumido
        """
        if not text or len(text.strip()) < 50:
            return text.strip()
        
        # Se já é pequeno, retorna como está
        if len(text) <= max_length:
            return text.strip()
        
        # Remove espaços extra e quebras de linha
        text = ' '.join(text.split())
        
        # Tenta cortar na primeira frase completa após max_length
        sentences = re.split(r'(?<=[.!?])\s+', text)
        result = ""
        
        for sentence in sentences:
            if len(result) + len(sentence) <= max_length:
                result += sentence + " "
            else:
                # Se a primeira frase é muito grande, corta no meio
                if not result:
                    result = text[:max_length] + "..."
                break
        
        return result.strip()
