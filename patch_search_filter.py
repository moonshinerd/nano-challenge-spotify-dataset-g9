import re

with open("api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = 'yt_results = yt_client.search(query, filter="songs", limit=limit)'
replacement = 'yt_results = yt_client.search(query + " audio", limit=limit)'

content = content.replace(target, replacement)

with open("api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
