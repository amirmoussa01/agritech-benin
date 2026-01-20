from django.db import models
from producteurs.models import Producteur, Parcelle


class TypeCulture(models.Model):
    CULTURES_CHOICES = [
        ('MAIS', 'Maïs'),
        ('SOJA', 'Soja'),
        ('ANANAS', 'Ananas'),
    ]
    
    nom = models.CharField(max_length=50, choices=CULTURES_CHOICES, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_nom_display()
    
    class Meta:
        verbose_name = "Type de Culture"
        verbose_name_plural = "Types de Cultures"


class Recolte(models.Model):
    producteur = models.ForeignKey(Producteur, on_delete=models.CASCADE, related_name='recoltes')
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE, related_name='recoltes')
    type_culture = models.ForeignKey(TypeCulture, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, help_text="Quantité en kg")
    date_recolte = models.DateField()
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    observations = models.TextField(blank=True)
    photo = models.ImageField(upload_to='recoltes/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.type_culture} - {self.quantite}kg - {self.producteur}"
    
    def rendement(self):
        """Calcule le rendement kg/hectare"""
        if self.parcelle.superficie > 0:
            return round(self.quantite / self.parcelle.superficie, 2)
        return 0
    
    class Meta:
        verbose_name = "Récolte"
        verbose_name_plural = "Récoltes"
        ordering = ['-date_recolte']