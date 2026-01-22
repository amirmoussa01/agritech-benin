#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "🗄️ Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "🔄 Application des migrations..."
python manage.py migrate

# Charger les données initiales UNIQUEMENT si la base est vide
if [ -f "data.json" ]; then
    echo "🔍 Vérification de la base de données..."
    
    # Compter le nombre d'utilisateurs
    USER_COUNT=$(python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()
from django.contrib.auth.models import User
print(User.objects.count())
" 2>/dev/null || echo "0")
    
    if [ "$USER_COUNT" = "0" ]; then
        echo "📥 Base de données vide - Chargement des données initiales..."
        python manage.py loaddata data.json && echo "✅ Données chargées avec succès !" || echo "⚠️ Erreur lors du chargement (peut-être déjà chargé)"
    else
        echo "✅ Base de données déjà initialisée ($USER_COUNT utilisateurs)"
    fi
else
    echo "⚠️ Fichier data.json non trouvé - pas de chargement de données"
fi

echo "✅ Build terminé avec succès !"