import re

with open("api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = 'raise HTTPException(status_code=500, detail=f"Erro ao baixar áudio: {str(e)}")'
replacement = 'raise HTTPException(status_code=400, detail="Essa música está bloqueada no YouTube (restrição de idade/região). Tente escolher outra versão da música na pesquisa!")'

content = content.replace(target, replacement)

with open("api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
