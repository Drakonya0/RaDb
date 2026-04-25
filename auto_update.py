# auto_update.py
import urllib.request
import urllib.parse
import json
import time
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

print("🔄 MISE À JOUR AUTOMATIQUE - COMPLÈTE")
print("=" * 50)

# Configuration ntfy.sh
NTFY_TOPIC = "ma-musique"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# TON SITE (GitHub Pages)
SITE_URL = "https://drakonya0.github.io/RaDb"

def send_notification(title, message, priority=3, url=""):
    try:
        msg = message.encode('utf-8')
        headers = {
            'Title': title.encode('utf-8'),
            'Priority': str(priority),
            'Tags': 'musical_note',
            'Content-Type': 'text/plain; charset=utf-8'
        }
        if url:
            headers['Click'] = url.encode('utf-8', errors='ignore')
        req = urllib.request.Request(NTFY_URL, data=msg, method='POST', headers=headers)
        urllib.request.urlopen(req, timeout=10)
        print(f"   ✅ Notification: {title}")
    except Exception as e:
        print(f"   ⚠️ Erreur notification: {e}")

def fetch_json(url):
    for attempt in range(3):
        try:
            headers = {'User-Agent': 'MusicScraper/2.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.loads(response.read().decode('utf-8'))
        except:
            if attempt < 2:
                time.sleep((attempt + 1) * 2)
            else:
                return None
    return None

def search_artist(name):
    encoded = urllib.parse.quote(name)
    url = f"https://itunes.apple.com/search?term={encoded}&entity=musicArtist&limit=1&country=fr"
    data = fetch_json(url)
    if data and data.get('resultCount', 0) > 0:
        return data['results'][0]
    return None

def get_album_tracklist(album_id):
    url = f"https://itunes.apple.com/lookup?id={album_id}&entity=song"
    data = fetch_json(url)
    tracks = []
    if data:
        for r in data.get('results', []):
            if r.get('wrapperType') == 'track':
                ms = r.get('trackTimeMillis', 0)
                minutes = ms // 60000
                seconds = (ms % 60000) // 1000
                tracks.append({
                    'number': r.get('trackNumber', 0),
                    'name': r.get('trackName', ''),
                    'duration': f"{minutes}:{seconds:02d}"
                })
        tracks.sort(key=lambda x: x['number'])
    return tracks

def get_artist_data(artist_name):
    artist = search_artist(artist_name)
    if not artist:
        return None

    artist_id = artist['artistId']
    url = f"https://itunes.apple.com/lookup?id={artist_id}&entity=album&limit=200"
    data = fetch_json(url)

    albums, singles, eps = [], [], []

    if data:
        for r in data.get('results', []):
            if r.get('wrapperType') == 'collection':
                name = r.get('collectionName', '').replace(' - Single', '').replace(' - EP', '')
                year = r.get('releaseDate', '')[:4]
                cover = r.get('artworkUrl100', '').replace('100x100', '600x600')
                album_id = r.get('collectionId')
                release_date = r.get('releaseDate', '')[:10]

                album_data = {
                    'name': name,
                    'year': year,
                    'release_date': release_date,
                    'cover': cover,
                    'tracks': get_album_tracklist(album_id)
                }

                if ' - Single' in r.get('collectionName', ''):
                    singles.append(album_data)
                elif ' - EP' in r.get('collectionName', ''):
                    eps.append(album_data)
                else:
                    albums.append(album_data)

                time.sleep(0.2)

    return {
        'name': artist['artistName'],
        'id': artist_id,
        'albums': albums,
        'singles': singles,
        'eps': eps
    }

def load_previous_state():
    state_file = Path('data/previous_state.json')
    if state_file.exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_current_state(state):
    with open('data/previous_state.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def detect_new_releases(old_data, new_data):
    new_releases = []
    old_dict = {a.get('name'): a for a in old_data if a.get('name')}

    for new_artist in new_data:
        old_artist = old_dict.get(new_artist.get('name'), {})

        for album in new_artist.get('albums', []):
            if album['name'] not in [o.get('name') for o in old_artist.get('albums', [])]:
                new_releases.append({
                    'type': 'album',
                    'artist': new_artist['name'],
                    'title': album['name'],
                    'date': album.get('release_date', '')
                })

        for single in new_artist.get('singles', []):
            if single['name'] not in [o.get('name') for o in old_artist.get('singles', [])]:
                new_releases.append({
                    'type': 'single',
                    'artist': new_artist['name'],
                    'title': single['name'],
                    'date': single.get('release_date', '')
                })

        for ep in new_artist.get('eps', []):
            if ep['name'] not in [o.get('name') for o in old_artist.get('eps', [])]:
                new_releases.append({
                    'type': 'ep',
                    'artist': new_artist['name'],
                    'title': ep['name'],
                    'date': ep.get('release_date', '')
                })

    return new_releases

# ============ MAIN ============

print("\n📁 Nettoyage des anciennes données...")
if os.path.exists('data/artists'):
    shutil.rmtree('data/artists')
Path('data/artists').mkdir(parents=True, exist_ok=True)

# Charger état précédent
old_state = load_previous_state()
print(f"📊 Ancien état : {len(old_state)} artistes")

# Lire les artistes
with open('artists.txt', 'r', encoding='utf-8') as f:
    artists = [l.strip() for l in f if l.strip() and not l.startswith('#')]

print(f"📋 {len(artists)} artistes à traiter\n")

all_artist_data = []
success = 0
errors = 0

for i, artist_name in enumerate(artists, 1):
    print(f"[{i}/{len(artists)}] 🎤 {artist_name[:40]}")

    data = get_artist_data(artist_name)
    if data:
        safe_name = artist_name.replace('/', '_').replace('\\', '_').replace(':', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in ' _-')
        with open(f'data/artists/{safe_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        all_artist_data.append(data)
        print(f"   ✅ {len(data['albums'])} albums, {len(data['singles'])} singles, {len(data['eps'])} EPs")
        success += 1
    else:
        print(f"   ❌ Non trouvé")
        errors += 1

    time.sleep(0.3)

# Détecter les nouveautés
print("\n🔍 Détection des nouveautés...")
new_releases = detect_new_releases(old_state, all_artist_data)
print(f"🆕 {len(new_releases)} nouvelles sorties détectées")

# Envoi notification
if new_releases:
    album_count = len([r for r in new_releases if r['type'] == 'album'])
    single_count = len([r for r in new_releases if r['type'] == 'single'])
    send_notification(
        f"🔥 {len(new_releases)} NOUVEAUTÉS !",
        f"📀 {album_count} albums · 🎵 {single_count} singles",
        priority=4,
        url=f"{SITE_URL}/releases.html"
    )
else:
    send_notification(
        "✅ Mise à jour terminée",
        f"{success} artistes mis à jour",
        priority=2,
        url=SITE_URL
    )

# === CRÉATION DE L'INDEX ===
print("\n📊 Création de l'index...")
index = []
for json_file in Path('data/artists').glob('*.json'):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            artist = json.load(f)
            index.append({
                'name': artist['name'],
                'albums': len(artist.get('albums', [])),
                'singles': len(artist.get('singles', [])),
                'eps': len(artist.get('eps', []))
            })
    except:
        pass

index.sort(key=lambda x: x['name'])
with open('data/index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
print(f"   ✅ Index créé: {len(index)} artistes")

# === CRÉATION DE L'HISTORIQUE COMPLET ===
print("\n📜 Mise à jour de l'historique complet...")

history_file = Path('data/releases_history.json')
all_releases = []
if history_file.exists():
    with open(history_file, 'r', encoding='utf-8') as f:
        all_releases = json.load(f)

existing_titles = {(r['artist'], r['title']) for r in all_releases}
new_entries = []

for artist in all_artist_data:
    for album in artist.get('albums', []):
        if album.get('release_date'):
            key = (artist['name'], album['name'])
            if key not in existing_titles:
                new_entries.append({
                    'type': 'album',
                    'artist': artist['name'],
                    'title': album['name'],
                    'date': album['release_date'],
                    'cover': album.get('cover', '')
                })
    for single in artist.get('singles', []):
        if single.get('release_date'):
            key = (artist['name'], single['name'])
            if key not in existing_titles:
                new_entries.append({
                    'type': 'single',
                    'artist': artist['name'],
                    'title': single['name'],
                    'date': single['release_date'],
                    'cover': single.get('cover', '')
                })
    for ep in artist.get('eps', []):
        if ep.get('release_date'):
            key = (artist['name'], ep['name'])
            if key not in existing_titles:
                new_entries.append({
                    'type': 'ep',
                    'artist': artist['name'],
                    'title': ep['name'],
                    'date': ep['release_date'],
                    'cover': ep.get('cover', '')
                })

all_releases.extend(new_entries)
all_releases.sort(key=lambda x: x['date'], reverse=True)

with open('data/releases_history.json', 'w', encoding='utf-8') as f:
    json.dump(all_releases, f, ensure_ascii=False, indent=2)

# === CRÉER LE FICHIER DES NOUVEAUTÉS DE LA SEMAINE (CORRIGÉ) ===
print("📅 Filtrage des nouveautés de la semaine...")

today = datetime.now()
week_ago = today - timedelta(days=7)

new_releases_week = []
for r in all_releases:
    date_str = r.get('date')
    if not date_str:
        continue
    try:
        r_date = datetime.strptime(date_str, '%Y-%m-%d')
        if r_date >= week_ago:
            new_releases_week.append(r)
    except Exception:
        pass

with open('data/new_releases.json', 'w', encoding='utf-8') as f:
    json.dump(new_releases_week, f, ensure_ascii=False, indent=2)

print(f"   ✅ Historique complet: {len(all_releases)} sorties")
print(f"   🆕 Cette semaine: {len(new_releases_week)} sorties")

# Sauvegarde état
save_current_state(all_artist_data)

print("\n" + "=" * 50)
print(f"✅ MISE À JOUR TERMINÉE !")
print(f"   📊 Succès: {success}/{len(artists)}")
print(f"   ⚠️  Erreurs: {errors}")
print(f"   🆕 Nouveautés détectées: {len(new_releases)}")
print(f"   📜 Historique complet: {len(all_releases)} sorties")
print(f"   📅 Cette semaine: {len(new_releases_week)} sorties")
print("=" * 50)