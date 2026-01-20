from django.urls import path
from . import views

# Définition des URLs pour l'application producteurs
urlpatterns = [
    # URL pour l'inscription d'un nouveau producteur
    # Exemple: http://127.0.0.1:8000/producteurs/inscription/
    path('inscription/', views.inscription_producteur, name='inscription_producteur'),

     # URL pour le profil utilisateur
    path('profil/', views.profil_utilisateur, name='profil_utilisateur'),
    
    # URL pour la déconnexion
    path('deconnexion/', views.deconnexion, name='deconnexion'),
]