"""Lógica de recomendação: garantir que uma faixa esteja no banco (cold
start via YouTube quando necessário) e buscar faixas similares por
distância de cosseno no embedding (pgvector)."""
import numpy as np
from fastapi import HTTPException
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

import config
from audio_analyzer import analyze_youtube_song
from models import Track
from services import youtube_service
from services.genre_service import genre_needs_refresh, get_genres_combined
from services.youtube_service import get_yt_info
from weights import FEATURE_WEIGHTS


def normalize_features(raw_features: dict) -> list:
    """Converte features brutas (saída do librosa) num vetor normalizado
    (z-score) e ponderado — mesmo formato salvo no embedding do banco."""
    stats = config.NORMALIZATION_STATS
    vec = []
    for feat in config.FEATURES:
        mean = stats['medias'][feat] if stats else 0
        std = stats['desvios'][feat] if stats else 1
        val = raw_features[feat]
        z = (val - mean) / std if std != 0 else 0
        weight = FEATURE_WEIGHTS.get(feat, 1.0)
        vec.append(z * weight)
    return vec


def ensure_track_in_db(db: Session, track_id: str) -> Track:
    """Retorna a faixa do banco; se não existir, faz o cold start completo
    (metadata + download + análise de áudio + identificação de gênero) e
    insere antes de retornar."""
    existing = db.get(Track, track_id)
    if existing:
        return existing

    # --- PROCESSO COLD START ---
    print(f"Música não encontrada no banco. Iniciando download do YT VideoID: {track_id}...")
    try:
        song_info = youtube_service.yt_client.get_song(track_id)
        track_name = song_info['videoDetails']['title']
        artists = song_info['videoDetails']['author']
    except Exception:
        track_name = "Faixa Desconhecida"
        artists = "YouTube"

    try:
        raw_features = analyze_youtube_song(track_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Essa música está bloqueada no YouTube (restrição de idade/região). Tente escolher outra versão da música na pesquisa!",
        )

    normalized_vec = normalize_features(raw_features)
    real_genre = get_genres_combined(track_name, artists, raw_features)

    stmt = pg_insert(Track).values(
        track_id=track_id,
        track_name=track_name,
        artists=artists,
        track_genre=real_genre,
        embedding=normalized_vec,
    ).on_conflict_do_nothing(index_elements=["track_id"])
    db.execute(stmt)
    db.commit()

    # Se outra requisição inseriu a mesma faixa em paralelo (ON CONFLICT DO
    # NOTHING), busca de novo pra pegar o objeto ORM já persistido.
    return db.get(Track, track_id)


def _dedupe_and_enrich(db: Session, rows, top_n: int) -> list:
    """A partir das linhas mais similares, monta a lista final de
    recomendações: limita a 2 faixas por artista principal, enriquece com
    dados do YouTube e re-identifica gênero pendente sob demanda."""
    recomendacoes = []
    artist_counts = {}

    for track, similarity in rows:
        if len(recomendacoes) >= top_n:
            break

        main_artist = track.artists.split(';')[0].strip().lower()
        if artist_counts.get(main_artist, 0) >= 2:
            continue
        artist_counts[main_artist] = artist_counts.get(main_artist, 0) + 1

        yt_data = get_yt_info(track.track_name, track.artists)
        similarity_val = max(0.0, min(1.0, float(similarity)))

        genre = track.track_genre
        if genre_needs_refresh(genre):
            new_genre = get_genres_combined(track.track_name, track.artists)
            if new_genre:
                genre = new_genre
                track.track_genre = new_genre
                db.commit()

        recomendacoes.append({
            "track_id": track.track_id,
            "track_name": track.track_name,
            "artists": track.artists,
            "genre": genre,
            "similarity": similarity_val,
            "thumbnail": yt_data['thumbnail'] if yt_data else None,
            "url": yt_data['url'] if yt_data else None,
        })

    return recomendacoes


def find_similar(db: Session, track: Track, top_n: int) -> dict:
    ref_yt = get_yt_info(track.track_name, track.artists)
    referencia = {
        "track_name": track.track_name,
        "artists": track.artists,
        "genre": track.track_genre,
        "thumbnail": ref_yt['thumbnail'] if ref_yt else None,
        "url": ref_yt['url'] if ref_yt else None,
    }

    similarity_expr = (1 - Track.embedding.cosine_distance(track.embedding)).label("similarity")
    top_rows = (
        db.query(Track, similarity_expr)
        .filter(Track.track_id != track.track_id)
        .order_by(Track.embedding.cosine_distance(track.embedding))
        .limit(top_n * 4)
        .all()
    )

    return {
        "reference": referencia,
        "recommendations": _dedupe_and_enrich(db, top_rows, top_n),
    }


def recommend_for_playlist(db: Session, track_ids: list, top_n: int) -> dict:
    if not track_ids:
        raise HTTPException(400, "Lista de músicas vazia.")

    tracks = [ensure_track_in_db(db, tid) for tid in track_ids]
    centroid_vec = np.mean([list(t.embedding) for t in tracks], axis=0).tolist()

    similarity_expr = (1 - Track.embedding.cosine_distance(centroid_vec)).label("similarity")
    top_rows = (
        db.query(Track, similarity_expr)
        .filter(~Track.track_id.in_(track_ids))
        .order_by(Track.embedding.cosine_distance(centroid_vec))
        .limit(top_n * 4)
        .all()
    )

    return {
        "reference": {
            "track_name": f"Playlist Personalizada ({len(track_ids)} músicas)",
            "artists": "Vários Artistas",
            "genre": "Mix",
            "thumbnail": None,
            "url": None,
        },
        "recommendations": _dedupe_and_enrich(db, top_rows, top_n),
    }
