import json
from pathlib import Path

print("📦 Création de l'index léger...")

# Charger le gros fichier avec l'encodage UTF-8
with open('data/discography.json', 'r', encoding='utf-8') as f:
    artists = json.load(f)

# Créer un index avec juste le nom + stats
index = []
for artist in artists:
    index.append({
        'name': artist['name'],
        'albums': len(artist.get('albums', [])),
        'singles': len(artist.get('singles', [])),
        'eps': len(artist.get('eps', []))
    })

# Sauvegarder l'index
with open('data/index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

# Calculer la taille du fichier
import os
size = os.path.getsize('data/index.json') / 1024
print(f"✅ Index créé : {len(index)} artistes")
print(f"   Taille : {size:.1f} KB")