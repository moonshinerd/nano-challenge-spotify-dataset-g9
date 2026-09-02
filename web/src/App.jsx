import { useState } from 'react'
import axios from 'axios'
import { Search, Play, Loader2 } from 'lucide-react'

function App() {
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [recommendations, setRecommendations] = useState(null)
  const [loadingSearch, setLoadingSearch] = useState(false)
  const [loadingRecs, setLoadingRecs] = useState(false)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
    }
    setLoadingSearch(false)
  }

  const getRecommendations = async (track_id) => {
    setLoadingRecs(true)
    try {
      const res = await axios.post(`${API_URL}/recommend`, { track_id, top_n: 5 })
      setRecommendations(res.data)
      setSearchResults([]) // limpa a busca
    } catch (error) {
      console.error(error)
    }
    setLoadingRecs(false)
  }

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-green-500 mb-2">Spotify Recommender</h1>
        <p className="text-gray-400">Busque uma música e receba recomendações instantâneas</p>
      </header>

      {/* SEARCH BAR */}
      <form onSubmit={searchSongs} className="relative mb-8 flex gap-2">
        <input 
          type="text" 
          placeholder="Digite o nome da música..."
          className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-green-500 transition-all"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-bold flex items-center gap-2">
          {loadingSearch ? <Loader2 className="animate-spin" /> : <Search />}
        </button>
      </form>

      {/* SEARCH RESULTS */}
      {searchResults.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-4 mb-8">
          <h2 className="text-xl font-bold mb-4">Resultados da Busca</h2>
          <div className="space-y-2">
            {searchResults.map(track => (
              <div key={track.track_id} className="flex items-center justify-between p-3 hover:bg-gray-700 rounded-lg transition-colors">
                <div className="flex items-center gap-4">
                  {track.thumbnail ? (
                    <img src={track.thumbnail} alt="Capa" className="w-12 h-12 rounded object-cover" />
                  ) : (
                    <div className="w-12 h-12 bg-gray-600 rounded flex items-center justify-center">🎵</div>
                  )}
                  <div>
                    <p className="font-bold">{track.track_name}</p>
                    <p className="text-sm text-gray-400">{track.artists} • {track.genre}</p>
                  </div>
                </div>
                <button 
                  onClick={() => getRecommendations(track.track_id)}
                  className="bg-gray-700 hover:bg-green-500 text-white px-4 py-2 rounded-full text-sm transition-colors"
                >
                  Gerar Recomendações
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* LOADING STATE FOR RECS */}
      {loadingRecs && (
        <div className="flex flex-col items-center justify-center py-20 text-green-500">
          <Loader2 className="w-12 h-12 animate-spin mb-4" />
          <p>Calculando similaridade e buscando capas no YouTube Music...</p>
        </div>
      )}

      {/* RECOMMENDATIONS */}
      {recommendations && !loadingRecs && (
        <div className="space-y-8 animate-fade-in">
          {/* MÚSICA REFERÊNCIA */}
          <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700 flex flex-col md:flex-row gap-6 items-center">
            {recommendations.reference.thumbnail ? (
              <img src={recommendations.reference.thumbnail} alt="Capa" className="w-40 h-40 rounded-lg shadow-2xl" />
            ) : (
              <div className="w-40 h-40 bg-gray-800 rounded-lg flex items-center justify-center">Sem Imagem</div>
            )}
            <div className="flex-1">
              <p className="text-sm text-green-400 font-bold uppercase tracking-wider mb-1">Baseado em</p>
              <h2 className="text-3xl font-bold mb-2">{recommendations.reference.track_name}</h2>
              <p className="text-xl text-gray-400 mb-6">{recommendations.reference.artists}</p>
              {recommendations.reference.url && (
                <a href={recommendations.reference.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-white text-black px-6 py-2 rounded-full font-bold hover:scale-105 transition-transform">
                  <Play size={18} /> Ouvir Referência
                </a>
              )}
            </div>
          </div>

          {/* LISTA RECOMENDADA */}
          <div>
            <h3 className="text-2xl font-bold mb-4">Recomendações</h3>
            <div className="grid gap-4">
              {recommendations.recommendations.map((rec, i) => (
                <div key={i} className="bg-gray-800 rounded-lg p-4 flex items-center gap-4 hover:bg-gray-750 transition-colors">
                  <div className="w-8 text-center text-gray-500 font-bold">{i + 1}</div>
                  
                  {rec.thumbnail ? (
                    <img src={rec.thumbnail} alt="Capa" className="w-16 h-16 rounded shadow-md" />
                  ) : (
                    <div className="w-16 h-16 bg-gray-700 rounded" />
                  )}
                  
                  <div className="flex-1">
                    <p className="font-bold text-lg">{rec.track_name}</p>
                    <p className="text-gray-400">{rec.artists}</p>
                  </div>
                  
                  <div className="text-right hidden md:block">
                    <p className="text-xs text-gray-500 uppercase">Match</p>
                    <p className="font-bold text-green-400">{(rec.similarity * 100).toFixed(1)}%</p>
                  </div>

                  {rec.url && (
                    <a href={rec.url} target="_blank" rel="noreferrer" className="p-3 bg-gray-700 hover:bg-white hover:text-black rounded-full transition-colors ml-4">
                      <Play size={20} className="ml-1" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
