"""
URL configuration for agritech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Configuration des URLs principales du projet
urlpatterns = [
    # URL de l'interface d'administration Django
    path('admin/', admin.site.urls),
    
    # URLs des pages publiques (accueil et contact) - DOIT ÊTRE EN PREMIER
    path('', include('pages.urls')),
    
    # URL pour la page de connexion
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # URL pour la page de déconnexion
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # URLs de l'application producteurs (inscription)
    path('producteurs/', include('producteurs.urls')),
    
    # URL du tableau de bord (page d'accueil après connexion)
    path('dashboard/', include('dashboard.urls')),
    
    # URLs de l'application récoltes
    path('recoltes/', include('recoltes.urls')),
    
    # URLs de l'application stockage
    path('stockage/', include('stockage.urls')),
]

# Configuration pour servir les fichiers média en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)