import os
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from crewai.tools import BaseTool

class EmailTool(BaseTool):
    name: str = "Ferramenta de Envio de Email"
    description: str = "Envia o corpo do texto (formatado em HTML) para a lista de distribuição."

    def _run(self, body: str) -> str:
        sender_email = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("EMAIL_PASSWORD")
        receivers_str = os.getenv("EMAIL_RECEIVERS")
        
        if not all([sender_email, sender_password, receivers_str]):
            return "Erro: Faltam variáveis de ambiente."

        receivers_list = [email.strip() for email in receivers_str.split(',')]
        html_content = markdown.markdown(body)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email 
        msg['Subject'] = f"Relatório Híbrido: K8s + AI Agents ({datetime.now().strftime('%d/%m')})"

        html_body = f"""
        <html>
          <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto;">
            <div style="background-color: #2c3e50; padding: 20px; text-align: center;">
              <h2 style="color: #ffffff; margin: 0;">🧠 HomeLab Intelligence</h2>
            </div>
            <div style="padding: 30px; border: 1px solid #ddd;">
              {html_content} 
            </div>
            <div style="text-align: center; padding-top: 20px; font-size: 12px; color: #999;">
              <p>Fontes verificadas. Paywalls ignorados.</p>
            </div>
          </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receivers_list, msg.as_string())
            server.quit()
            return f"Email enviado para {len(receivers_list)} destinatários."
        except Exception as e:
            return f"Erro SMTP: {str(e)}"