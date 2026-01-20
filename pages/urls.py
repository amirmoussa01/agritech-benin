from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('contact/', views.contact, name='contact'),
    path('ping/', views.ping, name='ping'),
]