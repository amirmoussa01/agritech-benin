from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import logging
import re

logger = logging.getLogger(__name__)

class BrevoEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not getattr(settings, 'BREVO_API_KEY', None):
            return
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        api_client = sib_api_v3_sdk.ApiClient(configuration)
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        num_sent = 0
        for message in email_messages:
            try:
                # 1. Destinataires
                to_list = [{"email": recipient} for recipient in message.to]
                
                # 2. Gestion de l'expéditeur (Parser Nom <email>)
                from_email = message.from_email or settings.DEFAULT_FROM_EMAIL
                sender_name = "AgriTech-Bénin"
                sender_email = from_email
                
                if '<' in from_email and '>' in from_email:
                    match = re.match(r'(.*?)<(.+?)>', from_email)
                    if match:
                        sender_name = match.group(1).strip()
                        sender_email = match.group(2).strip()

                # 3. Détection intelligente du contenu
                body = message.body.strip()
                
                # Correction de la détection (html au lieu de mtml)
                if body.startswith('<html') or body.startswith('<!DOCTYPE') or body.startswith('<table'):
                    html_content = body
                else:
                    # Conversion texte brut vers HTML propre
                    html_content = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            {body.replace(chr(10), '<br>')}
                        </div>
                    </body>
                    </html>
                    """

                # 4. Création de l'objet Brevo
                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to_list,
                    sender={"name": sender_name, "email": sender_email},
                    subject=message.subject,
                    html_content=html_content,
                )

                # 5. Envoi via API
                api_response = self.api_instance.send_transac_email(send_smtp_email)
                if api_response and api_response.message_id:
                    num_sent += 1
                    
            except Exception as e:
                logger.error(f"❌ Erreur backend Brevo: {e}")
                if not self.fail_silently:
                    raise
        return num_sent
    
"""
Backend email personnalisé pour Brevo (Sendinblue) API
Fichier : agritech/email_backend.py
"""
# from django.core.mail.backends.base import BaseEmailBackend
# from django.conf import settings
# import sib_api_v3_sdk
# from sib_api_v3_sdk.rest import ApiException
# import logging

# logger = logging.getLogger(__name__)


# class BrevoEmailBackend(BaseEmailBackend):
#     """Backend email utilisant l'API Brevo"""
#     
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         
#         if not settings.BREVO_API_KEY:
#             logger.error("❌ BREVO_API_KEY non définie")
#             print("❌ BREVO_API_KEY non définie dans settings.py")
#             return
#             
#         # Configuration API Brevo
#         configuration = sib_api_v3_sdk.Configuration()
#         configuration.api_key['api-key'] = settings.BREVO_API_KEY
#         
#         api_client = sib_api_v3_sdk.ApiClient(configuration)
#         self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)
#         
#         print("✅ Backend Brevo initialisé")
#         logger.info("✅ Backend Brevo initialisé")
#     
#     def send_messages(self, email_messages):
#         """Envoie les emails via Brevo API"""
#         if not email_messages:
#             return 0
#         
#         if not settings.BREVO_API_KEY:
#             logger.error("❌ Clé API Brevo manquante")
#             return 0
#         
#         num_sent = 0
#         for message in email_messages:
#             try:
#                 # Destinataires
#                 to_list = [{"email": recipient} for recipient in message.to]
#                 
#                 # Expéditeur - extraire le nom si présent
#                 from_email = message.from_email or settings.DEFAULT_FROM_EMAIL
#                 
#                 # Si le format est "Nom <email@example.com>", on le sépare
#                 if '<' in from_email and '>' in from_email:
#                     import re
#                     match = re.match(r'(.*?)<(.+?)>', from_email)
#                     if match:
#                         sender_name = match.group(1).strip()
#                         sender_email = match.group(2).strip()
#                     else:
#                         sender_name = "AgriTech-Bénin"
#                         sender_email = from_email
#                 else:
#                     sender_name = "AgriTech-Bénin"
#                     sender_email = from_email
#                 
#                 sender = {
#                     "name": sender_name,
#                     "email": sender_email
#                 }
#                 
#                 # Contenu HTML ou texte
#                 is_html = getattr(message, 'content_subtype', 'plain') == 'html'
#                 
#                 if is_html:
#                     html_content = message.body
#                 else:
#                     # Convertir texte en HTML simple
#                     html_content = f"""
#                     <html>
#                     <head><meta charset="UTF-8"></head>
#                     <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
#                         <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
#                             {message.body.replace(chr(10), '<br>')}
#                         </div>
#                     </body>
#                     </html>
#                     """
#                 
#                 # Créer l'email Brevo
#                 send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
#                     to=to_list,
#                     sender=sender,
#                     subject=message.subject,
#                     html_content=html_content,
#                 )
#                 
#                 # Logs
#                 print(f"\n📧 Envoi email Brevo:")
#                 print(f"   De: {sender['email']}")
#                 print(f"   À: {message.to}")
#                 print(f"   Sujet: {message.subject}")
#                 
#                 # Envoi
#                 api_response = self.api_instance.send_transac_email(send_smtp_email)
#                 
#                 if api_response and api_response.message_id:
#                     num_sent += 1
#                     print(f"✅ Email envoyé - ID: {api_response.message_id}")
#                     logger.info(f"✅ Email envoyé - ID: {api_response.message_id}")
#                 else:
#                     print(f"⚠️ Réponse inattendue: {api_response}")
#                     logger.warning(f"⚠️ Réponse inattendue: {api_response}")
#                     
#             except ApiException as e:
#                 print(f"\n❌ Erreur API Brevo:")
#                 print(f"   Status: {e.status}")
#                 print(f"   Raison: {e.reason}")
#                 logger.error(f"❌ Erreur Brevo: {e.status} - {e.reason}")
#                 
#                 if not self.fail_silently:
#                     raise
#                     
#             except Exception as e:
#                 print(f"\n❌ Erreur: {type(e).__name__}: {e}")
#                 logger.error(f"❌ Erreur: {e}")
#                 
#                 if not self.fail_silently:
#                     raise
#         
#         print(f"\n📊 Total: {num_sent}/{len(email_messages)} emails envoyés\n")
#         return num_sent
