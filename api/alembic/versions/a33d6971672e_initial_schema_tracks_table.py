"""initial schema (tracks table)

Revision ID: a33d6971672e
Revises:
Create Date: 2026-09-02 19:55:27.313412

Migração inicial: reflete o schema já criado pelos scripts de bootstrap
(api/init_db.py e api/ingest_1m.py). Toda a DDL aqui é idempotente
(IF NOT EXISTS) de propósito — essa migração é segura tanto para um banco
novo do zero quanto para o banco de desenvolvimento atual, que já tem a
tabela/índice criados.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "a33d6971672e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensão pgvector - necessária antes de qualquer coluna vector(...)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS tracks (
            track_id VARCHAR PRIMARY KEY,
            track_name VARCHAR,
            artists VARCHAR,
            track_genre VARCHAR,
            embedding vector(14)
        )
        """
    )

    # CONCURRENTLY evita travar INSERT/UPDATE/DELETE na tabela enquanto o
    # índice é construído (importante: uma tabela com centenas de milhares
    # de linhas pode levar minutos para indexar, e sem CONCURRENTLY isso
    # bloqueia qualquer cold-start de música nova nesse meio tempo). Por
    # isso não pode rodar dentro da transação da migration.
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tracks_embedding "
            "ON tracks USING hnsw (embedding vector_cosine_ops)"
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_tracks_embedding")
    op.execute("DROP TABLE IF EXISTS tracks")
