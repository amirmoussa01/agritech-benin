#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "🗄️ Collecte des fichiers statiques..."
python manage.py collectstatic --no-input

echo "🔄 Application des migrations..."
python manage.py migrate

# Charger les données UNIQUEMENT si la base est complètement vide
if [ -f "data.json" ]; then
    echo "🔍 Vérification de la base de données..."
    
    # Utiliser manage.py shell pour compter de manière fiable
    USER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null || echo "error")
    
    if [ "$USER_COUNT" = "0" ]; then
        echo "📥 Base de données vide - Chargement des données initiales..."
        python manage.py loaddata data.json && echo "✅ Données chargées !" || echo "⚠️ Erreur chargement"
    elif [ "$USER_COUNT" = "error" ]; then
        echo "⚠️ Impossible de vérifier - Tentative de chargement..."
        python manage.py loaddata data.json || echo "⚠️ Erreur ou données déjà présentes"
    else
        echo "✅ Base de données OK - $USER_COUNT utilisateur(s) présent(s)"
        echo "ℹ️ Pas de rechargement (pour conserver les données existantes)"
    fi
else
    echo "⚠️ Fichier data.json non trouvé"
fi

echo "✅ Build terminé avec succès !"