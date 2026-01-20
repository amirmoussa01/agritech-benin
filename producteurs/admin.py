from django.contrib import admin
from .models import Commune, Arrondissement, Producteur, Parcelle


# Configuration de l'affichage des Communes dans l'admin
@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('nom', 'departement', 'nombre_arrondissements')
    
    # Champs de recherche
    search_fields = ('nom', 'departement')
    
    # Filtres latéraux
    list_filter = ('departement',)
    
    # Méthode personnalisée pour compter les arrondissements
    def nombre_arrondissements(self, obj):
        return obj.arrondissements.count()
    nombre_arrondissements.short_description = 'Nombre d\'arrondissements'


# Configuration de l'affichage des Arrondissements dans l'admin
@admin.register(Arrondissement)
class ArrondissementAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('nom', 'commune', 'nombre_producteurs')
    
    # Champs de recherche
    search_fields = ('nom', 'commune__nom')
    
    # Filtres latéraux
    list_filter = ('commune__departement', 'commune')
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'commune')
        }),
    )
    
    # Méthode personnalisée pour compter les producteurs
    def nombre_producteurs(self, obj):
        return Producteur.objects.filter(arrondissement=obj).count()
    nombre_producteurs.short_description = 'Nombre de producteurs'


# Configuration inline pour afficher les parcelles dans la fiche producteur
class ParcelleInline(admin.TabularInline):
    model = Parcelle
    extra = 1  # Nombre de formulaires vides à afficher
    fields = ('nom', 'superficie', 'localisation', 'photo')


# Configuration de l'affichage des Producteurs dans l'admin
@admin.register(Producteur)
class ProducteurAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('nom', 'prenom', 'telephone', 'arrondissement', 'nombre_parcelles', 'date_inscription')
    
    # Champs de recherche
    search_fields = ('nom', 'prenom', 'telephone', 'email')
    
    # Filtres latéraux
    list_filter = ('arrondissement__commune__departement', 'arrondissement__commune', 'date_inscription')
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'photo', 'telephone', 'email')
        }),
        ('Localisation', {
            'fields': ('arrondissement',)
        }),
        ('Compte utilisateur', {
            'fields': ('user',),
            'classes': ('collapse',)  # Section repliable
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('date_inscription',)
    
    # Afficher les parcelles dans la fiche producteur
    inlines = [ParcelleInline]
    
    # Méthode personnalisée pour compter les parcelles
    def nombre_parcelles(self, obj):
        return obj.parcelles.count()
    nombre_parcelles.short_description = 'Nombre de parcelles'


# Configuration de l'affichage des Parcelles dans l'admin
@admin.register(Parcelle)
class ParcelleAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('nom', 'producteur', 'superficie', 'localisation', 'date_creation')
    
    # Champs de recherche
    search_fields = ('nom', 'producteur__nom', 'producteur__prenom', 'localisation')
    
    # Filtres latéraux
    list_filter = ('producteur__arrondissement__commune', 'date_creation')
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations générales', {
            'fields': ('producteur', 'nom', 'superficie', 'photo')
        }),
        ('Localisation', {
            'fields': ('localisation', 'latitude', 'longitude')
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('date_creation',)