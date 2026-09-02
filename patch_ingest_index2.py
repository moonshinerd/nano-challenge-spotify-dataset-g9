import re

with open("api/ingest_1m.py", "r", encoding="utf-8") as f:
    content = f.read()

target = 'cur.execute("CREATE INDEX IF NOT EXISTS idx_tracks_embedding ON tracks USING hnsw (embedding vector_cosine_ops);")'
replacement = """cur.execute("SET maintenance_work_mem = '2GB';")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tracks_embedding ON tracks USING hnsw (embedding vector_cosine_ops);")"""

content = content.replace(target, replacement)

with open("api/ingest_1m.py", "w", encoding="utf-8") as f:
    f.write(content)
