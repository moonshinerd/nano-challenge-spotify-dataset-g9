import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import json
from weights import FEATURE_WEIGHTS

FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 
    'speechiness', 'acousticness', 'instrumentalness', 
    'liveness', 'valence', 'tempo'
]

print("Carregando status de Normalização (stats.json)...")
with open("stats.json", "r") as f:
    stats = json.load(f)

print("Conectando ao banco de dados...")
conn = psycopg2.connect(host="db", dbname="spotify", user="user", password="password")
cur = conn.cursor()

print("Puxando lista de músicas já existentes para evitar duplicatas...")
cur.execute("SELECT LOWER(TRIM(track_name)), LOWER(TRIM(artists)) FROM tracks;")
existing = set(cur.fetchall())
print(f"Total no banco atualmente: {len(existing)}")

print("Lendo CSV Comprimido de 1 Milhão...")
df = pd.read_csv("/data/raw/dataset_1M_clean.csv.gz", compression='gzip')

inserts = []
count = 0
skipped = 0

print("Processando e Normalizando novos vetores...")
for idx, row in df.iterrows():
    t_name = str(row['name']).strip()
    t_artists = str(row['artists']).strip()
    
    t_name_lower = t_name.lower()
    t_artists_lower = t_artists.lower()
    
    # Previne duplicatas exatas de Nome + Artista
    if (t_name_lower, t_artists_lower) in existing:
        skipped += 1
        continue
        
    t_id = str(row.get('track_id', row.get('id', f"new_{count}")))
    
    z_scores = []
    # Usando 14 dimensões (11 features acústicas + 3 zeradas para time_signature etc se for o caso)
    # Na verdade, nosso vetor tem 14 dimensões no banco?
    # Vamos conferir o que o main.py insere no cold_start!
    # No main.py, len(FEATURES) é 11. Mas e as outras 3?
    try:
        for f in FEATURES:
            val = float(row[f])
            z = (val - stats['medias'][f]) / stats['desvios'][f]
            z = z * FEATURE_WEIGHTS.get(f, 1.0)
            z_scores.append(z)
            
        extra_features = ['time_signature', 'duration_ms', 'explicit']
        for ef in extra_features:
            if ef in stats['medias']:
                val = float(row.get(ef, stats['medias'][ef]))
                z = (val - stats['medias'][ef]) / stats['desvios'][ef]
                z_scores.append(z)
            else:
                z_scores.append(0.0)
        
        # Garante 14 posições
        while len(z_scores) < 14:
            z_scores.append(0.0)
            
        emb_str = "[" + ",".join(map(str, z_scores[:14])) + "]"
        
        # Novo dataset não tem genre, setamos como null ou desconhecido
        genre = "desconhecido"
        
        inserts.append((t_id, t_name, t_artists, genre, emb_str))
        existing.add((t_name_lower, t_artists_lower))
        count += 1
    except Exception as e:
        skipped += 1

    # Batch Insert a cada 10000 para não estourar a RAM
    if len(inserts) >= 10000:
        execute_batch(cur, """
            INSERT INTO tracks (track_id, track_name, artists, track_genre, embedding)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (track_id) DO NOTHING;
        """, inserts)
        conn.commit()
        print(f"Inseridas {count} músicas no banco... (Ignoradas: {skipped})")
        inserts = []

if inserts:
    execute_batch(cur, """
        INSERT INTO tracks (track_id, track_name, artists, track_genre, embedding)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (track_id) DO NOTHING;
    """, inserts)
    conn.commit()
    print(f"Finalizado! Inseridas {count} músicas no total. (Ignoradas: {skipped})")

print("Construindo índice HNSW para buscas em milissegundos...")
try:
    cur.execute("SET maintenance_work_mem = '2GB';")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_tracks_embedding ON tracks USING hnsw (embedding vector_cosine_ops);")
    conn.commit()
    print("Índice construído com sucesso!")
except Exception as e:
    print("Aviso ao construir o índice:", e)
    conn.rollback()

