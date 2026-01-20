from django import forms
from .models import MouvementStock


class MouvementStockForm(forms.ModelForm):
    """
    Formulaire pour créer un mouvement de stock
    """
    
    class Meta:
        model = MouvementStock
        fields = ['type_mouvement', 'quantite', 'motif', 'recolte']
        widgets = {
            'type_mouvement': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'recolte': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'type_mouvement': 'Type de mouvement',
            'quantite': 'Quantité (kg)',
            'motif': 'Motif',
            'recolte': 'Récolte associée (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le champ recolte optionnel
        self.fields['recolte'].required = False