#!/usr/bin/env bash
# exit on error
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Collecter les fichiers statiques
python manage.py collectstatic --no-input

# Appliquer les migrations
python manage.py migrate

# Charger les données initiales (seulement si la base est vide)
python manage.py load_initial_data