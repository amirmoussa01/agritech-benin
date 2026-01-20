#!/usr/bin/env bash
# exit on error
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Appliquer les migrations
python manage.py migrate

# Charger les données initiales (si le fichier existe ET si la base est vide)
if [ -f "data.json" ]; then
    echo "🔄 Vérification et chargement des données initiales..."
    python manage.py loaddata data.json || echo "⚠️ Données déjà présentes ou erreur ignorée."
fi