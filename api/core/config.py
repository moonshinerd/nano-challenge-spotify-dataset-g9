"""Configuração e constantes compartilhadas pela aplicação."""
import json

# Ordem das features do vetor de embedding — precisa bater com a ordem usada
# em ingest_1m.py, init_db.py e export_web_tracks.py na hora de montar/ler o
# embedding, e com EMBEDDING_DIM em models.py.
FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
    'duration_ms', 'explicit', 'time_signature',
]

# Estatísticas (média/desvio padrão) de cada feature no dataset original,
# usadas para normalizar (z-score) o embedding de músicas novas (cold
# start). Carregado uma vez na subida do servidor (ver main.py:lifespan).
NORMALIZATION_STATS = None


def load_normalization_stats(path: str = "stats.json"):
    """Carrega stats.json (gerado por save_stats.py) para NORMALIZATION_STATS."""
    global NORMALIZATION_STATS
    try:
        with open(path, "r") as f:
            NORMALIZATION_STATS = json.load(f)
    except Exception:
        print(f"Aviso: {path} não encontrado. Rode 'python save_stats.py' no container.")
    return NORMALIZATION_STATS
