from django.core.management.base import BaseCommand
from producteurs.permissions import create_groups


class Command(BaseCommand):
    """
    Commande Django pour initialiser les groupes d'utilisateurs
    Utilisation: python manage.py init_groups
    """
    help = 'Crée les groupes d\'utilisateurs et leurs permissions'

    def handle(self, *args, **options):
        # Appeler la fonction de création des groupes
        create_groups()
        self.stdout.write(
            self.style.SUCCESS('Groupes et permissions créés avec succès!')
        )