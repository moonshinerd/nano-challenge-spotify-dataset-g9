import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ytmusicapi import YTMusic
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/spotify")
engine = create_engine(DATABASE_URL)
yt_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global yt_client
    print("Iniciando API com PostgreSQL/pgvector...")
    
    # Verifica se o banco já foi populado
    with engine.connect() as conn:
        try:
            res = conn.execute(text("SELECT count(*) FROM tracks")).scalar()
            print(f"✅ Banco de dados contém {res} faixas prontas para recomendação.")
        except Exception as e:
            print("⚠️ A tabela 'tracks' ainda não existe ou está vazia. Execute 'python init_db.py' no container.")
            
    yt_client = YTMusic()
    yield

app = FastAPI(lifespan=lifespan, title="Spotify Recommender API (pgvector)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    track_id: str
    top_n: int = 5

@app.get("/search")
def search_pg(query: str, limit: int = 5):
    """Busca músicas no PostgreSQL usando ILIKE e traz capas do YT Music"""
    query = f"%{query}%"
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT track_id, track_name, artists, track_genre 
                FROM tracks 
                WHERE track_name ILIKE :q OR artists ILIKE :q 
                LIMIT :lim
            """), 
            {"q": query, "lim": limit}
        ).mappings().all()
        
    lista = []
    for r in result:
        yt_data = get_yt_info(r['track_name'], r['artists'])
        lista.append({
            "track_id": r['track_id'],
            "track_name": r['track_name'],
            "artists": r['artists'],
            "genre": r['track_genre'],
            "thumbnail": yt_data['thumbnail']
        })
    return {"results": lista}

def get_yt_info(track_name, artists):
    try:
        res = yt_client.search(f"{track_name} {artists}", filter="songs", limit=1)
        if res:
            track = res[0]
            img_url = track['thumbnails'][-1]['url'] if 'thumbnails' in track and track['thumbnails'] else None
            vid = track.get('videoId')
            return {
                "thumbnail": img_url,
                "url": f"https://music.youtube.com/watch?v={vid}" if vid else None
            }
    except Exception as e:
        print(f"Erro YT API: {e}")
    return {"thumbnail": None, "url": None}

@app.post("/recommend")
def recommend_pg(req: RecommendationRequest):
    """Calcula a similaridade usando o operador <=> do pgvector diretamente no SQL"""
    with engine.connect() as conn:
        # 1. Busca o embedding da música de referência
        ref_row = conn.execute(
            text("SELECT track_name, artists, embedding FROM tracks WHERE track_id = :id"),
            {"id": req.track_id}
        ).mappings().first()
        
        if not ref_row:
            raise HTTPException(status_code=404, detail="Música não encontrada")
            
        ref_yt = get_yt_info(ref_row['track_name'], ref_row['artists'])
        referencia = {
            "track_name": ref_row['track_name'],
            "artists": ref_row['artists'],
            "thumbnail": ref_yt['thumbnail'],
            "url": ref_yt['url']
        }

        # 2. Busca as top N mais próximas usando Cosine Distance (<=>) do pgvector
        # O pgvector retorna a 'distância', então similaridade = 1 - distância
        top_rows = conn.execute(
            text("""
                SELECT track_id, track_name, artists, (1 - (embedding <=> :emb)) AS similarity
                FROM tracks 
                WHERE track_id != :id
                ORDER BY embedding <=> :emb
                LIMIT :top
            """),
            {"emb": ref_row['embedding'], "id": req.track_id, "top": req.top_n}
        ).mappings().all()

    # 3. Enriquecer recomendações
    recomendacoes = []
    for r in top_rows:
        yt_data = get_yt_info(r['track_name'], r['artists'])
        recomendacoes.append({
            "track_id": r['track_id'],
            "track_name": r['track_name'],
            "artists": r['artists'],
            "similarity": float(r['similarity']),
            "thumbnail": yt_data['thumbnail'],
            "url": yt_data['url']
        })
        
    return {
        "reference": referencia,
        "recommendations": recomendacoes
    }
