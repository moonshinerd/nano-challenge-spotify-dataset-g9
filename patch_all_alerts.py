import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('alert("Erro ao buscar músicas.")', 'setToast("Erro ao buscar músicas."); setTimeout(() => setToast(null), 5000)')
content = content.replace('alert("Erro ao buscar recomendações para a playlist.")', 'setToast("Erro ao buscar recomendações para a playlist."); setTimeout(() => setToast(null), 5000)')

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
