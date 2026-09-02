"""
Exporta para CSV as músicas que foram adicionadas ao banco via "cold start"
(busca do usuário -> download do YouTube -> análise de áudio), ou seja,
músicas que NÃO fazem parte de nenhum dos datasets originais (dataset.csv
ou dataset_1M_clean.csv.gz).

Essas músicas são identificadas pelo formato do track_id: o cold start em
main.py (ensure_track_in_db) usa o videoId do YouTube como track_id, que
sempre tem 11 caracteres (letras, números, "_" e "-"). Os datasets originais
usam IDs do Spotify, que sempre têm 22 caracteres.

O script gera dois CSVs, ambos com merge incremental (sem duplicar, sem
sobrescrever o que já existe):

1. /data/raw/musicas_web_descobertas.csv — músicas de descoberta web, com
   features de áudio (denormalizadas do embedding) e gênero. Para essas,
   o script faz "backfill" ativo: se ainda não têm gênero, consulta o
   iTunes/IA (mesma lógica de lazy-load do /recommend) e já atualiza tanto
   o banco quanto o CSV.

2. /data/raw/generos_dataset_identificados.csv — apenas track_id + gênero,
   para músicas do dataset de 1M cujo gênero já foi resolvido via lazy load
   em algum momento (quando apareceram em /search, /recommend ou
   /recommend_playlist). Aqui o script NÃO dispara buscas novas no iTunes
   (seriam ~740 mil chamadas) — só exporta o que o uso normal do app já
   resolveu, permitindo mesclar de volta no dataset original depois.

Uso (dentro do container da API):
    docker compose exec api python export_web_tracks.py
"""
import json
import os
import sys
import csv
from pathlib import Path

from sqlalchemy import create_engine, text

# Reaproveita a lógica de gênero e os pesos já usados pela API,
# sem disparar o lifespan do FastAPI (get_genres_combined não depende do yt_client).
from services.genre_service import get_genres_combined
from config import FEATURES
from weights import FEATURE_WEIGHTS

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/spotify")
engine = create_engine(DATABASE_URL)

STATS_PATH = Path("stats.json")
OUTPUT_CSV = Path("/data/raw/musicas_web_descobertas.csv")
DATASET_GENRES_CSV = Path("/data/raw/generos_dataset_identificados.csv")

# videoId do YouTube: sempre 11 caracteres [A-Za-z0-9_-]
YT_ID_REGEX = r"^[A-Za-z0-9_-]{11}$"

CSV_COLUMNS = [
    "track_id", "track_name", "artists", "track_genre",
    "danceability", "energy", "key", "loudness", "mode", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo",
    "duration_ms", "explicit", "time_signature",
]


def load_stats():
    if not STATS_PATH.exists():
        print("stats.json não encontrado — rode save_stats.py antes.")
        sys.exit(1)
    with open(STATS_PATH, "r") as f:
        return json.load(f)


def backfill_genres(conn):
    """
    Atualiza track_genre apenas para as músicas de descoberta web (cold start,
    track_id = videoId do YouTube) que ainda estão sem gênero.

    Importante: NÃO mexe nas músicas dos datasets originais (dataset.csv /
    dataset_1M_clean.csv.gz) — é normal e esperado que o dataset de 1M não
    tenha gênero; essas são resolvidas sob demanda (lazy load) quando
    aparecem para o usuário em /recommend e /recommend_playlist.
    """
    rows = conn.execute(text(f"""
        SELECT track_id, track_name, artists
        FROM tracks
        WHERE track_id ~ '{YT_ID_REGEX}'
          AND (
                track_genre IS NULL
             OR TRIM(track_genre) = ''
             OR LOWER(track_genre) IN ('descoberta da web', 'desconhecido', 'desconhecida')
          )
    """)).mappings().all()

    if not rows:
        print("Backfill de gênero: nada para atualizar (músicas web já têm gênero).")
        return 0

    print(f"Backfill de gênero: {len(rows)} música(s) de descoberta web sem gênero. Consultando iTunes/IA...")
    updated = 0
    for i, row in enumerate(rows, 1):
        new_genre = get_genres_combined(row["track_name"], row["artists"])
        if new_genre and new_genre.lower() != "descoberta da web":
            conn.execute(
                text("UPDATE tracks SET track_genre = :g WHERE track_id = :id"),
                {"g": new_genre, "id": row["track_id"]},
            )
            updated += 1
        if i % 25 == 0:
            print(f"  ...{i}/{len(rows)} processadas ({updated} atualizadas até agora)")
    print(f"Backfill de gênero concluído: {updated}/{len(rows)} atualizada(s).")
    return updated


