from django.urls import path
from . import views

# Définition des URLs pour l'application dashboard
urlpatterns = [
    # URL pour afficher le tableau de bord principal
    # Exemple: http://127.0.0.1:8000/dashboard/
    path('', views.tableau_de_bord, name='tableau_de_bord'),
]