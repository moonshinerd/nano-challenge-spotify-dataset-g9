import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { Search, Play, Pause, X, Loader2, Music, SkipBack, SkipForward, Wand2, ListMusic } from 'lucide-react'

function App() {
  const [errorMsg, setErrorMsg] = useState(null);
  const [toast, setToast] = useState(null);
  
  useEffect(() => {
    const handleErr = (msg, url, line, col, error) => {
      setErrorMsg(`${msg} - ${error?.stack}`);
      return false; 
    };
    window.onerror = handleErr;
    window.addEventListener('unhandledrejection', (e) => {
      setErrorMsg(`Unhandled Promise Rejection: ${e.reason?.message} - ${e.reason?.stack}`);
    });
  }, []);
  
  if (errorMsg) {
    return (
      <div className="bg-red-900 text-white p-10 h-screen w-screen overflow-auto">
        <h1 className="text-4xl font-bold">CRASH FATAL!</h1>
        <pre className="mt-4 whitespace-pre-wrap">{errorMsg}</pre>
        <button onClick={() => window.location.reload()} className="mt-4 bg-white text-black px-4 py-2 rounded">Reload</button>
      </div>
    );
  }

  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [recommendations, setRecommendations] = useState(null)
  const [selectedTracks, setSelectedTracks] = useState([])
  
  // Player state
  const [playQueue, setPlayQueue] = useState([])
  const [currentPlaying, setCurrentPlaying] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [showQueue, setShowQueue] = useState(false)
  const [isBuffering, setIsBuffering] = useState(false)
  const audioRef = useRef(null)
  const [loadingSearch, setLoadingSearch] = useState(false)
  const [loadingRecs, setLoadingRecs] = useState(false)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const [loadingMsgIdx, setLoadingMsgIdx] = useState(0)

  const loadingMessages = [
    "Conectando ao YouTube Music...",
    "Baixando amostra de áudio (yt-dlp)...",
    "Analisando ondas sonoras (Librosa)...",
    "Normalizando vetores (Z-Score)...",
    "Calculando similaridade no PostgreSQL...",
    "Quase lá..."
  ]

  useEffect(() => {
    let interval;
    if (loadingRecs) {
      interval = setInterval(() => {
        setLoadingMsgIdx((prev) => (prev + 1) % loadingMessages.length);
      }, 2500);
    }
    return () => clearInterval(interval);
  }, [loadingRecs]);

  useEffect(() => {
    if (currentPlaying) {
      setIsPlaying(true);
      setIsBuffering(true);
      setProgress(0);
    }
  }, [currentPlaying]);

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch(e => console.log(e));
      }
      setIsPlaying(!isPlaying);
    }
  };

  const formatTime = (time) => {
    if (!time || isNaN(time)) return "0:00"
    const mins = Math.floor(time / 60)
    const secs = Math.floor(time % 60)
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`
  };

  const searchSongs = async (e) => {
    e.preventDefault()
    if (!query) return
    setLoadingSearch(true)
    try {
      const res = await axios.get(`${API_URL}/search?query=${query}`)
      setSearchResults(res.data.results)
      setRecommendations(null)
    } catch (error) {
      console.error(error)
      setToast("Erro ao buscar músicas."); setTimeout(() => setToast(null), 5000)
    }
    setLoadingSearch(false)
  }

  const toggleTrackSelection = (track) => {
    if (selectedTracks.find(t => t.track_id === track.track_id)) {
      setSelectedTracks(selectedTracks.filter(t => t.track_id !== track.track_id))
    } else {
      setSelectedTracks([...selectedTracks, track])
    }
  }

  const getRecommendations = async (track_id, source) => {
    setLoadingRecs(true)
    setRecommendations(null)
    const oldSearch = searchResults;
    setSearchResults([])
    
    // Se for do Catálogo, é instantâneo, então travamos a mensagem no final
    if (source === 'database') {
      setLoadingMsgIdx(4);
    }

    try {
      const res = await axios.post(`${API_URL}/recommend`, { track_id, top_n: 5 })
      setRecommendations(res.data)
    } catch (error) {
      console.error(error)
      setSearchResults(oldSearch)
      const msg = error.response?.data?.detail || "Erro ao buscar recomendações.";
      setToast(msg)
      setTimeout(() => setToast(null), 5000)
    }
    setLoadingRecs(false)
  }

  const getPlaylistRecommendations = async () => {
    if (selectedTracks.length === 0) return
    
    setLoadingRecs(true)
    setRecommendations(null)
    setSearchResults([])
    setLoadingMsgIdx(0)
    
    try {
      const selectedThumbnails = selectedTracks.map(t => t.thumbnail).filter(Boolean);
      
      const res = await axios.post(`${API_URL}/recommend_playlist`, {
        track_ids: selectedTracks.map(t => t.track_id),
        top_n: 10
      })
      
      const data = res.data;
      data.reference.thumbnails = selectedThumbnails;
      data.reference.originalTracks = selectedTracks;
      
      setRecommendations(data)
      setSelectedTracks([]) 
    } catch (error) {
      console.error(error)
      setToast("Erro ao buscar recomendações para a playlist."); setTimeout(() => setToast(null), 5000)
    }
    setLoadingRecs(false)
  }

  const handlePlay = (track) => {
    const q = encodeURIComponent(`${track.track_name} ${track.artists}`);
    
    // Auto-engate (Queue Inteligente)
    let newQueue = [track];
    if (recommendations && (track.track_id === recommendations.reference.track_id || recommendations.recommendations.find(t => t.track_id === track.track_id))) {
      // Se estamos na tela de recomendações, engata as próximas recomendações
      const rest = recommendations.recommendations.filter(t => t.track_id !== track.track_id);
      newQueue = [track, ...rest];
    } else if (searchResults.length > 0) {
      // Se estamos na busca, engata os próximos resultados da busca
      const idx = searchResults.findIndex(t => t.track_id === track.track_id);
      if (idx >= 0) {
        newQueue = searchResults.slice(idx);
      }
    }
    
    setPlayQueue(newQueue);
    setCurrentPlaying({
      ...track,
      streamUrl: `${API_URL}/play?query=${q}`
    });
  }

  const handlePrevTrack = () => {
    if (!currentPlaying || playQueue.length === 0) return;
    const currentIndex = playQueue.findIndex(t => t.track_name === currentPlaying.track_name);
    if (currentIndex > 0) {
      const prev = playQueue[currentIndex - 1];
      const q = encodeURIComponent(`${prev.track_name} ${prev.artists}`);
      setCurrentPlaying({
        ...prev,
        streamUrl: `${API_URL}/play?query=${q}`
      });
    }
  }

  const handleNextTrack = () => {
    if (!currentPlaying || playQueue.length === 0) return;
    const currentIndex = playQueue.findIndex(t => t.track_name === currentPlaying.track_name);
    if (currentIndex >= 0 && currentIndex < playQueue.length - 1) {
      const next = playQueue[currentIndex + 1];
      const q = encodeURIComponent(`${next.track_name} ${next.artists}`);
      setCurrentPlaying({
        ...next,
        streamUrl: `${API_URL}/play?query=${q}`
      });
    } else {
      // Fim da fila
      setCurrentPlaying(null);
    }
  }

  const handlePlayPlaylist = () => {
    if (!recommendations) return;
    const orig = recommendations.reference.originalTracks || [recommendations.reference];
    const recs = recommendations.recommendations || [];
    const all = [...orig, ...recs];
    
    // Embaralhar (Shuffle)
    const shuffled = all.sort(() => Math.random() - 0.5);
    
    if (shuffled.length > 0) {
      setPlayQueue(shuffled);
      const first = shuffled[0];
      const q = encodeURIComponent(`${first.track_name} ${first.artists}`);
      setCurrentPlaying({
        ...first,
        streamUrl: `${API_URL}/play?query=${q}`
      });
    }
  }

  return (
    <div className={`min-h-screen p-4 md:p-8 max-w-7xl mx-auto flex flex-col lg:flex-row gap-8 justify-center transition-all duration-300 ${currentPlaying ? "pb-48" : "pb-12"}`}>
      {/* TOAST NOTIFICATION */}
      {toast && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded-full shadow-2xl z-50 flex items-center gap-3 animate-fade-in">
          <X size={18} className="cursor-pointer hover:text-gray-200" onClick={() => setToast(null)} />
          <span className="font-bold text-sm md:text-base">{toast}</span>
        </div>
      )}
      <div className="flex-1 w-full max-w-4xl mx-auto transition-all duration-500">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-green-500 mb-2">Music Recommender</h1>
          <p className="text-gray-400 mb-8">Descubra músicas semelhantes baseadas em atributos de áudio reais.</p>
          
          <form onSubmit={searchSongs} className="relative max-w-2xl mx-auto">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Digite o nome da música e artista..."
              className="w-full bg-gray-800 text-white rounded-full py-4 pl-6 pr-16 focus:outline-none focus:ring-2 focus:ring-green-500 text-lg shadow-lg"
            />
            <button
              type="submit"
              disabled={loadingSearch || !query}
              className="absolute right-2 top-2 p-2 bg-green-500 hover:bg-green-600 text-black rounded-full transition-colors disabled:opacity-50"
            >
              {loadingSearch ? <Loader2 size={24} className="animate-spin" /> : <Search size={24} />}
            </button>
          </form>
        </header>

      {/* SEARCH RESULTS */}
      {searchResults.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4 mb-8">
          <h2 className="text-xl font-bold mb-4">Resultados da Busca</h2>
          <div className="space-y-2">
            {searchResults.map(track => (
              <div key={track.track_id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 hover:bg-gray-700 rounded-lg transition-colors gap-3 sm:gap-0">
                <div className="flex items-center gap-4">
                  {track.thumbnail ? (
                    <img src={track.thumbnail} alt="Capa" className="w-12 h-12 rounded object-cover" />
                  ) : (
                    <div className="w-12 h-12 bg-gray-600 rounded flex items-center justify-center">🎵</div>
                  )}
                  <div>
                    <div className="flex items-center gap-2">
                      <div className="marquee-wrapper max-w-[150px] sm:max-w-[300px]"><p className="font-bold marquee-text" title={track.track_name}>{track.track_name}</p></div>
                      {track.source === 'database' ? (
                        <span className="bg-gray-600 text-xs px-2 py-0.5 rounded text-white">Catálogo</span>
                      ) : (
                        <span className="bg-blue-600 text-xs px-2 py-0.5 rounded text-white">Web</span>
                      )}
                    </div>
                    <div className="flex flex-wrap items-center gap-2 mt-1">
                      <p className="text-sm text-gray-400 truncate max-w-[150px] sm:max-w-[300px]" title={track.artists}>{track.artists}</p>
                      {track.genre && track.genre.split(',').map((g, idx) => (
                        <span key={idx} className="bg-gray-700 text-gray-300 text-[10px] px-2 py-0.5 rounded-full border border-gray-600">
                          {g.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 self-end sm:self-auto">
                  <button 
                    onClick={() => toggleTrackSelection(track)}
                    className={`p-3 rounded-full transition-colors font-bold ${selectedTracks.find(t => t.track_id === track.track_id) ? 'bg-green-500 text-black' : 'bg-gray-800 hover:bg-gray-700 text-white'}`}
                    title={selectedTracks.find(t => t.track_id === track.track_id) ? "Remover da Playlist" : "Adicionar à Playlist"}
                  >
                    {selectedTracks.find(t => t.track_id === track.track_id) ? "-" : "+"}
                  </button>
                  <button 
                    onClick={() => handlePlay(track)}
                    className="p-3 bg-gray-800 hover:bg-gray-700 text-white rounded-full transition-colors"
                    title="Ouvir Faixa"
                  >
                    <Play size={20} className={currentPlaying?.track_name === track.track_name ? "text-green-500" : ""} />
                  </button>
                  <button 
                    onClick={() => getRecommendations(track.track_id, track.source)}
                    className="px-4 py-2 sm:px-6 sm:py-3 bg-green-500 hover:bg-green-600 text-black font-bold rounded-full transition-transform hover:scale-105 flex items-center gap-2"
                  >
                    <span className="hidden sm:inline">Analisar & Recomendar</span>
                    <span className="sm:hidden flex items-center gap-1"><Wand2 size={16}/> Analisar</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}



      {/* LOADING STATE FOR SEARCH */}
      {loadingRecs && (
        <div className="flex flex-col items-center justify-center py-20 text-green-500">
          <Loader2 className="w-12 h-12 animate-spin mb-4" />
          <p className="text-xl font-bold">{loadingMessages[loadingMsgIdx]}</p>
          <p className="text-sm text-gray-400 mt-2">(Isso pode levar de 5 a 15 segundos na primeira vez)</p>
        </div>
      )}

      {/* RECOMMENDATIONS */}
      {recommendations && !loadingRecs && (
        <div className="space-y-8 animate-fade-in">
          {/* MÚSICA REFERÊNCIA */}
          <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700 flex flex-col md:flex-row gap-6 items-center">
            <div className="w-40 h-40 shrink-0 rounded-lg shadow-2xl overflow-hidden bg-gray-900">
              {recommendations.reference.thumbnails && recommendations.reference.thumbnails.length > 0 ? (
                <div className={`w-full h-full grid ${recommendations.reference.thumbnails.length >= 4 ? 'grid-cols-2 grid-rows-2' : recommendations.reference.thumbnails.length >= 2 ? 'grid-cols-2' : 'grid-cols-1'}`}>
                  {recommendations.reference.thumbnails.slice(0,4).map((thumb, i) => (
                    <img key={i} src={thumb} alt="Capa Mix" className={`w-full h-full object-cover ${recommendations.reference.thumbnails.length === 3 && i === 0 ? 'col-span-2 row-span-1 h-20' : ''}`} />
                  ))}
                </div>
              ) : recommendations.reference.thumbnail ? (
                <img src={recommendations.reference.thumbnail} alt="Capa" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-500">Sem Imagem</div>
              )}
            </div>
            <div className="flex-1">
              <p className="text-sm text-green-400 font-bold uppercase tracking-wider mb-1">Baseado em</p>
              <h2 className="text-3xl font-bold mb-2">{recommendations.reference.track_name}</h2>
              <p className="text-xl text-gray-400 mb-3">{recommendations.reference.artists}</p>
              <div className="flex flex-wrap gap-2 mb-6">
                {recommendations.reference.genre && recommendations.reference.genre.split(',').map((g, idx) => (
                  <span key={idx} className="bg-green-900/30 text-green-400 text-xs px-3 py-1 rounded-full border border-green-700/50">
                    {g.trim()}
                  </span>
                ))}
              </div>
              
              {recommendations.reference.originalTracks && (
                <div className="mb-6">
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-bold">Músicas Combinadas:</p>
                  <div className="flex flex-wrap gap-2">
                    {recommendations.reference.originalTracks.map((t, idx) => (
                      <button 
                        key={idx} 
                        onClick={() => handlePlay(t)}
                        className="bg-gray-800 hover:bg-gray-700 hover:text-green-400 text-gray-300 text-xs px-3 py-1.5 rounded-md border border-gray-700 flex items-center gap-2 transition-colors group cursor-pointer"
                        title="Ouvir Faixa"
                      >
                        {t.thumbnail && <img src={t.thumbnail} className="w-4 h-4 rounded-sm object-cover" />}
                        <Play size={12} className="hidden group-hover:inline-block text-green-500" />
                        <span>{t.track_name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-4">
                {recommendations.reference.originalTracks ? (
                  <button 
                    onClick={handlePlayPlaylist}
                    className="inline-flex items-center gap-2 bg-green-500 text-black px-6 py-3 rounded-full font-bold hover:scale-105 transition-transform"
                  >
                    <Play size={20} /> Tocar Super Mix
                  </button>
                ) : (
                  <>
                    <button 
                      onClick={() => handlePlay(recommendations.reference)}
                      className="inline-flex items-center gap-2 bg-white text-black px-6 py-3 rounded-full font-bold hover:scale-105 transition-transform"
                    >
                      <Play size={20} className={currentPlaying?.track_name === recommendations.reference.track_name ? "text-green-500" : ""} /> Ouvir Música
                    </button>
                    <button 
                      onClick={handlePlayPlaylist}
                      className="inline-flex items-center gap-2 bg-green-500 text-black px-6 py-3 rounded-full font-bold hover:scale-105 transition-transform"
                    >
                      <Play size={20} /> Tocar Rádio
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* LISTA RECOMENDADA */}
          <div>
            <h3 className="text-2xl font-bold mb-4">Recomendações</h3>
            <div className="grid gap-4">
              {recommendations.recommendations.map((rec, i) => (
                <div key={i} className="bg-gray-800 rounded-lg p-4 flex items-center gap-4 hover:bg-gray-700 transition-colors">
                  <div className="w-8 text-center text-gray-500 font-bold">{i + 1}</div>
                  
                  {rec.thumbnail ? (
                    <img src={rec.thumbnail} alt="Capa" className="w-16 h-16 rounded shadow-md" />
                  ) : (
                    <div className="w-16 h-16 bg-gray-700 rounded" />
                  )}
                  
                  <div className="flex-1">
                    <div className="marquee-wrapper max-w-[150px] sm:max-w-[400px]"><p className="font-bold text-lg marquee-text" title={rec.track_name}>{rec.track_name}</p></div>
                    <div className="flex flex-wrap items-center gap-2 mt-1">
                      <p className="text-gray-400 text-sm truncate max-w-[150px] sm:max-w-[400px]" title={rec.artists}>{rec.artists}</p>
                      {rec.genre && rec.genre.split(',').map((g, idx) => (
                        <span key={idx} className="bg-gray-700 text-gray-300 text-[10px] px-2 py-0.5 rounded-full border border-gray-600">
                          {g.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="text-right hidden md:block">
                    <p className="text-green-400 font-bold">{(rec.similarity * 100).toFixed(1)}% Match</p>
                  </div>
                  
                  <button 
                    onClick={() => handlePlay(rec)}
                    className="p-3 bg-gray-800 hover:bg-gray-700 rounded-full transition-colors ml-4"
                    title="Ouvir Faixa"
                  >
                    <Play size={20} className={currentPlaying?.track_name === rec.track_name ? "text-green-500" : "text-white"} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      </div> {/* FECHA O FLEX-1 ESQUERDO */}

      {/* PLAYLIST SELECTION SIDEBAR (RIGHT COLUMN) */}
      {selectedTracks.length > 0 && !loadingRecs && !recommendations && (
        <div className="w-full lg:w-96 shrink-0">
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-xl sticky top-8">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white">Sua Playlist Base</h3>
              <span className="bg-green-900/50 text-green-400 px-3 py-1 rounded-full text-sm font-bold">
                {selectedTracks.length} Músicas
              </span>
            </div>
            
            <div className="flex flex-col gap-3 mb-8 max-h-[50vh] overflow-y-auto pr-2 custom-scrollbar">
              {selectedTracks.map((t, idx) => (
                <div key={idx} className="bg-gray-900 p-3 rounded-xl flex items-center justify-between group">
                  <div className="flex items-center gap-3 overflow-hidden">
                    {t.thumbnail ? (
                      <img src={t.thumbnail} alt="" className="w-10 h-10 rounded object-cover" />
                    ) : (
                      <div className="w-10 h-10 bg-gray-800 rounded flex items-center justify-center">
                        <Music size={16} className="text-gray-500" />
                      </div>
                    )}
                    <div className="truncate">
                      <div className="marquee-wrapper max-w-[120px] sm:max-w-[200px]"><p className="text-sm font-bold text-white marquee-text" title={t.track_name}>{t.track_name}</p></div>
                      <div className="marquee-wrapper max-w-[120px] sm:max-w-[200px]"><p className="text-xs text-gray-400 marquee-text" title={t.artists}>{t.artists}</p></div>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
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
                  </div>
                </div>
              ))}
            </div>
            
            <div className="flex gap-4 mb-4">
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
            </div>
            <p className="text-gray-500 text-xs text-center mt-4">
              O sistema calculará o centróide matemático dos vetores acústicos para encontrar o ponto de equilíbrio perfeito entre as suas escolhas.
            </p>
          </div>
        </div>
      )}

      {/* GLOBAL AUDIO PLAYER */}
      {currentPlaying && (
        <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 p-4 px-4 sm:px-8 flex flex-wrap sm:flex-nowrap items-center justify-between z-50 shadow-[0_-10px_30px_rgba(0,0,0,0.5)] gap-4 sm:gap-0">
          <div className="flex items-center gap-4 w-1/3">
            {currentPlaying.thumbnail ? (
              <img src={currentPlaying.thumbnail} alt="Capa" className="w-14 h-14 rounded shadow-lg" />
            ) : (
              <div className="w-14 h-14 bg-gray-800 rounded flex items-center justify-center">
                <Music size={24} className="text-gray-500" />
              </div>
            )}
            <div>
              <div className="marquee-wrapper max-w-[150px] sm:max-w-[300px]"><p className="font-bold text-white text-sm md:text-base marquee-text" title={currentPlaying.track_name}>{currentPlaying.track_name}</p></div>
              <div className="marquee-wrapper max-w-[150px] sm:max-w-[300px]"><p className="text-gray-400 text-xs md:text-sm marquee-text" title={currentPlaying.artists}>{currentPlaying.artists}</p></div>
            </div>
          </div>
          
          <div className="w-1/2 flex flex-col items-center">
            <div className="flex items-center gap-4 mb-2">
              <button 
                onClick={handlePrevTrack} 
                className="text-gray-400 hover:text-white transition-colors"
                title="Música Anterior"
              >
                <SkipBack size={20} />
              </button>
              
              <button 
                onClick={togglePlayPause}
                className="w-10 h-10 flex items-center justify-center bg-white text-black rounded-full hover:scale-105 transition-transform"
                disabled={isBuffering}
              >
                {isBuffering ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : isPlaying ? (
                  <Pause size={20} className="fill-black" />
                ) : (
                  <Play size={20} className="fill-black ml-1" />
                )}
              </button>

              <button 
                onClick={handleNextTrack} 
                className="text-gray-400 hover:text-white transition-colors"
                title="Próxima Música"
              >
                <SkipForward size={20} />
              </button>
            </div>
            
            <div className="flex items-center w-full max-w-lg gap-3">
              <span className="text-xs text-gray-400 font-mono w-10 text-right">{formatTime(progress)}</span>
              <div className="flex-1 h-1.5 bg-gray-700 rounded-full relative group cursor-pointer"
                onClick={(e) => {
                  if (audioRef.current && duration) {
                    const rect = e.currentTarget.getBoundingClientRect()
                    const pos = (e.clientX - rect.left) / rect.width
                    audioRef.current.currentTime = pos * duration
                  }
                }}
              >
                <div 
                  className="absolute top-0 left-0 h-full bg-green-500 rounded-full" 
                  style={{ width: `${(progress / (duration || 1)) * 100}%` }}
                ></div>
                <div 
                  className="absolute top-1/2 -mt-1.5 -ml-1.5 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 shadow"
                  style={{ left: `${(progress / (duration || 1)) * 100}%` }}
                ></div>
              </div>
              <span className="text-xs text-gray-400 font-mono w-10">{formatTime(duration)}</span>
            </div>

            <audio 
              ref={audioRef}
              src={currentPlaying.streamUrl} 
              autoPlay 
              onTimeUpdate={() => setProgress(audioRef.current?.currentTime || 0)}
              onLoadedMetadata={() => setDuration(audioRef.current?.duration || 0)}
              onPlaying={() => { setIsPlaying(true); setIsBuffering(false); }}
              onWaiting={() => setIsBuffering(true)}
              onPause={() => setIsPlaying(false)}
              onEnded={handleNextTrack}
              className="hidden"
            />
          </div>
          
          <div className="w-1/3 flex justify-end gap-2 relative">
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
              <div className="absolute bottom-full mb-4 right-0 sm:right-8 w-80 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl p-4 max-h-96 overflow-y-auto custom-scrollbar flex flex-col gap-2">
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
    </div>
  )
}

export default App
