"""
Carrega de volta no banco os dois CSVs que export_web_tracks.py gera:

1. data/raw/musicas_web_descobertas.csv — músicas descobertas via cold
   start (busca do usuário -> YouTube -> análise de áudio) que não fazem
   parte de nenhum dataset original. Sem esse script, elas ficam só no
   commit do CSV: numa máquina nova, o setup carrega dataset.csv e
   dataset_1M_clean.csv.gz, mas NUNCA insere essas faixas de volta — cada
   pessoa que roda `docker compose up --build` teria que redescobrir essas
   músicas do zero (refazendo download + análise) pra elas aparecerem no
   catálogo.

2. data/raw/generos_dataset_identificados.csv — gêneros do dataset de 1M
   já resolvidos via lazy load (iTunes/IA) em algum uso anterior do app.
   Sem esse script, cada pessoa nova começaria com esses ~80 mil+ gêneros
   como "desconhecido" de novo, até alguém buscar cada faixa de novo.

Roda como parte do setup (ver docker-compose.yml), depois de ingest_1m.py
— assim tanto um clone novo do repositório quanto o ambiente de quem já
vinha usando ficam com o mesmo catálogo/gêneros já descobertos.

Uso manual (dentro do container):
    docker compose exec api python /scripts/load_exported_tracks.py
"""
import csv
import os
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

sys.path.insert(0, '/app')  # scripts/ roda fora de api/; /app é onde o Dockerfile monta api/
from core.config import FEATURES, load_normalization_stats
from core.weights import FEATURE_WEIGHTS

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/spotify")
WEB_TRACKS_CSV = Path("/data/raw/musicas_web_descobertas.csv")
DATASET_GENRES_CSV = Path("/data/raw/generos_dataset_identificados.csv")


def normalize_features(raw_features: dict, stats: dict) -> list:
    """Mesmo cálculo de services/recommend_service.py — duplicado aqui de
    propósito: este script roda fora do processo da API (via scripts/),
    então não depende da inicialização do FastAPI nem de rede pra API."""
    vec = []
    for feat in FEATURES:
        mean = stats['medias'][feat] if stats else 0
        std = stats['desvios'][feat] if stats else 1
        val = float(raw_features[feat])
        z = (val - mean) / std if std != 0 else 0
        weight = FEATURE_WEIGHTS.get(feat, 1.0)
        vec.append(z * weight)
    return vec


def load_web_tracks(cur, stats: dict):
    if not WEB_TRACKS_CSV.exists():
        print(f"{WEB_TRACKS_CSV} não encontrado — nada de músicas web pra carregar.")
        return

    with open(WEB_TRACKS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("musicas_web_descobertas.csv está vazio.")
        return

    data_to_insert = []
    for row in rows:
        raw_features = {feat: row[feat] for feat in FEATURES}
        vec = normalize_features(raw_features, stats)
        emb_str = "[" + ",".join(map(str, vec)) + "]"
        data_to_insert.append((
            row["track_id"], row["track_name"], row["artists"], row["track_genre"], emb_str,
        ))

    inserted = execute_values(cur, """
        INSERT INTO tracks (track_id, track_name, artists, track_genre, embedding)
        VALUES %s
        ON CONFLICT (track_id) DO NOTHING
        RETURNING track_id
    """, data_to_insert, fetch=True)
    print(f"Músicas de descoberta web: {len(inserted)} nova(s) inserida(s) (de {len(data_to_insert)} no CSV; o resto já existia no banco).")


def load_resolved_genres(cur):
    if not DATASET_GENRES_CSV.exists():
        print(f"{DATASET_GENRES_CSV} não encontrado — nada de gênero resolvido pra aplicar.")
        return

    with open(DATASET_GENRES_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("generos_dataset_identificados.csv está vazio.")
        return

    data = [(row["track_id"], row["track_genre"]) for row in rows]

    # UPDATE em massa via tabela temporária: bem mais rápido que um UPDATE
    # por linha para dezenas de milhares de registros.
    cur.execute("""
        CREATE TEMP TABLE tmp_genres (track_id VARCHAR, track_genre VARCHAR) ON COMMIT DROP
    """)
    execute_values(cur, "INSERT INTO tmp_genres (track_id, track_genre) VALUES %s", data)
    cur.execute("""
        UPDATE tracks
        SET track_genre = tmp_genres.track_genre
        FROM tmp_genres
        WHERE tracks.track_id = tmp_genres.track_id
          AND (tracks.track_genre IS NULL OR tracks.track_genre = '' OR LOWER(tracks.track_genre) = 'desconhecido')
    """)
    print(f"Gêneros do dataset: {cur.rowcount} atualizado(s) a partir do CSV (de {len(data)} disponíveis).")


def main():
    stats = load_normalization_stats()
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        load_web_tracks(cur, stats)
        load_resolved_genres(cur)
        conn.commit()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
