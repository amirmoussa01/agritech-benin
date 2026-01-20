from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Entrepot, Stock, MouvementStock
from .forms import MouvementStockForm


def is_gestionnaire(user):
    """
    Vérifie si l'utilisateur est dans le groupe Gestionnaires
    ou est un superutilisateur
    """
    return user.groups.filter(name='Gestionnaires').exists() or user.is_superuser


@login_required
@user_passes_test(is_gestionnaire)
def liste_entrepots(request):
    """
    Affiche la liste des entrepôts
    - Les gestionnaires voient UNIQUEMENT leur(s) entrepôt(s) assigné(s)
    - Les superutilisateurs voient tous les entrepôts
    """
    
    # Si c'est un superutilisateur, il voit tout
    if request.user.is_superuser:
        entrepots = Entrepot.objects.all()
        is_superuser = True
    else:
        # Sinon, le gestionnaire voit uniquement ses entrepôts
        entrepots = Entrepot.objects.filter(gestionnaire=request.user)
        is_superuser = False
    
    # Filtre de recherche
    search_query = request.GET.get('search', '')
    if search_query:
        entrepots = entrepots.filter(
            Q(nom__icontains=search_query) |
            Q(arrondissement__nom__icontains=search_query) |
            Q(gestionnaire__username__icontains=search_query)
        )
    
    # Calcul des statistiques
    capacite_totale = sum([e.capacite_max for e in entrepots])
    stock_total = sum([e.stock_actuel() for e in entrepots])
    
    # Calcul du taux moyen de remplissage
    if capacite_totale > 0:
        taux_moyen = (stock_total / capacite_totale) * 100
    else:
        taux_moyen = 0
    
    context = {
        'entrepots': entrepots,
        'search_query': search_query,
        'is_superuser': is_superuser,
        'capacite_totale': capacite_totale,
        'stock_total': stock_total,
        'taux_moyen': round(taux_moyen, 1),
    }
    
    return render(request, 'stockage/liste_entrepots.html', context)


@login_required
@user_passes_test(is_gestionnaire)
def detail_entrepot(request, pk):
    """
    Affiche les détails d'un entrepôt
    - Les gestionnaires peuvent voir UNIQUEMENT leurs entrepôts
    - Les superutilisateurs peuvent voir tous les entrepôts
    """
    
    entrepot = get_object_or_404(Entrepot, pk=pk)
    
    # Vérification des permissions
    if not request.user.is_superuser:
        # Si ce n'est pas un superutilisateur, vérifier que c'est son entrepôt
        if entrepot.gestionnaire != request.user:
            messages.error(request, "Vous n'avez pas accès à cet entrepôt.")
            return redirect('liste_entrepots')
    
    # Récupérer tous les stocks de cet entrepôt
    stocks = entrepot.stocks.all()
    
    # Récupérer les stocks en alerte
    stocks_alerte = [stock for stock in stocks if stock.est_en_alerte()]
    
    context = {
        'entrepot': entrepot,
        'stocks': stocks,
        'stocks_alerte': stocks_alerte,
    }
    
    return render(request, 'stockage/detail_entrepot.html', context)


@login_required
@user_passes_test(is_gestionnaire)
def liste_stocks(request):
    """
    Affiche la liste de tous les stocks
    - Les gestionnaires voient uniquement les stocks de leurs entrepôts
    - Les superutilisateurs voient tous les stocks
    """
    
    # Si c'est un superutilisateur, il voit tous les stocks
    if request.user.is_superuser:
        stocks = Stock.objects.all()
    else:
        # Sinon, le gestionnaire voit uniquement les stocks de ses entrepôts
        mes_entrepots = Entrepot.objects.filter(gestionnaire=request.user)
        stocks = Stock.objects.filter(entrepot__in=mes_entrepots)
    
    # Filtres
    type_culture_filter = request.GET.get('type_culture', '')
    alerte_only = request.GET.get('alerte', '')
    
    if type_culture_filter:
        stocks = stocks.filter(type_culture__nom=type_culture_filter)
    
    # Convertir en liste pour pouvoir filtrer avec est_en_alerte()
    stocks_list = list(stocks)
    
    if alerte_only:
        # Filtrer pour afficher uniquement les stocks en alerte
        stocks_list = [stock for stock in stocks_list if stock.est_en_alerte()]
    
    # Calcul des statistiques
    nombre_stocks = len(stocks_list)
    nombre_alertes = len([s for s in stocks_list if s.est_en_alerte()])
    stock_total = sum([s.quantite_actuelle for s in stocks_list])
    
    context = {
        'stocks': stocks_list,
        'type_culture_filter': type_culture_filter,
        'alerte_only': alerte_only,
        'nombre_stocks': nombre_stocks,
        'nombre_alertes': nombre_alertes,
        'stock_total': stock_total,
    }
    
    return render(request, 'stockage/liste_stocks.html', context)

@login_required
@user_passes_test(is_gestionnaire)
def ajouter_mouvement(request, stock_id):
    """
    Permet d'ajouter un mouvement de stock (entrée ou sortie)
    - Les gestionnaires peuvent ajouter des mouvements uniquement pour leurs entrepôts
    - Les superutilisateurs peuvent ajouter des mouvements pour tous les stocks
    """
    
    stock = get_object_or_404(Stock, pk=stock_id)
    
    # Vérification des permissions
    if not request.user.is_superuser:
        # Si ce n'est pas un superutilisateur, vérifier que c'est son entrepôt
        if stock.entrepot.gestionnaire != request.user:
            messages.error(request, "Vous n'avez pas accès à ce stock.")
            return redirect('liste_entrepots')
    
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            # Créer le mouvement mais ne pas encore sauvegarder
            mouvement = form.save(commit=False)
            mouvement.stock = stock
            
            # Ajouter l'opérateur (utilisateur connecté)
            mouvement.operateur = request.user.get_full_name() or request.user.username
            
            # Mettre à jour la quantité du stock
            if mouvement.type_mouvement == 'ENTREE':
                stock.quantite_actuelle += mouvement.quantite
            else:  # SORTIE
                if stock.quantite_actuelle >= mouvement.quantite:
                    stock.quantite_actuelle -= mouvement.quantite
                else:
                    messages.error(request, 'Quantité insuffisante en stock!')
                    return redirect('detail_entrepot', pk=stock.entrepot.pk)
            
            # Sauvegarder le stock et le mouvement
            stock.save()
            mouvement.save()
            
            messages.success(request, 'Mouvement de stock enregistré avec succès!')
            return redirect('detail_entrepot', pk=stock.entrepot.pk)
    else:
        form = MouvementStockForm()
    
    context = {
        'form': form,
        'stock': stock,
    }
    
    return render(request, 'stockage/ajouter_mouvement.html', context)


@login_required
@user_passes_test(is_gestionnaire)
def historique_mouvements(request, stock_id):
    """
    Affiche l'historique des mouvements d'un stock
    - Les gestionnaires peuvent voir l'historique uniquement pour leurs entrepôts
    - Les superutilisateurs peuvent voir tous les historiques
    """
    
    stock = get_object_or_404(Stock, pk=stock_id)
    
    # Vérification des permissions
    if not request.user.is_superuser:
        # Si ce n'est pas un superutilisateur, vérifier que c'est son entrepôt
        if stock.entrepot.gestionnaire != request.user:
            messages.error(request, "Vous n'avez pas accès à cet historique.")
            return redirect('liste_entrepots')
    
    mouvements = stock.mouvements.all()
    
    context = {
        'stock': stock,
        'mouvements': mouvements,
    }
    
    return render(request, 'stockage/historique_mouvements.html', context)