from django import forms
from .models import Recolte, TypeCulture


class RecolteForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une récolte
    """
    
    class Meta:
        model = Recolte
        fields = ['parcelle', 'type_culture', 'quantite', 'date_recolte', 'observations', 'photo']
        widgets = {
            'date_recolte': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parcelle': forms.Select(attrs={'class': 'form-control'}),
            'type_culture': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'parcelle': 'Parcelle',
            'type_culture': 'Type de culture',
            'quantite': 'Quantité (kg)',
            'date_recolte': 'Date de récolte',
            'observations': 'Observations',
            'photo': 'Photo de la récolte',
        }
    
    def __init__(self, *args, **kwargs):
        # Récupérer le producteur passé en paramètre
        producteur = kwargs.pop('producteur', None)
        super().__init__(*args, **kwargs)
        
        # Limiter les parcelles à celles du producteur
        if producteur:
            self.fields['parcelle'].queryset = producteur.parcelles.all()