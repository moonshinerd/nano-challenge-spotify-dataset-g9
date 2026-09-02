import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target1 = """  const getRecommendations = async (track_id, source) => {
    setLoadingRecs(true)
    setRecommendations(null)
    setSearchResults([]) // limpa a busca na hora para mostrar o carregamento"""

replacement1 = """  const getRecommendations = async (track_id, source) => {
    setLoadingRecs(true)
    setRecommendations(null)
    const oldSearch = searchResults;
    setSearchResults([])"""

content = content.replace(target1, replacement1)

target2 = """    try {
      const res = await axios.post(`${API_URL}/recommend`, { track_id, top_n: 5 })
      setRecommendations(res.data)
    } catch (error) {
      console.error(error)
      alert("Erro ao buscar recomendações.")
    }"""

replacement2 = """    try {
      const res = await axios.post(`${API_URL}/recommend`, { track_id, top_n: 5 })
      setRecommendations(res.data)
    } catch (error) {
      console.error(error)
      setSearchResults(oldSearch)
      const msg = error.response?.data?.detail || "Erro ao buscar recomendações.";
      alert(msg)
    }"""

content = content.replace(target2, replacement2)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
