from django.contrib import admin
from .models import TypeCulture, Recolte


# Configuration de l'affichage des Types de Culture dans l'admin
@admin.register(TypeCulture)
class TypeCultureAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('nom', 'description')
    
    # Champs de recherche
    search_fields = ('nom', 'description')


# Configuration de l'affichage des Récoltes dans l'admin
@admin.register(Recolte)
class RecolteAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = ('type_culture', 'producteur', 'parcelle', 'quantite', 'date_recolte', 'rendement_display')
    
    # Champs de recherche
    search_fields = ('producteur__nom', 'producteur__prenom', 'type_culture__nom', 'parcelle__nom')
    
    # Filtres latéraux
    list_filter = ('type_culture', 'date_recolte', 'producteur__arrondissement__commune')
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations de base', {
            'fields': ('producteur', 'parcelle', 'type_culture')
        }),
        ('Quantités et dates', {
            'fields': ('quantite', 'date_recolte', 'photo')
        }),
        ('Observations', {
            'fields': ('observations',),
            'classes': ('collapse',)  # Section repliable
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('date_enregistrement',)
    
    # Date hierarchy pour navigation par date
    date_hierarchy = 'date_recolte'
    
    # Méthode personnalisée pour afficher le rendement
    def rendement_display(self, obj):
        return f"{obj.rendement()} kg/ha"
    rendement_display.short_description = 'Rendement'
    
    # Limitation des choix de parcelles selon le producteur sélectionné
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Si on édite une récolte existante
        if db_field.name == "parcelle":
            if request.resolver_match.kwargs.get('object_id'):
                # Récupérer l'ID de la récolte en cours d'édition
                recolte_id = request.resolver_match.kwargs['object_id']
                try:
                    recolte = Recolte.objects.get(pk=recolte_id)
                    # Limiter les parcelles à celles du producteur
                    kwargs["queryset"] = recolte.producteur.parcelles.all()
                except Recolte.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)