def fetch_web_tracks(conn):
    """Busca no banco as músicas cujo track_id é um videoId do YouTube (cold start)."""
    rows = conn.execute(text(f"""
        SELECT track_id, track_name, artists, track_genre, embedding
        FROM tracks
        WHERE track_id ~ '{YT_ID_REGEX}'
        ORDER BY track_id
    """)).mappings().all()
    return rows


def denormalize(embedding_str: str, stats: dict) -> dict:
    """Reverte o z-score ponderado salvo no banco para valores aproximados das features originais."""
    # embedding vem como "[v1,v2,...]" (pgvector) -> lista de floats
    values = [float(v) for v in embedding_str.strip("[]").split(",")]
    medias = stats["medias"]
    desvios = stats["desvios"]
    raw = {}
    for feat, z_weighted in zip(FEATURES, values):
        weight = FEATURE_WEIGHTS.get(feat, 1.0)
        z = z_weighted / weight if weight else 0.0
        std = desvios.get(feat, 1) or 1
        mean = medias.get(feat, 0)
        raw[feat] = z * std + mean
    return raw


def fetch_resolved_dataset_genres(conn):
    """
    Busca no banco os gêneros já identificados (via lazy load no /search,
    /recommend e /recommend_playlist) para músicas do dataset de 1M — essas
    entram no banco sem gênero e vão sendo preenchidas conforme aparecem
    para o usuário. NÃO dispara novas buscas no iTunes aqui: só exporta o
    que já foi resolvido, para não sobrecarregar a API externa.
    """
    rows = conn.execute(text(f"""
        SELECT track_id, track_genre
        FROM tracks
        WHERE track_id !~ '{YT_ID_REGEX}'
          AND track_genre IS NOT NULL
          AND TRIM(track_genre) != ''
          AND LOWER(track_genre) NOT IN ('descoberta da web', 'desconhecido', 'desconhecida')
        ORDER BY track_id
    """)).mappings().all()
    return rows


def export_resolved_dataset_genres(conn):
    """Escreve/atualiza generos_dataset_identificados.csv (track_id, track_genre)."""
    rows = fetch_resolved_dataset_genres(conn)
    existing_ids = load_existing_ids(DATASET_GENRES_CSV)
    is_new_file = not DATASET_GENRES_CSV.exists()
    new_rows = [r for r in rows if r["track_id"] not in existing_ids]

    if not new_rows and not is_new_file:
        print("Gêneros do dataset: nada novo para adicionar.")
        return

    DATASET_GENRES_CSV.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if is_new_file else "a"
    with open(DATASET_GENRES_CSV, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["track_id", "track_genre"])
        if is_new_file:
            writer.writeheader()
        for r in new_rows:
            writer.writerow({"track_id": r["track_id"], "track_genre": r["track_genre"]})

    print(f"{'Criado' if is_new_file else 'Atualizado'}: {DATASET_GENRES_CSV} (+{len(new_rows)} gênero(s) novo(s), total {len(rows)} resolvidos).")


def load_existing_ids(path: Path) -> set:
    if not path.exists():
        return set()
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["track_id"] for row in reader}


def main():
    stats = load_stats()

    with engine.begin() as conn:
        backfill_genres(conn)

    with engine.connect() as conn:
        export_resolved_dataset_genres(conn)

    with engine.connect() as conn:
        web_tracks = fetch_web_tracks(conn)

    print(f"Encontradas {len(web_tracks)} música(s) de descoberta web (fora dos datasets originais).")

    existing_ids = load_existing_ids(OUTPUT_CSV)
    is_new_file = not OUTPUT_CSV.exists()
    new_rows = [t for t in web_tracks if t["track_id"] not in existing_ids]

    if not new_rows and not is_new_file:
        print("Nenhuma música nova para adicionar ao CSV.")
        return

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if is_new_file else "a"
    with open(OUTPUT_CSV, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if is_new_file:
            writer.writeheader()
        for t in new_rows:
            raw = denormalize(t["embedding"], stats)
            writer.writerow({
                "track_id": t["track_id"],
                "track_name": t["track_name"],
                "artists": t["artists"],
                "track_genre": t["track_genre"],
                **{k: round(v, 6) for k, v in raw.items()},
            })

    print(f"{'Criado' if is_new_file else 'Atualizado'}: {OUTPUT_CSV} (+{len(new_rows)} música(s) novas).")


if __name__ == "__main__":
    main()
