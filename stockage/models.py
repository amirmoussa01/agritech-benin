from django.db import models
from producteurs.models import Arrondissement
from recoltes.models import TypeCulture, Recolte
from django.contrib.auth.models import User

class Entrepot(models.Model):
    nom = models.CharField(max_length=100)
    arrondissement = models.ForeignKey(Arrondissement, on_delete=models.CASCADE, related_name='entrepots')
    capacite_max = models.DecimalField(max_digits=10, decimal_places=2, help_text="Capacité maximale en kg")
    adresse = models.CharField(max_length=255)
    
    # MODIFIÉ : Le gestionnaire est maintenant un utilisateur réel
    gestionnaire = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        limit_choices_to={'groups__name': 'Gestionnaires'},  # Seulement les gestionnaires
        help_text="Gestionnaire responsable de cet entrepôt"
    )
    
    photo = models.ImageField(upload_to='entrepots/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} - {self.arrondissement}"
    
    def stock_actuel(self):
        """Calcule le stock total actuel"""
        total = 0
        for stock in self.stocks.all():
            total += stock.quantite_actuelle
        return total
    
    def taux_remplissage(self):
        """Calcule le pourcentage de remplissage"""
        if self.capacite_max > 0:
            return round((self.stock_actuel() / self.capacite_max) * 100, 2)
        return 0
    
    # NOUVEAU : Méthode pour obtenir le nom du gestionnaire
    def nom_gestionnaire(self):
        """Retourne le nom complet du gestionnaire ou 'Non assigné'"""
        if self.gestionnaire:
            return self.gestionnaire.get_full_name() or self.gestionnaire.username
        return "Non assigné"
    
    # NOUVEAU : Méthode pour obtenir le téléphone du gestionnaire
    def telephone_gestionnaire(self):
        """Retourne le téléphone du gestionnaire si c'est un producteur (sinon email)"""
        if self.gestionnaire:
            try:
                # Si le gestionnaire a un profil producteur
                producteur = self.gestionnaire.producteur
                return producteur.telephone
            except:
                # Sinon retourner l'email
                return self.gestionnaire.email or "Non renseigné"
        return "Non renseigné"
    
    class Meta:
        verbose_name = "Entrepôt"
        verbose_name_plural = "Entrepôts"


class Stock(models.Model):
    entrepot = models.ForeignKey(Entrepot, on_delete=models.CASCADE, related_name='stocks')
    type_culture = models.ForeignKey(TypeCulture, on_delete=models.CASCADE)
    quantite_actuelle = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seuil_alerte = models.DecimalField(max_digits=10, decimal_places=2, help_text="Seuil d'alerte en kg")
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.type_culture} - {self.entrepot.nom} ({self.quantite_actuelle}kg)"
    
    def est_en_alerte(self):
        """
        Vérifie si le stock est en dessous du seuil d'alerte
        Retourne False si les valeurs sont None pour éviter les erreurs
        """
        if self.quantite_actuelle is not None and self.seuil_alerte is not None:
            return self.quantite_actuelle < self.seuil_alerte
        return False
    
    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        unique_together = ['entrepot', 'type_culture']


class MouvementStock(models.Model):
    TYPE_MOUVEMENT = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
    ]
    
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='mouvements')
    recolte = models.ForeignKey(Recolte, on_delete=models.SET_NULL, null=True, blank=True)
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    motif = models.CharField(max_length=255)
    operateur = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.type_mouvement} - {self.quantite}kg - {self.stock}"
    
    class Meta:
        verbose_name = "Mouvement de Stock"
        verbose_name_plural = "Mouvements de Stock"
        ordering = ['-date_mouvement']