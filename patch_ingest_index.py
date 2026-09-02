import re

with open("api/ingest_1m.py", "r", encoding="utf-8") as f:
    content = f.read()

target = 'print(f"Finalizado! Inseridas {count} músicas no total. (Ignoradas: {skipped})")'
replacement = """print(f"Finalizado! Inseridas {count} músicas no total. (Ignoradas: {skipped})")

print("Construindo índice HNSW para buscas em milissegundos...")
try:
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tracks_embedding ON tracks USING hnsw (embedding vector_cosine_ops);")
    conn.commit()
    print("Índice construído com sucesso!")
except Exception as e:
    print("Aviso ao construir o índice:", e)
    conn.rollback()"""

content = content.replace(target, replacement)

with open("api/ingest_1m.py", "w", encoding="utf-8") as f:
    f.write(content)
