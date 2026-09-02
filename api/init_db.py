import sys
import os
import pandas as pd
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

sys.path.insert(0, '/src/shared')
from dados import carregar_dataset, construir_df_unique

# Usando psycopg2 diretamente para lidar com cast de vetores de forma mais fácil
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
    print("Carregando CSV...")
    dataset_path = Path("/data/raw/dataset.csv")
    df = carregar_dataset(dataset_path)
    df_unique = construir_df_unique(df)
    df_unique['explicit'] = df_unique['explicit'].astype(int)

    print("Calculando matriz normalizada (z-score)...")
    from weights import FEATURE_WEIGHTS
    
    medias = df_unique[FEATURES].mean()
    desvios = df_unique[FEATURES].std()
    
    matriz_normalizada = ((df_unique[FEATURES] - medias) / desvios)
    
    # Aplicando os pesos nas features
    for feat in FEATURES:
        weight = FEATURE_WEIGHTS.get(feat, 1.0)
        matriz_normalizada[feat] = matriz_normalizada[feat] * weight
        
    matriz_normalizada = matriz_normalizada.to_numpy(dtype=float)
    
    print("Preparando dados para inserção no banco...")
    # Extrair track_id corretamente
    track_ids = df_unique['track_id'].apply(lambda x: x.split(', ')[0] if isinstance(x, str) else x).tolist()
    track_names = df_unique['track_name'].tolist()
    artists = df_unique['artists'].tolist()
    track_genres = df_unique['track_genre'].tolist()
    
    # Prepara lista de tuplas para inserção em lote
    # Converte o numpy array de volta para list para o psycopg2
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
        
    print("Conectando ao PostgreSQL...")
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    cur = conn.cursor()
    
    print(f"Inserindo {len(data_to_insert)} músicas no banco de forma otimizada...")
    # Inserção em massa com cast explícito para vetor
    insert_query = """
        INSERT INTO tracks (track_id, track_name, artists, track_genre, embedding)
        VALUES %s
        ON CONFLICT (track_id) DO NOTHING
    """
    
    # execute_values lida muito bem com grandes lotes (page_size 1000)
    # Precisamos do cast ::vector no template? execute_values usa %s para os valores,
    # psycopg2 passará a string e o postgres pode fazer o cast automático na tabela tipada,
    # mas para garantir podemos omitir o cast e deixar o postgresolicitar.
    # Como a tabela já tem 'embedding vector(14)', enviar texto " [1,2,3] " faz cast implícito no psycopg2 em DML simples.
    # Mas execute_values cria a query.
    # A melhor forma é usar execute_values normal:
    
    execute_values(cur, insert_query, data_to_insert, page_size=2000)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Banco de dados populado com sucesso!")

if __name__ == "__main__":
    init_db()
