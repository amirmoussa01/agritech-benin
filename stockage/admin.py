from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import User
from .models import Entrepot, Stock, MouvementStock


# Configuration inline pour afficher les stocks dans la fiche entrepôt
class StockInline(admin.TabularInline):
    model = Stock
    extra = 0
    fields = ('type_culture', 'quantite_actuelle', 'seuil_alerte', 'statut_alerte')
    readonly_fields = ('statut_alerte',)
    
    def statut_alerte(self, obj):
        if obj.est_en_alerte():
            return format_html('<span style="color: red; font-weight: bold;">ALERTE</span>')
        return format_html('<span style="color: green;">OK</span>')
    statut_alerte.short_description = 'Statut'


# Configuration de l'affichage des Entrepôts dans l'admin
@admin.register(Entrepot)
class EntrepotAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('nom', 'arrondissement', 'capacite_max', 'stock_actuel_display', 
                    'taux_remplissage_display', 'gestionnaire_display')
    
    # Champs de recherche
    search_fields = ('nom', 'gestionnaire__username', 'gestionnaire__first_name', 
                     'gestionnaire__last_name', 'adresse')
    
    # Filtres latéraux
    list_filter = ('arrondissement__commune__departement', 'arrondissement__commune', 'gestionnaire')
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'arrondissement', 'capacite_max', 'adresse', 'photo')
        }),
        ('Gestion', {
            'fields': ('gestionnaire',),
            'description': 'Sélectionnez le gestionnaire responsable de cet entrepôt parmi les utilisateurs du groupe "Gestionnaires".'
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('date_creation',)
    
    # Afficher les stocks dans la fiche entrepôt
    inlines = [StockInline]
    
    # Méthode pour afficher le stock actuel
    def stock_actuel_display(self, obj):
        return f"{obj.stock_actuel():.0f} kg"
    stock_actuel_display.short_description = 'Stock actuel'
    
    # Méthode pour afficher le taux de remplissage avec couleur - CORRIGÉ
    def taux_remplissage_display(self, obj):
        taux = obj.taux_remplissage()
        if taux > 90:
            color = 'red'
        elif taux > 70:
            color = 'orange'
        else:
            color = 'green'
        # Format le pourcentage d'abord, puis passe-le à format_html
        pourcentage = f'{taux:.1f}%'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, pourcentage
        )
    taux_remplissage_display.short_description = 'Taux de remplissage'
    
    # Méthode pour afficher le gestionnaire
    def gestionnaire_display(self, obj):
        if obj.gestionnaire:
            return obj.nom_gestionnaire()
        return format_html('<span style="color: gray; font-style: italic;">Non assigné</span>')
    gestionnaire_display.short_description = 'Gestionnaire'
    
    # Limiter les choix de gestionnaire aux utilisateurs du groupe "Gestionnaires"
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "gestionnaire":
            # Afficher seulement les utilisateurs du groupe Gestionnaires ou superusers
            kwargs["queryset"] = User.objects.filter(
                groups__name='Gestionnaires'
            ) | User.objects.filter(is_superuser=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Configuration de l'affichage des Stocks dans l'admin
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('type_culture', 'entrepot', 'quantite_actuelle', 'seuil_alerte', 'statut_alerte_display', 'derniere_mise_a_jour')
    
    # Champs de recherche
    search_fields = ('type_culture__nom', 'entrepot__nom')
    
    # Filtres latéraux
    list_filter = ('type_culture', 'entrepot__arrondissement__commune')
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations de base', {
            'fields': ('entrepot', 'type_culture')
        }),
        ('Quantités', {
            'fields': ('quantite_actuelle', 'seuil_alerte')
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('derniere_mise_a_jour',)
    
    # Méthode pour afficher le statut d'alerte avec couleur
    def statut_alerte_display(self, obj):
        if obj.est_en_alerte():
            return format_html(
                '<span style="background-color: #ffcccc; padding: 3px 10px; border-radius: 3px; font-weight: bold;">ALERTE</span>'
            )
        return format_html(
            '<span style="background-color: #ccffcc; padding: 3px 10px; border-radius: 3px;">NORMAL</span>'
        )
    statut_alerte_display.short_description = 'Statut'


# Configuration de l'affichage des Mouvements de Stock dans l'admin
@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('type_mouvement_display', 'stock', 'quantite', 'date_mouvement', 'operateur', 'motif')
    
    # Champs de recherche
    search_fields = ('stock__type_culture__nom', 'stock__entrepot__nom', 'motif', 'operateur')
    
    # Filtres latéraux
    list_filter = ('type_mouvement', 'date_mouvement', 'stock__type_culture')
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations du mouvement', {
            'fields': ('stock', 'type_mouvement', 'quantite', 'recolte')
        }),
        ('Détails', {
            'fields': ('motif', 'operateur')
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('date_mouvement',)
    
    # Date hierarchy pour navigation par date
    date_hierarchy = 'date_mouvement'
    
    # Tri par défaut
    ordering = ('-date_mouvement',)
    
    # Méthode pour afficher le type de mouvement avec couleur
    def type_mouvement_display(self, obj):
        if obj.type_mouvement == 'ENTREE':
            return format_html(
                '<span style="color: green; font-weight: bold;">↑ ENTRÉE</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">↓ SORTIE</span>'
        )
    type_mouvement_display.short_description = 'Type'