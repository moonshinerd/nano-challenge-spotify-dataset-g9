import sys
import os
import pandas as pd
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

sys.path.insert(0, '/src/shared')
sys.path.insert(0, '/app')  # scripts/ roda fora de api/; /app é onde o Dockerfile monta api/ (para importar core/weights.py)
from dados import carregar_dataset, construir_df_unique

DB_HOST = "db"
DB_NAME = "spotify"
DB_USER = "user"
DB_PASS = "password"

FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
    'duration_ms', 'explicit', 'time_signature',
]

def init_db():
    # Schema (extensão vector, tabela, índice HNSW) é responsabilidade do
    # Alembic agora (alembic/versions/..._initial_schema_tracks_table.py) —
    # roda como passo separado antes deste script (ver docker-compose.yml).
    # Este script cuida só da carga de dados (seed) do dataset original.
    print("Conectando ao PostgreSQL...")
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()

    print("Carregando CSV original (Base Kaggle)...")
    dataset_path = Path("/data/raw/dataset.csv")
    if not dataset_path.exists():
        print("Arquivo base não encontrado. Pulando importação original.")
        return

    df = carregar_dataset(dataset_path)
    df_unique = construir_df_unique(df)
    df_unique['explicit'] = df_unique['explicit'].astype(int)

    print("Calculando matriz normalizada (z-score)...")
    from core.weights import FEATURE_WEIGHTS
    
    medias = df_unique[FEATURES].mean()
    desvios = df_unique[FEATURES].std()
    
    matriz_normalizada = ((df_unique[FEATURES] - medias) / desvios)
    
    for feat in FEATURES:
        weight = FEATURE_WEIGHTS.get(feat, 1.0)
        matriz_normalizada[feat] = matriz_normalizada[feat] * weight
        
    matriz_normalizada = matriz_normalizada.to_numpy(dtype=float)
    
    print("Preparando dados para inserção no banco...")
    track_ids = df_unique['track_id'].apply(lambda x: x.split(', ')[0] if isinstance(x, str) else x).tolist()
    track_names = df_unique['track_name'].tolist()
    artists = df_unique['artists'].tolist()
    track_genres = df_unique['track_genre'].tolist()
    
    data_to_insert = []
    for i in range(len(track_ids)):
        vec_str = "[" + ",".join(map(str, matriz_normalizada[i])) + "]"
        data_to_insert.append((
            track_ids[i],
            track_names[i],
            artists[i],
            track_genres[i],
            vec_str
        ))
        
    print(f"Inserindo {len(data_to_insert)} músicas originais no banco...")
    insert_query = """
        INSERT INTO tracks (track_id, track_name, artists, track_genre, embedding)
        VALUES %s
        ON CONFLICT (track_id) DO NOTHING
    """
    
    execute_values(cur, insert_query, data_to_insert, page_size=2000)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Banco de dados populado com sucesso (Base Original)!")

if __name__ == "__main__":
    init_db()
