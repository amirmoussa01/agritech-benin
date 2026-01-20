from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from recoltes.models import Recolte
from stockage.models import Stock, MouvementStock


def create_groups():
    """
    Fonction pour créer les groupes d'utilisateurs et leurs permissions
    Cette fonction doit être exécutée une seule fois après la migration
    """
    
    # Groupe 1: Producteurs - peuvent uniquement gérer leurs propres données
    producteurs_group, created = Group.objects.get_or_create(name='Producteurs')
    if created:
        # Permissions pour voir et créer leurs propres récoltes
        content_type_recolte = ContentType.objects.get_for_model(Recolte)
        permission_view_recolte = Permission.objects.get(
            codename='view_recolte',
            content_type=content_type_recolte,
        )
        permission_add_recolte = Permission.objects.get(
            codename='add_recolte',
            content_type=content_type_recolte,
        )
        producteurs_group.permissions.add(permission_view_recolte, permission_add_recolte)
        print("Groupe 'Producteurs' créé avec succès")
    
    # Groupe 2: Gestionnaires - ont accès à tout
    gestionnaires_group, created = Group.objects.get_or_create(name='Gestionnaires')
    if created:
        # Permissions complètes sur les stocks et mouvements
        content_type_stock = ContentType.objects.get_for_model(Stock)
        content_type_mouvement = ContentType.objects.get_for_model(MouvementStock)
        
        # Récupérer toutes les permissions pour stocks et mouvements
        stock_permissions = Permission.objects.filter(content_type=content_type_stock)
        mouvement_permissions = Permission.objects.filter(content_type=content_type_mouvement)
        
        # Ajouter toutes ces permissions au groupe
        for perm in stock_permissions:
            gestionnaires_group.permissions.add(perm)
        for perm in mouvement_permissions:
            gestionnaires_group.permissions.add(perm)
        
        print("Groupe 'Gestionnaires' créé avec succès")
    
    return producteurs_group, gestionnaires_group