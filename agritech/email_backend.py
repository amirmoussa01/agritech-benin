import sib_api_v3_sdk
import logging
import re
from sib_api_v3_sdk.rest import ApiException
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)

class BrevoEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not getattr(settings, 'BREVO_API_KEY', None):
            logger.error("❌ BREVO_API_KEY manquante")
            return
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    def send_messages(self, email_messages):
        if not email_messages: return 0
        num_sent = 0
        for message in email_messages:
            try:
                to_list = [{"email": r} for r in message.to]
                from_email = message.from_email or settings.DEFAULT_FROM_EMAIL
                
                # Parsing propre du nom de l'expéditeur
                name, email = "AgriTech-Bénin", from_email
                if '<' in from_email:
                    match = re.match(r'(.*?)<(.+?)>', from_email)
                    if match:
                        name, email = match.group(1).strip(), match.group(2).strip()

                # Détection du contenu (HTML ou Plain)
                content_type = getattr(message, 'content_subtype', 'plain')
                html_body = message.body if content_type == 'html' else message.body.replace('\n', '<br>')

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to_list,
                    sender={"name": name, "email": email},
                    subject=message.subject,
                    html_content=html_body # On envoie directement le corps sans wrapper inutile
                )

                api_response = self.api_instance.send_transac_email(send_smtp_email)
                if api_response.message_id:
                    num_sent += 1
            except Exception as e:
                logger.error(f"❌ Erreur envoi: {e}")
                if not self.fail_silently: raise
        return num_sent