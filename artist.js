const urlParams = new URLSearchParams(window.location.search);
const artistName = decodeURIComponent(urlParams.get('name'));

let artistData = null;

async function loadArtist() {
    const container = document.getElementById('discography-container');
    container.innerHTML = '<div class="loading">chargement...</div>';
    
    try {
        const response = await fetch('data/discography_enriched.json');
        const allArtists = await response.json();
        
        artistData = allArtists.find(a => a.name === artistName);
        
        if (!artistData) {
            throw new Error('Artiste non trouvé');
        }
        
        document.getElementById('artist-name').textContent = artistData.name;
        
        const totalAlbums = artistData.albums?.length || 0;
        const totalSingles = artistData.singles?.length || 0;
        const totalEps = artistData.eps?.length || 0;
        const totalTracks = [...(artistData.albums || []), ...(artistData.singles || []), ...(artistData.eps || [])]
            .reduce((sum, item) => sum + (item.tracks?.length || 0), 0);
        
        document.getElementById('artist-stats').innerHTML = `
            <div class="stats">
                <span class="stat-badge"><strong>${totalAlbums}</strong> albums</span>
                <span class="stat-badge"><strong>${totalSingles}</strong> singles</span>
                <span class="stat-badge"><strong>${totalEps}</strong> EPs</span>
                <span class="stat-badge"><strong>${totalTracks}</strong> titres</span>
            </div>
        `;
        
        renderDiscography();
        
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = '<div class="empty">artiste non trouvé</div>';
    }
}

function sortChronologique(items) {
    return [...items].sort((a, b) => {
        const yearA = parseInt(a.year) || 0;
        const yearB = parseInt(b.year) || 0;
        return yearB - yearA;
    });
}

function renderStreamingLinks(links) {
    if (!links) return '';
    
    const platforms = [
        { name: 'Apple Music', icon: '🍎', key: 'apple', class: 'apple' },
        { name: 'Spotify', icon: '🎵', key: 'spotify', class: 'spotify' },
        { name: 'YouTube', icon: '📺', key: 'youtube', class: 'youtube' },
        { name: 'Deezer', icon: '🎧', key: 'deezer', class: 'deezer' }
    ];
    
    return platforms.map(p => {
        if (links[p.key]) {
            return `<a href="${links[p.key]}" target="_blank" class="stream-link ${p.class}" onclick="event.stopPropagation()">${p.icon} ${p.name}</a>`;
        }
        return '';
    }).join('');
}

function renderTracks(tracks) {
    if (!tracks || tracks.length === 0) {
        return '<div class="track-item"><span class="track-name">tracklist non disponible</span></div>';
    }
    
    return tracks.map(track => `
        <div class="track-item">
            <span class="track-number">${String(track.number || '•').padStart(2, ' ')}</span>
            <span class="track-name">${escapeHtml(track.name)}</span>
            <span class="track-duration">${track.duration || ''}</span>
        </div>
    `).join('');
}

function renderDiscography() {
    const container = document.getElementById('discography-container');
    
    const sortedAlbums = sortChronologique(artistData.albums || []);
    const sortedSingles = sortChronologique(artistData.singles || []);
    const sortedEps = sortChronologique(artistData.eps || []);
    
    let html = '';
    
    if (sortedAlbums.length > 0) {
        html += `
            <div class="section">
                <div class="section-title">📀 albums studio · ${sortedAlbums.length}</div>
                <div class="albums-grid">
                    ${sortedAlbums.map((album, idx) => `
                        <div class="album-card">
                            <div class="album-header" onclick="toggleTracklist(${idx}, 'albums')">
                                <img src="${album.cover || ''}" class="album-cover" onerror="this.src='https://placehold.co/100x100/1c1c1e/98989d?text=no+cover'">
                                <div class="album-info">
                                    <div class="album-name">${escapeHtml(album.name)}</div>
                                    <div class="album-year">${album.year || '?'}</div>
                                    <div class="album-meta">${album.tracks?.length || 0} titres</div>
                                    <div class="streaming-links">
                                        ${renderStreamingLinks(album.links)}
                                    </div>
                                </div>
                            </div>
                            <div class="tracklist" id="tracklist-albums-${idx}">
                                ${renderTracks(album.tracks)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    if (sortedSingles.length > 0) {
        html += `
            <div class="section">
                <div class="section-title">🎵 singles · ${sortedSingles.length}</div>
                <div class="albums-grid">
                    ${sortedSingles.map((single, idx) => `
                        <div class="album-card">
                            <div class="album-header" onclick="toggleTracklist(${idx}, 'singles')">
                                <img src="${single.cover || ''}" class="album-cover" onerror="this.src='https://placehold.co/100x100/1c1c1e/98989d?text=no+cover'">
                                <div class="album-info">
                                    <div class="album-name">${escapeHtml(single.name)}</div>
                                    <div class="album-year">${single.year || '?'}</div>
                                    <div class="streaming-links">
                                        ${renderStreamingLinks(single.links)}
                                    </div>
                                </div>
                            </div>
                            <div class="tracklist" id="tracklist-singles-${idx}">
                                ${renderTracks(single.tracks)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    if (sortedEps.length > 0) {
        html += `
            <div class="section">
                <div class="section-title">💿 eps · ${sortedEps.length}</div>
                <div class="albums-grid">
                    ${sortedEps.map((ep, idx) => `
                        <div class="album-card">
                            <div class="album-header" onclick="toggleTracklist(${idx}, 'eps')">
                                <img src="${ep.cover || ''}" class="album-cover" onerror="this.src='https://placehold.co/100x100/1c1c1e/98989d?text=no+cover'">
                                <div class="album-info">
                                    <div class="album-name">${escapeHtml(ep.name)}</div>
                                    <div class="album-year">${ep.year || '?'}</div>
                                    <div class="streaming-links">
                                        ${renderStreamingLinks(ep.links)}
                                    </div>
                                </div>
                            </div>
                            <div class="tracklist" id="tracklist-eps-${idx}">
                                ${renderTracks(ep.tracks)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function toggleTracklist(idx, type) {
    const element = document.getElementById(`tracklist-${type}-${idx}`);
    if (element) {
        element.classList.toggle('open');
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

loadArtist();