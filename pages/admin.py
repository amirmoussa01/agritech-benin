from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'sujet', 'date_envoi', 'traite']
    list_filter = ['traite', 'date_envoi', 'sujet']
    search_fields = ['nom', 'email', 'sujet', 'message']
    date_hierarchy = 'date_envoi'
    
    fieldsets = (
        ('Informations du contact', {
            'fields': ('nom', 'email', 'telephone', 'sujet')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Gestion', {
            'fields': ('traite', 'date_envoi')
        }),
    )
    
    readonly_fields = ['date_envoi']
    
    # Marquer comme traité en masse
    actions = ['marquer_comme_traite']
    
    def marquer_comme_traite(self, request, queryset):
        queryset.update(traite=True)
    marquer_comme_traite.short_description = "Marquer comme traité"