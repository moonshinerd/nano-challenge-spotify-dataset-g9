import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target1 = """      const msg = error.response?.data?.detail || "Erro ao buscar recomendações.";
      alert(msg)"""
replacement1 = """      const msg = error.response?.data?.detail || "Erro ao buscar recomendações.";
      setToast(msg)
      setTimeout(() => setToast(null), 5000)"""

content = content.replace(target1, replacement1)

target2 = """      const msg = error.response?.data?.detail || "Erro ao gerar Super Mix.";
      alert(msg)"""
replacement2 = """      const msg = error.response?.data?.detail || "Erro ao gerar Super Mix.";
      setToast(msg)
      setTimeout(() => setToast(null), 5000)"""

content = content.replace(target2, replacement2)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
