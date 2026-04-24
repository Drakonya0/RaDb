let allArtists = [];

async function loadArtistsList() {
    const container = document.getElementById('artists-list');
    container.innerHTML = '<div class="loading">chargement des artistes...</div>';
    
    try {
        // Charger index.json
        const response = await fetch('data/index.json');
        allArtists = await response.json();
        
        console.log('Artistes chargés:', allArtists.length);
        displayArtists(allArtists);
        
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = '<div class="empty">erreur de chargement</div>';
    }
}

function displayArtists(artists, filter = '') {
    const container = document.getElementById('artists-list');
    const filtered = artists.filter(a => 
        a.name && a.name.toLowerCase().includes(filter.toLowerCase())
    );
    
    if (filtered.length === 0) {
        container.innerHTML = '<div class="empty">aucun artiste trouvé</div>';
        return;
    }
    
    container.innerHTML = filtered.map(artist => `
        <div class="artist-card" onclick="goToArtist('${encodeURIComponent(artist.name)}')">
            <h3>${escapeHtml(artist.name)}</h3>
            <p>📀 ${artist.albums} · 🎵 ${artist.singles} · 💿 ${artist.eps}</p>
        </div>
    `).join('');
}

function goToArtist(artistName) {
    window.location.href = `artist.html?name=${encodeURIComponent(artistName)}`;
}

function setupSearch() {
    const search = document.getElementById('search');
    if (search) {
        search.addEventListener('input', (e) => {
            if (allArtists.length > 0) {
                displayArtists(allArtists, e.target.value);
            }
        });
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

loadArtistsList();
setupSearch();

// Dark mode toggle
const themeToggle = document.createElement('div');
themeToggle.className = 'theme-toggle';
themeToggle.innerHTML = `
    <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
`;
document.body.appendChild(themeToggle);

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    const isDark = document.body.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

// Charger le thème sauvegardé
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark');
}