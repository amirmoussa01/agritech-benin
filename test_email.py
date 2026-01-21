"""
Script de test pour l'envoi d'emails via Brevo
À placer à la RACINE du projet (même niveau que manage.py)

Usage: python test_email.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 70)
print("🧪 TEST D'ENVOI EMAIL - AgriTech-Bénin")
print("=" * 70)

print(f"\n📋 Configuration:")
print(f"   Backend        : {settings.EMAIL_BACKEND}")
print(f"   Clé API Brevo  : {'✅ Présente' if settings.BREVO_API_KEY else '❌ Manquante'}")
print(f"   Email expéditeur: {settings.DEFAULT_FROM_EMAIL}")

if not settings.BREVO_API_KEY:
    print("\n❌ ERREUR: Clé API Brevo manquante dans .env")
    exit(1)

print(f"\n📧 Envoi d'un email de test...")

try:
    result = send_mail(
        subject='✅ Test AgriTech-Bénin',
        message='''Bonjour,

Ceci est un email de test depuis Django.

Si vous recevez cet email, votre configuration Brevo fonctionne parfaitement !

--
AgriTech-Bénin
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['moussaamir979@gmail.com'],
        fail_silently=False,
    )
    
    print("\n" + "=" * 70)
    if result > 0:
        print("✅ SUCCESS ! Email envoyé")
        print("=" * 70)
        print(f"\n📬 Vérifiez: moussaamir979@gmail.com")
        print("   (Pensez à vérifier les spams)")
    else:
        print("⚠️ Aucun email envoyé")
        
except Exception as e:
    print("\n" + "=" * 70)
    print(f"❌ ERREUR: {type(e).__name__}")
    print("=" * 70)
    print(f"   {e}")
    print(f"\n💡 Vérifiez:")
    print(f"   1. Clé API valide dans .env")
    print(f"   2. Email vérifié dans Brevo")
    print(f"   3. Package installé: pip install sib-api-v3-sdk")

print("\n" + "=" * 70)