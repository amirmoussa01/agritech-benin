from django.urls import path
from . import views

# Définition des URLs pour l'application recoltes
urlpatterns = [
    # URL pour afficher la liste des récoltes
    # Exemple: http://127.0.0.1:8000/recoltes/
    path('', views.liste_recoltes, name='liste_recoltes'),
    
    # URL pour ajouter une nouvelle récolte
    # Exemple: http://127.0.0.1:8000/recoltes/ajouter/
    path('ajouter/', views.ajouter_recolte, name='ajouter_recolte'),
    
    # URL pour voir les détails d'une récolte spécifique
    # Exemple: http://127.0.0.1:8000/recoltes/5/
    path('<int:pk>/', views.detail_recolte, name='detail_recolte'),
]