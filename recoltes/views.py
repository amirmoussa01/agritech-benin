from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Recolte, TypeCulture
from producteurs.models import Producteur, Parcelle
from .forms import RecolteForm


@login_required
def liste_recoltes(request):
    """
    Affiche la liste des récoltes
    - Les producteurs voient uniquement leurs récoltes
    - Les gestionnaires voient toutes les récoltes
    """
    
    # Vérifier si l'utilisateur est un producteur
    try:
        producteur = Producteur.objects.get(user=request.user)
        # Le producteur voit uniquement ses récoltes
        recoltes = Recolte.objects.filter(producteur=producteur)
        is_producteur = True
    except Producteur.DoesNotExist:
        # L'utilisateur est un gestionnaire, il voit tout
        recoltes = Recolte.objects.all()
        is_producteur = False
    
    # Filtres de recherche
    search_query = request.GET.get('search', '')
    type_culture_filter = request.GET.get('type_culture', '')
    
    if search_query:
        recoltes = recoltes.filter(
            Q(producteur__nom__icontains=search_query) |
            Q(producteur__prenom__icontains=search_query) |
            Q(parcelle__nom__icontains=search_query)
        )
    
    if type_culture_filter:
        recoltes = recoltes.filter(type_culture__nom=type_culture_filter)
    
    # Récupérer tous les types de culture pour le filtre
    types_culture = TypeCulture.objects.all()
    
    context = {
        'recoltes': recoltes,
        'types_culture': types_culture,
        'is_producteur': is_producteur,
        'search_query': search_query,
        'type_culture_filter': type_culture_filter,
    }
    
    return render(request, 'recoltes/liste_recoltes.html', context)


@login_required
def ajouter_recolte(request):
    """
    Permet d'ajouter une nouvelle récolte
    Seuls les producteurs peuvent ajouter des récoltes
    """
    
    # Vérifier que l'utilisateur est un producteur
    try:
        producteur = Producteur.objects.get(user=request.user)
    except Producteur.DoesNotExist:
        messages.error(request, "Seuls les producteurs peuvent ajouter des récoltes.")
        return redirect('liste_recoltes')
    
    if request.method == 'POST':
        form = RecolteForm(request.POST, request.FILES, producteur=producteur)
        if form.is_valid():
            # Créer la récolte mais ne pas encore sauvegarder en base
            recolte = form.save(commit=False)
            # Associer le producteur connecté
            recolte.producteur = producteur
            # Sauvegarder en base
            recolte.save()
            
            messages.success(request, 'Récolte enregistrée avec succès!')
            return redirect('liste_recoltes')
    else:
        # Afficher le formulaire vide
        form = RecolteForm(producteur=producteur)
    
    context = {
        'form': form,
        'producteur': producteur,
    }
    
    return render(request, 'recoltes/ajouter_recolte.html', context)


@login_required
def detail_recolte(request, pk):
    """
    Affiche les détails d'une récolte
    - Les producteurs voient uniquement leurs récoltes
    - Les gestionnaires voient toutes les récoltes
    """
    
    recolte = get_object_or_404(Recolte, pk=pk)
    
    # Vérifier les permissions
    try:
        producteur = Producteur.objects.get(user=request.user)
        # Le producteur ne peut voir que ses propres récoltes
        if recolte.producteur != producteur:
            messages.error(request, "Vous n'avez pas accès à cette récolte.")
            return redirect('liste_recoltes')
    except Producteur.DoesNotExist:
        # L'utilisateur est un gestionnaire, il peut tout voir
        pass
    
    context = {
        'recolte': recolte,
    }
    
    return render(request, 'recoltes/detail_recolte.html', context)