import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Search Results track_name
content = re.sub(
    r'<p className="font-bold">\{track\.track_name\}</p>',
    r'<div className="marquee-wrapper max-w-[150px] sm:max-w-[300px]"><p className="font-bold marquee-text" title={track.track_name}>{track.track_name}</p></div>',
    content
)

# 2. Search Results artists
content = re.sub(
    r'<p className="text-sm text-gray-400">\{track\.artists\}</p>',
    r'<p className="text-sm text-gray-400 truncate max-w-[150px] sm:max-w-[300px]" title={track.artists}>{track.artists}</p>',
    content
)

# 3. Recommendations track_name
content = re.sub(
    r'<p className="font-bold text-lg">\{rec\.track_name\}</p>',
    r'<div className="marquee-wrapper max-w-[150px] sm:max-w-[400px]"><p className="font-bold text-lg marquee-text" title={rec.track_name}>{rec.track_name}</p></div>',
    content
)

# 4. Recommendations artists
content = re.sub(
    r'<p className="text-gray-400 text-sm">\{rec\.artists\}</p>',
    r'<p className="text-gray-400 text-sm truncate max-w-[150px] sm:max-w-[400px]" title={rec.artists}>{rec.artists}</p>',
    content
)

# 5. Playlist track_name
content = re.sub(
    r'<p className="font-bold text-sm text-white">\{t\.track_name\}</p>',
    r'<div className="marquee-wrapper max-w-[120px] sm:max-w-[180px]"><p className="font-bold text-sm text-white marquee-text" title={t.track_name}>{t.track_name}</p></div>',
    content
)

# 6. Playlist artists
content = re.sub(
    r'<p className="text-xs text-gray-400">\{t\.artists\}</p>',
    r'<p className="text-xs text-gray-400 truncate max-w-[120px] sm:max-w-[180px]" title={t.artists}>{t.artists}</p>',
    content
)

# Write back
with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied.")
