#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "🗄️ Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "🔄 Application des migrations..."
python manage.py migrate

# FORCER le chargement des données à CHAQUE déploiement
if [ -f "data.json" ]; then
    echo "🔄 CHARGEMENT FORCÉ des données depuis data.json..."
    
    # Vider complètement la base de données
    echo "⚠️ Suppression des anciennes données..."
    python manage.py flush --no-input
    
    # Recréer les tables (au cas où)
    echo "🔄 Re-application des migrations..."
    python manage.py migrate
    
    # Charger les données
    echo "📥 Chargement des données..."
    python manage.py loaddata data.json
    
    # Vérifier le nombre d'utilisateurs chargés
    echo "🔍 Vérification..."
    python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()
from django.contrib.auth.models import User
from producteurs.models import Producteur
from recoltes.models import Recolte
print(f'✅ Utilisateurs: {User.objects.count()}')
print(f'✅ Producteurs: {Producteur.objects.count()}')
print(f'✅ Récoltes: {Recolte.objects.count()}')
" || echo "⚠️ Impossible de vérifier les données"
    
    echo "✅ Données chargées avec succès !"
else
    echo "❌ ERREUR: Fichier data.json non trouvé !"
    echo "⚠️ La base de données sera vide."
fi

echo "✅ Build terminé avec succès !"