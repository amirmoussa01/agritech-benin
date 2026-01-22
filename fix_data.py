"""
Script pour générer data.json avec encodage UTF-8 strict sans BOM
À placer à la RACINE du projet (même niveau que manage.py)

Usage: python fix_data.py
"""
import os
import sys
import django
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

from django.core import management
from io import StringIO

print("=" * 70)
print("🔧 Génération data.json UTF-8 sans BOM")
print("=" * 70)

# Capturer la sortie de dumpdata
output = StringIO()

try:
    # Exécuter dumpdata
    print("\n📊 Export des données depuis la base de données...")
    management.call_command(
        'dumpdata',
        natural_foreign=True,
        natural_primary=True,
        exclude=['contenttypes', 'auth.Permission'],
        indent=2,
        stdout=output
    )
    
    # Récupérer le contenu
    json_data = output.getvalue()
    
    # Vérifier que c'est du JSON valide
    print("🔍 Validation du JSON...")
    try:
        parsed = json.loads(json_data)
        print(f"✅ JSON valide : {len(parsed)} objets exportés")
    except json.JSONDecodeError as e:
        print(f"❌ Erreur JSON : {e}")
        sys.exit(1)
    
    # Écrire dans le fichier avec encodage UTF-8 explicite SANS BOM
    print("\n💾 Écriture dans data.json...")
    with open('data.json', 'w', encoding='utf-8', newline='\n') as f:
        f.write(json_data)
    
    print("✅ Fichier data.json créé")
    
    # Vérification de l'encodage
    print("\n🔍 Vérification de l'encodage...")
    with open('data.json', 'rb') as f:
        first_bytes = f.read(4)
        
    # Vérifier qu'il n'y a PAS de BOM
    if first_bytes[:3] == b'\xef\xbb\xbf':
        print("⚠️ BOM UTF-8 détecté - Suppression...")
        # Supprimer le BOM
        with open('data.json', 'rb') as f:
            content = f.read()
        if content[:3] == b'\xef\xbb\xbf':
            content = content[3:]
        with open('data.json', 'wb') as f:
            f.write(content)
        print("✅ BOM supprimé")
    elif first_bytes[:2] == b'\xff\xfe' or first_bytes[:2] == b'\xfe\xff':
        print("❌ ERREUR: BOM UTF-16 détecté!")
        print("Le fichier est corrompu. Réessayez.")
        sys.exit(1)
    else:
        print("✅ Encodage correct - Pas de BOM")
    
    # Afficher les premières lignes pour vérification visuelle
    print("\n📄 Aperçu du fichier généré:")
    print("-" * 70)
    with open('data.json', 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 15:
                break
            print(line.rstrip())
    print("-" * 70)
    
    # Statistiques
    print("\n📊 Statistiques:")
    print(f"   - Objets exportés: {len(parsed)}")
    
    # Compter par modèle
    models_count = {}
    for obj in parsed:
        model = obj.get('model', 'unknown')
        models_count[model] = models_count.get(model, 0) + 1
    
    for model, count in sorted(models_count.items()):
        print(f"   - {model}: {count}")
    
    print("\n" + "=" * 70)
    print("✅ SUCCESS - data.json est prêt à être déployé!")
    print("=" * 70)
    print("\n📌 Prochaines étapes:")
    print("   1. Vérifiez l'aperçu ci-dessus (doit être du JSON propre)")
    print("   2. git add data.json")
    print("   3. git commit -m 'Export données pour PostgreSQL'")
    print("   4. git push origin main")
    
except Exception as e:
    print(f"\n❌ Erreur lors de l'export: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)