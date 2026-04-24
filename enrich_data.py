# enrich_data.py
import json
import urllib.request
import time
from pathlib import Path

print("🎵 ENRICHISSEMENT DES DONNÉES")
print("=" * 50)

def fetch_json(url):
    try:
        headers = {'User-Agent': 'MusicScraper/1.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except:
        return None

def get_streaming_links(artist_name, album_name):
    """Génère les liens de streaming"""
    # Nettoyer les noms pour les URLs
    clean_artist = artist_name.replace(' ', '%20').replace('&', '')
    clean_album = album_name.replace(' ', '%20').replace('&', '')
    
    return {
        "apple": f"https://music.apple.com/search?term={clean_artist}%20{clean_album}",
        "spotify": f"https://open.spotify.com/search/{clean_artist}%20{clean_album}",
        "youtube": f"https://www.youtube.com/results?search_query={clean_artist}+{clean_album}",
        "deezer": f"https://www.deezer.com/search/{clean_artist}%20{clean_album}"
    }

def get_better_cover(artist_name, album_name):
    """Tente de trouver une meilleure pochette via Last.fm"""
    # Simplifié - on garde celle d'Apple pour l'instant
    return None

# Charger les données
with open('data/discography.json', 'r', encoding='utf-8') as f:
    artists = json.load(f)

print(f"📋 {len(artists)} artistes à enrichir")

# Enrichir chaque artiste
for i, artist in enumerate(artists, 1):
    print(f"[{i}/{len(artists)}] {artist['name'][:40]}")
    
    # Ajouter les liens de streaming pour chaque album/single/ep
    for album in artist.get('albums', []):
        if 'links' not in album:
            album['links'] = get_streaming_links(artist['name'], album['name'])
    
    for single in artist.get('singles', []):
        if 'links' not in single:
            single['links'] = get_streaming_links(artist['name'], single['name'])
    
    for ep in artist.get('eps', []):
        if 'links' not in ep:
            ep['links'] = get_streaming_links(artist['name'], ep['name'])
    
    if i % 100 == 0:
        print(f"   💾 Sauvegarde intermédiaire...")
        with open('data/discography_enriched.json', 'w', encoding='utf-8') as f:
            json.dump(artists, f, ensure_ascii=False, indent=2)
    
    time.sleep(0.1)

# Sauvegarde finale
with open('data/discography_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(artists, f, ensure_ascii=False, indent=2)

# Re-créer l'index
index = []
for artist in artists:
    index.append({
        'name': artist['name'],
        'albums': len(artist.get('albums', [])),
        'singles': len(artist.get('singles', [])),
        'eps': len(artist.get('eps', []))
    })

with open('data/index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fichiers créés :")
print(f"   - data/discography_enriched.json")
print(f"   - data/index.json (mis à jour)")