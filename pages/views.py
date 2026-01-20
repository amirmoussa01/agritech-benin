from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contact
from recoltes.models import Recolte, TypeCulture
from stockage.models import Entrepot
from producteurs.models import Producteur
from django.http import JsonResponse

def accueil(request):
    """Page d'accueil publique"""
    
    # Statistiques globales pour impressionner les visiteurs
    total_producteurs = Producteur.objects.count()
    total_recoltes = Recolte.objects.count()
    total_entrepots = Entrepot.objects.count()
    
    # Calcul de la production totale
    production_totale = sum(recolte.quantite for recolte in Recolte.objects.all())
    
    context = {
        'total_producteurs': total_producteurs,
        'total_recoltes': total_recoltes,
        'total_entrepots': total_entrepots,
        'production_totale': production_totale,
    }
    
    return render(request, 'pages/accueil.html', context)


def contact(request):
    """Page de contact avec formulaire"""
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        sujet = request.POST.get('sujet')
        message_texte = request.POST.get('message')
        
        # Validation basique
        if nom and email and sujet and message_texte:
            # Création du message de contact
            Contact.objects.create(
                nom=nom,
                email=email,
                telephone=telephone or '',
                sujet=sujet,
                message=message_texte
            )
            
            messages.success(request, 'Votre message a été envoyé avec succès ! Nous vous répondrons dans les plus brefs délais.')
            return redirect('contact')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
    
    return render(request, 'pages/contact.html')

def ping(request):
    """Endpoint léger pour le monitoring (UptimeRobot, Cron-Job, etc.)"""
    return JsonResponse({
        'status': 'ok',
        'message': 'AgriTech-Benin is alive',
        'service': 'running'
    })