import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = """                  <button 
                    onClick={() => toggleTrackSelection(t)} 
                    className="text-gray-500 hover:text-red-400 p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Remover"
                  >
                    <X size={18} />
                  </button>"""

replacement = """                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button 
                      onClick={() => handlePlay(t)} 
                      className="text-gray-400 hover:text-green-500 p-2"
                      title="Ouvir"
                    >
                      <Play size={18} className={currentPlaying?.track_name === t.track_name ? "text-green-500" : ""} />
                    </button>
                    <button 
                      onClick={() => toggleTrackSelection(t)} 
                      className="text-gray-400 hover:text-red-400 p-2"
                      title="Remover"
                    >
                      <X size={18} />
                    </button>
                  </div>"""

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
