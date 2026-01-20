from django.urls import path
from . import views

# Définition des URLs pour l'application stockage
urlpatterns = [
    # URL pour afficher la liste des entrepôts
    # Exemple: http://127.0.0.1:8000/stockage/entrepots/
    path('entrepots/', views.liste_entrepots, name='liste_entrepots'),
    
    # URL pour voir les détails d'un entrepôt spécifique
    # Exemple: http://127.0.0.1:8000/stockage/entrepots/3/
    path('entrepots/<int:pk>/', views.detail_entrepot, name='detail_entrepot'),
    
    # URL pour afficher la liste de tous les stocks
    # Exemple: http://127.0.0.1:8000/stockage/stocks/
    path('stocks/', views.liste_stocks, name='liste_stocks'),
    
    # URL pour ajouter un mouvement de stock
    # Exemple: http://127.0.0.1:8000/stockage/stocks/5/mouvement/
    path('stocks/<int:stock_id>/mouvement/', views.ajouter_mouvement, name='ajouter_mouvement'),
    
    # URL pour voir l'historique des mouvements d'un stock
    # Exemple: http://127.0.0.1:8000/stockage/stocks/5/historique/
    path('stocks/<int:stock_id>/historique/', views.historique_mouvements, name='historique_mouvements'),
]