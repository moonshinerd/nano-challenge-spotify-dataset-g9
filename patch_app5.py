import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = """            <button 
              onClick={getPlaylistRecommendations}
              className="w-full bg-green-500 hover:bg-green-600 text-black py-4 rounded-xl font-bold text-lg transition-transform hover:scale-105 shadow-lg shadow-green-900/20"
            >
              Gerar Super Mix ✨
            </button>"""

replacement = """            <div className="flex gap-4 mb-4">
              <button 
                onClick={() => {
                   setPlayQueue(selectedTracks);
                   const first = selectedTracks[0];
                   setCurrentPlaying({
                     ...first,
                     streamUrl: `${API_URL}/play?query=${encodeURIComponent(first.track_name + ' ' + first.artists)}`
                   });
                }}
                className="w-1/2 bg-white hover:bg-gray-200 text-black py-4 rounded-xl font-bold text-md transition-transform hover:scale-105 flex items-center justify-center gap-2 shadow-lg"
              >
                <Play size={20} /> Tocar Lista
              </button>
              <button 
                onClick={getPlaylistRecommendations}
                className="w-1/2 bg-green-500 hover:bg-green-600 text-black py-4 rounded-xl font-bold text-md transition-transform hover:scale-105 flex items-center justify-center gap-2 shadow-lg shadow-green-900/20"
              >
                Super Mix ✨
              </button>
            </div>"""

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
