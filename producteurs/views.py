from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import InscriptionProducteurForm
from .models import Producteur


def inscription_producteur(request):
    """
    Vue pour l'inscription d'un nouveau producteur
    Accessible sans authentification
    """
    
    # Si l'utilisateur est déjà connecté, le rediriger vers le tableau de bord
    if request.user.is_authenticated:
        return redirect('tableau_de_bord')
    
    if request.method == 'POST':
        form = InscriptionProducteurForm(request.POST, request.FILES)
        if form.is_valid():
            # Créer le compte utilisateur et le profil producteur
            user = form.save()
            
            # Connecter automatiquement l'utilisateur après inscription
            login(request, user)
            
            messages.success(
                request, 
                f'Bienvenue {user.first_name} ! Votre compte a été créé avec succès.'
            )
            return redirect('tableau_de_bord')
    else:
        form = InscriptionProducteurForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'producteurs/inscription.html', context)


@login_required
def profil_utilisateur(request):
    """
    Affiche le profil de l'utilisateur connecté
    """
    try:
        # Si l'utilisateur est un producteur
        producteur = Producteur.objects.get(user=request.user)
        context = {
            'producteur': producteur,
            'is_producteur': True,
        }
    except Producteur.DoesNotExist:
        # Si c'est un gestionnaire ou admin
        context = {
            'is_producteur': False,
        }
    
    return render(request, 'producteurs/profil.html', context)


@login_required
def deconnexion(request):
    """
    Déconnecte l'utilisateur et supprime la session
    """
    if request.method == 'POST':
        # Déconnecter l'utilisateur
        logout(request)
        
        # Message de confirmation
        messages.success(request, 'Vous avez été déconnecté avec succès.')
        
        # Rediriger vers la page de connexion
        return redirect('login')
    
    # Si la méthode n'est pas POST, rediriger vers le tableau de bord
    return redirect('tableau_de_bord')