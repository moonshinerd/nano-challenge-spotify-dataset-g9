"""Modelos SQLAlchemy (ORM) que espelham o schema do banco."""
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Index, String

from core.database import Base

# Número de dimensões do vetor de embedding (features de áudio ponderadas
# e normalizadas por z-score — ver weights.py e config.FEATURES).
EMBEDDING_DIM = 14


class Track(Base):
    """Uma faixa: do dataset original, do dataset de 1M ou descoberta via
    cold-start (busca do usuário -> YouTube -> análise de áudio).

    O tipo de origem de uma faixa não é armazenado explicitamente; é inferido
    pelo formato do track_id (ver services/track_origin.py): IDs do Spotify
    (datasets) têm 22 caracteres, videoIds do YouTube (cold-start) têm 11.
    """
    __tablename__ = "tracks"

    track_id = Column(String, primary_key=True)
    track_name = Column(String)
    artists = Column(String)
    track_genre = Column(String)
    embedding = Column(Vector(EMBEDDING_DIM))

    __table_args__ = (
        # Declarado aqui só para o Alembic reconhecer o índice como
        # intencional (autogenerate) e não tentar removê-lo em diffs
        # futuros. A criação real acontece via CONCURRENTLY na migration
        # (ver alembic/versions/..._initial_schema_tracks_table.py) — sem
        # isso, um CREATE INDEX comum travaria a tabela para escritas
        # durante a construção do índice.
        Index(
            "idx_tracks_embedding",
            embedding,
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        # Índices GIN/trigram usados pelo /search (ILIKE '%termo%' em
        # track_name/artists) — criação real via CONCURRENTLY na migration
        # a42301cb4e2b_add_trigram_indexes_for_track_search.py.
        Index(
            "idx_tracks_name_trgm",
            track_name,
            postgresql_using="gin",
            postgresql_ops={"track_name": "gin_trgm_ops"},
        ),
        Index(
            "idx_tracks_artists_trgm",
            artists,
            postgresql_using="gin",
            postgresql_ops={"artists": "gin_trgm_ops"},
        ),
    )
