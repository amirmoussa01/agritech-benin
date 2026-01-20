from django.db import models
from django.contrib.auth.models import User


class Commune(models.Model):
    nom = models.CharField(max_length=100)
    departement = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nom} ({self.departement})"
    
    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"


class Arrondissement(models.Model):
    nom = models.CharField(max_length=100)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='arrondissements')
    
    def __str__(self):
        return f"{self.nom} - {self.commune.nom}"
    
    class Meta:
        verbose_name = "Arrondissement"
        verbose_name_plural = "Arrondissements"


class Producteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    arrondissement = models.ForeignKey(Arrondissement, on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to='producteurs/', blank=True, null=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
    class Meta:
        verbose_name = "Producteur"
        verbose_name_plural = "Producteurs"
        ordering = ['nom', 'prenom']


class Parcelle(models.Model):
    producteur = models.ForeignKey(Producteur, on_delete=models.CASCADE, related_name='parcelles')
    nom = models.CharField(max_length=100)
    superficie = models.DecimalField(max_digits=10, decimal_places=2, help_text="Superficie en hectares")
    localisation = models.CharField(max_length=255, help_text="Description de la localisation")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photo = models.ImageField(upload_to='parcelles/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} - {self.producteur}"
    
    class Meta:
        verbose_name = "Parcelle"
        verbose_name_plural = "Parcelles"