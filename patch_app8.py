import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target1 = "import { Search, Play, Pause, X, Loader2, Music, SkipBack, SkipForward, Wand2 } from 'lucide-react'"
replacement1 = "import { Search, Play, Pause, X, Loader2, Music, SkipBack, SkipForward, Wand2, ListMusic } from 'lucide-react'"
content = content.replace(target1, replacement1)

target2 = "  const [duration, setDuration] = useState(0);"
replacement2 = "  const [duration, setDuration] = useState(0);\n  const [showQueue, setShowQueue] = useState(false);"
content = content.replace(target2, replacement2)

target3 = """          <div className="w-1/3 flex justify-end">
            <button 
              onClick={() => setCurrentPlaying(null)}
              className="text-gray-400 hover:text-white p-2"
              title="Fechar Player"
            >
              <X size={24} />
            </button>
          </div>
        </div>
      )}
    </div>"""

replacement3 = """          <div className="w-1/3 flex justify-end gap-2 relative">
            <button 
              onClick={() => setShowQueue(!showQueue)}
              className={`p-2 transition-colors ${showQueue ? 'text-green-500' : 'text-gray-400 hover:text-white'}`}
              title="Fila de Reprodução"
            >
              <ListMusic size={20} />
            </button>
            <button 
              onClick={() => setCurrentPlaying(null)}
              className="text-gray-400 hover:text-white p-2"
              title="Fechar Player"
            >
              <X size={24} />
            </button>

            {/* Fila Popup */}
            {showQueue && (
              <div className="absolute bottom-16 right-0 w-80 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl p-4 max-h-96 overflow-y-auto custom-scrollbar flex flex-col gap-2">
                <h4 className="font-bold text-white mb-2 sticky top-0 bg-gray-900 pb-2 border-b border-gray-800">Fila de Reprodução</h4>
                {playQueue.length === 0 ? (
                  <p className="text-gray-500 text-sm">Fila vazia</p>
                ) : (
                  playQueue.map((qTrack, idx) => (
                    <div 
                      key={idx} 
                      onClick={() => {
                        setCurrentPlaying({
                          ...qTrack,
                          streamUrl: `${API_URL}/play?query=${encodeURIComponent(qTrack.track_name + ' ' + qTrack.artists)}`
                        });
                      }}
                      className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors group ${currentPlaying?.track_name === qTrack.track_name ? 'bg-gray-800 border border-gray-700' : 'hover:bg-gray-800'}`}
                    >
                      {currentPlaying?.track_name === qTrack.track_name ? (
                        <Play size={14} className="text-green-500 shrink-0" />
                      ) : (
                        <span className="text-xs text-gray-500 font-bold w-3 shrink-0">{idx + 1}</span>
                      )}
                      <div className="truncate flex-1">
                        <p className={`text-sm truncate font-bold ${currentPlaying?.track_name === qTrack.track_name ? 'text-green-500' : 'text-white'}`}>{qTrack.track_name}</p>
                        <p className="text-xs text-gray-400 truncate">{qTrack.artists}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>"""

content = content.replace(target3, replacement3)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
