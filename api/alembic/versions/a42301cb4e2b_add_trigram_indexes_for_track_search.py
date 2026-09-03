"""add trigram indexes for track search

Revision ID: a42301cb4e2b
Revises: a33d6971672e
Create Date: 2026-09-02

O /search faz até 5 buscas por (nome, artista) usando ILIKE '%...%' contra
a tabela tracks (~822 mil linhas). Sem índice, cada uma dessas é uma
varredura sequencial completa (~900ms medido via EXPLAIN ANALYZE) — até
~4.5s+ só nisso, e mais sob concorrência. Índices GIN com pg_trgm resolvem
ILIKE com wildcard nas duas pontas ('%termo%'), que um índice B-tree comum
não consegue usar.
"""
from alembic import op

revision = "a42301cb4e2b"
down_revision = "a33d6971672e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # CONCURRENTLY (mesmo motivo do índice HNSW): não trava a tabela pra
    # escrita enquanto o índice é construído.
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tracks_name_trgm "
            "ON tracks USING gin (track_name gin_trgm_ops)"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tracks_artists_trgm "
            "ON tracks USING gin (artists gin_trgm_ops)"
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_tracks_name_trgm")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_tracks_artists_trgm")
