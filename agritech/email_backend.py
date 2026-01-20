"""
Backend email personnalisé pour Brevo (Sendinblue) API
"""
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


class BrevoEmailBackend(BaseEmailBackend):
    """
    Backend email utilisant l'API Brevo (Sendinblue)
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configuration de l'API Brevo
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
    
    def send_messages(self, email_messages):
        """
        Envoie une liste de messages email via l'API Brevo
        """
        if not email_messages:
            return 0
        
        num_sent = 0
        for message in email_messages:
            try:
                # Préparer l'email au format Brevo
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=[{"email": recipient} for recipient in message.to],
                    sender={
                        "email": message.from_email or settings.DEFAULT_FROM_EMAIL,
                        "name": "AgriTech-Bénin"
                    },
                    subject=message.subject,
                    html_content=message.body if message.content_subtype == 'html' else None,
                    text_content=message.body if message.content_subtype == 'plain' else None,
                )
                
                # Envoyer l'email
                api_response = self.api_instance.send_transac_email(send_smtp_email)
                
                if api_response:
                    num_sent += 1
                    
            except ApiException as e:
                if not self.fail_silently:
                    raise
                    
        return num_sent