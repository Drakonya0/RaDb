# update_music.py
import urllib.request
import json
from datetime import datetime

print("🔄 Mise à jour de la discographie")
print("=" * 40)

# Test de base
try:
    with open('artists.txt', 'r', encoding='utf-8') as f:
        artists = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    print(f"✅ {len(artists)} artistes chargés")
    
    # Tester l'API Apple avec le premier artiste
    if artists:
        test_name = urllib.parse.quote(artists[0])
        url = f"https://itunes.apple.com/search?term={test_name}&entity=musicArtist&limit=1"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            if data['results']:
                print(f"✅ API OK : {data['results'][0]['artistName']}")
            else:
                print(f"⚠️ Artiste non trouvé : {artists[0]}")
    
    # Sauvegarde vide pour que le workflow continue
    with open('data/discography.json', 'w') as f:
        json.dump({"test": "ok", "date": str(datetime.now())}, f)
    
    print("✅ Script terminé avec succès")
    
except Exception as e:
    print(f"❌ Erreur : {e}")
    exit(1)
