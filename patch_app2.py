import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'<p className="text-sm font-bold text-white truncate">\{t\.track_name\}</p>',
    r'<div className="marquee-wrapper max-w-[120px] sm:max-w-[200px]"><p className="text-sm font-bold text-white marquee-text" title={t.track_name}>{t.track_name}</p></div>',
    content
)

content = re.sub(
    r'<p className="text-xs text-gray-400 truncate">\{t\.artists\}</p>',
    r'<div className="marquee-wrapper max-w-[120px] sm:max-w-[200px]"><p className="text-xs text-gray-400 marquee-text" title={t.artists}>{t.artists}</p></div>',
    content
)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
