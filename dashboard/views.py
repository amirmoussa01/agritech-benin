from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from recoltes.models import Recolte, TypeCulture
from stockage.models import Stock, Entrepot
from producteurs.models import Producteur, Arrondissement


@login_required
def tableau_de_bord(request):
    """
    Affiche le tableau de bord principal avec les statistiques
    - Les producteurs voient leurs propres statistiques
    - Les gestionnaires voient les statistiques de LEURS entrepôts uniquement
    - Les superutilisateurs voient les statistiques globales
    """
    
    # Vérifier si l'utilisateur est un producteur
    try:
        producteur = Producteur.objects.get(user=request.user)
        is_producteur = True
        
        # Statistiques pour le producteur connecté
        total_recoltes = Recolte.objects.filter(producteur=producteur).count()
        quantite_totale = Recolte.objects.filter(producteur=producteur).aggregate(
            total=Sum('quantite')
        )['total'] or 0
        
        # Récoltes par type de culture pour ce producteur
        recoltes_par_culture = Recolte.objects.filter(
            producteur=producteur
        ).values(
            'type_culture__nom'
        ).annotate(
            total=Sum('quantite')
        )
        
        # Dernières récoltes du producteur
        dernieres_recoltes = Recolte.objects.filter(
            producteur=producteur
        ).order_by('-date_recolte')[:5]
        
        context = {
            'is_producteur': is_producteur,
            'producteur': producteur,
            'total_recoltes': total_recoltes,
            'quantite_totale': quantite_totale,
            'recoltes_par_culture': recoltes_par_culture,
            'dernieres_recoltes': dernieres_recoltes,
        }
        
    except Producteur.DoesNotExist:
        # L'utilisateur est un gestionnaire ou admin
        is_producteur = False
        is_superuser = request.user.is_superuser
        
        # Vérifier si c'est un gestionnaire avec entrepôts assignés
        mes_entrepots = Entrepot.objects.filter(gestionnaire=request.user)
        is_gestionnaire = mes_entrepots.exists()
        
        if is_superuser:
            # ADMIN : Statistiques globales
            entrepots = Entrepot.objects.all()
            stocks = Stock.objects.all()
            
            # Statistiques globales
            total_producteurs = Producteur.objects.count()
            total_recoltes = Recolte.objects.count()
            total_entrepots = Entrepot.objects.count()
            
            # Quantité totale récoltée
            quantite_totale = Recolte.objects.aggregate(
                total=Sum('quantite')
            )['total'] or 0
            
            # Récoltes par type de culture (globalement)
            recoltes_par_culture = Recolte.objects.values(
                'type_culture__nom'
            ).annotate(
                total=Sum('quantite')
            )
            
            # Production par arrondissement
            production_par_zone = Recolte.objects.values(
                'producteur__arrondissement__nom',
                'producteur__arrondissement__commune__nom'
            ).annotate(
                total=Sum('quantite'),
                nombre_producteurs=Count('producteur', distinct=True)
            ).order_by('-total')[:10]
            
            # Stocks en alerte (tous)
            stocks_alerte = [stock for stock in stocks if stock.est_en_alerte()]
            
            # Rendements moyens par culture
            rendements_par_culture = []
            for culture in TypeCulture.objects.all():
                recoltes = Recolte.objects.filter(type_culture=culture)
                if recoltes.exists():
                    rendement_moyen = sum([r.rendement() for r in recoltes]) / recoltes.count()
                    rendements_par_culture.append({
                        'culture': culture.get_nom_display(),
                        'rendement_moyen': round(rendement_moyen, 2)
                    })
            
            context = {
                'is_producteur': is_producteur,
                'is_superuser': is_superuser,
                'is_gestionnaire': False,
                'total_producteurs': total_producteurs,
                'total_recoltes': total_recoltes,
                'total_entrepots': total_entrepots,
                'quantite_totale': quantite_totale,
                'recoltes_par_culture': recoltes_par_culture,
                'production_par_zone': production_par_zone,
                'stocks_alerte': stocks_alerte,
                'rendements_par_culture': rendements_par_culture,
            }
            
        elif is_gestionnaire:
            # GESTIONNAIRE : Statistiques de SES entrepôts uniquement
            
            # Ses entrepôts
            entrepots = mes_entrepots
            
            # Ses stocks
            stocks = Stock.objects.filter(entrepot__in=mes_entrepots)
            
            # Statistiques de ses entrepôts
            total_entrepots = mes_entrepots.count()
            
            # Capacité totale de ses entrepôts
            capacite_totale = mes_entrepots.aggregate(
                total=Sum('capacite_max')
            )['total'] or 0
            
            # Stock total de ses entrepôts
            stock_total = sum([e.stock_actuel() for e in mes_entrepots])
            
            # Taux de remplissage moyen
            if capacite_totale > 0:
                taux_moyen = (stock_total / capacite_totale) * 100
            else:
                taux_moyen = 0
            
            # Stocks en alerte dans ses entrepôts
            stocks_alerte = [stock for stock in stocks if stock.est_en_alerte()]
            
            # Stocks par type de culture
            stocks_par_culture = {}
            for stock in stocks:
                culture_nom = str(stock.type_culture)
                if culture_nom in stocks_par_culture:
                    stocks_par_culture[culture_nom] += stock.quantite_actuelle
                else:
                    stocks_par_culture[culture_nom] = stock.quantite_actuelle
            
            # Liste des entrepôts avec leurs infos
            mes_entrepots_infos = []
            for entrepot in mes_entrepots:
                mes_entrepots_infos.append({
                    'entrepot': entrepot,
                    'stock_actuel': entrepot.stock_actuel(),
                    'taux_remplissage': entrepot.taux_remplissage(),
                    'stocks_alerte': [s for s in entrepot.stocks.all() if s.est_en_alerte()],
                })
            
            context = {
                'is_producteur': is_producteur,
                'is_superuser': is_superuser,
                'is_gestionnaire': is_gestionnaire,
                'total_entrepots': total_entrepots,
                'capacite_totale': capacite_totale,
                'stock_total': stock_total,
                'taux_moyen': round(taux_moyen, 2),
                'stocks_alerte': stocks_alerte,
                'stocks_par_culture': stocks_par_culture,
                'mes_entrepots_infos': mes_entrepots_infos,
            }
            
        else:
            # Utilisateur sans rôle spécifique
            context = {
                'is_producteur': is_producteur,
                'is_superuser': is_superuser,
                'is_gestionnaire': is_gestionnaire,
            }
    
    return render(request, 'dashboard/tableau_de_bord.html', context)