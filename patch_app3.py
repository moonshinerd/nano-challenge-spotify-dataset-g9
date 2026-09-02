import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'<p className="font-bold text-white text-sm md:text-base line-clamp-1">\{currentPlaying\.track_name\}</p>',
    r'<div className="marquee-wrapper max-w-[150px] sm:max-w-[300px]"><p className="font-bold text-white text-sm md:text-base marquee-text" title={currentPlaying.track_name}>{currentPlaying.track_name}</p></div>',
    content
)

content = re.sub(
    r'<p className="text-gray-400 text-xs md:text-sm line-clamp-1">\{currentPlaying\.artists\}</p>',
    r'<div className="marquee-wrapper max-w-[150px] sm:max-w-[300px]"><p className="text-gray-400 text-xs md:text-sm marquee-text" title={currentPlaying.artists}>{currentPlaying.artists}</p></div>',
    content
)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
