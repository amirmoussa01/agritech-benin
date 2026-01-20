from django.db import migrations, models
import django.db.models.deletion


def migrate_gestionnaire_to_null(apps, schema_editor):
    """
    Vide le champ gestionnaire avant de changer son type
    """
    Entrepot = apps.get_model('stockage', 'Entrepot')
    # Mettre tous les gestionnaires à vide (pour éviter les conflits)
    for entrepot in Entrepot.objects.all():
        entrepot.gestionnaire = None
        entrepot.save()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('stockage', '0001_initial'),
    ]

    operations = [
        # Étape 1: Supprimer le champ telephone_gestionnaire
        migrations.RemoveField(
            model_name='entrepot',
            name='telephone_gestionnaire',
        ),
        
        # Étape 2: Renommer temporairement l'ancien champ gestionnaire
        migrations.RenameField(
            model_name='entrepot',
            old_name='gestionnaire',
            new_name='gestionnaire_old',
        ),
        
        # Étape 3: Ajouter le nouveau champ gestionnaire (ForeignKey)
        migrations.AddField(
            model_name='entrepot',
            name='gestionnaire',
            field=models.ForeignKey(
                blank=True,
                help_text='Gestionnaire responsable de cet entrepôt',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='auth.user'
            ),
        ),
        
        # Étape 4: Supprimer l'ancien champ
        migrations.RemoveField(
            model_name='entrepot',
            name='gestionnaire_old',
        ),
    ]