from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Producteur, Arrondissement


class InscriptionProducteurForm(UserCreationForm):
    """
    Formulaire pour l'inscription d'un nouveau producteur
    Combine la création d'un compte utilisateur et d'un profil producteur
    """
    
    # Champs pour le compte utilisateur
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choisissez un nom d\'utilisateur'})
    )
    
    email = forms.EmailField(
        label="Adresse email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre.email@exemple.com'})
    )
    
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Créez un mot de passe sécurisé'})
    )
    
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez votre mot de passe'})
    )
    
    # Champs pour le profil producteur
    nom = forms.CharField(
        label="Nom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom de famille'})
    )
    
    prenom = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    
    telephone = forms.CharField(
        label="Téléphone",
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: +229 XX XX XX XX'})
    )
    
    arrondissement = forms.ModelChoiceField(
        label="Arrondissement",
        queryset=Arrondissement.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Sélectionnez votre arrondissement --"
    )
    
    photo = forms.ImageField(
        label="Photo de profil (optionnel)",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        """
        Vérifie que l'email n'est pas déjà utilisé
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email
    
    def save(self, commit=True):
        """
        Sauvegarde le compte utilisateur et crée le profil producteur
        """
        # Créer le compte utilisateur
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['prenom']
        user.last_name = self.cleaned_data['nom']
        
        if commit:
            user.save()
            
            # Créer le profil producteur associé
            producteur = Producteur.objects.create(
                user=user,
                nom=self.cleaned_data['nom'],
                prenom=self.cleaned_data['prenom'],
                telephone=self.cleaned_data['telephone'],
                email=self.cleaned_data['email'],
                arrondissement=self.cleaned_data['arrondissement'],
                photo=self.cleaned_data.get('photo')
            )
            
            # Ajouter l'utilisateur au groupe Producteurs
            from django.contrib.auth.models import Group
            producteurs_group, created = Group.objects.get_or_create(name='Producteurs')
            user.groups.add(producteurs_group)
        
        return user