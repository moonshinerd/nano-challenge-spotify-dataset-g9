import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = """                      <div key={idx} className="bg-gray-800 text-gray-300 text-xs px-3 py-1.5 rounded-md border border-gray-700 flex items-center gap-2">
                        {t.thumbnail && <img src={t.thumbnail} className="w-4 h-4 rounded-sm object-cover" />}
                        <span>{t.track_name}</span>
                      </div>"""

replacement = """                      <button 
                        key={idx} 
                        onClick={() => handlePlay(t)}
                        className="bg-gray-800 hover:bg-gray-700 hover:text-green-400 text-gray-300 text-xs px-3 py-1.5 rounded-md border border-gray-700 flex items-center gap-2 transition-colors group cursor-pointer"
                        title="Ouvir Faixa"
                      >
                        {t.thumbnail && <img src={t.thumbnail} className="w-4 h-4 rounded-sm object-cover" />}
                        <Play size={12} className="hidden group-hover:inline-block text-green-500" />
                        <span>{t.track_name}</span>
                      </button>"""

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
