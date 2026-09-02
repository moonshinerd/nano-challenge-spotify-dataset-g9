import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
from ytmusicapi import YTMusic
from sqlalchemy import create_engine, text
from audio_analyzer import analyze_youtube_song
from weights import FEATURE_WEIGHTS

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/spotify")
engine = create_engine(DATABASE_URL)
yt_client = None

# Variáveis globais para normalização
NORMALIZATION_STATS = None
FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
    'duration_ms', 'explicit', 'time_signature',
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global yt_client, NORMALIZATION_STATS
    print("Iniciando API com PostgreSQL/pgvector...")
    
    # Carrega as estatísticas para normalização de músicas novas
    try:
        with open("stats.json", "r") as f:
            NORMALIZATION_STATS = json.load(f)
    except Exception as e:
        print("Aviso: stats.json não encontrado. Rode python save_stats.py no container.")

    yt_client = YTMusic()
    yield

app = FastAPI(lifespan=lifespan, title="Spotify Recommender API (pgvector + Cold Start)")

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

class PlaylistRecommendationRequest(BaseModel):
    track_ids: List[str]
    top_n: int = 10

class AnalyzeRequest(BaseModel):
    query: str
    top_n: int = 5

@app.get("/search")
def search_unified(query: str, limit: int = 5):
    """
    Pesquisa rápida: Faz UMA única busca no YT Music para pegar os resultados.
    Depois, faz um match no banco local pelo Nome + Artista para ver se já temos a música (Cache).
    Tempo total estimado: ~1 a 2 segundos.
    """
    lista = []
    try:
        # Busca 1 única vez na API do Youtube (Muito mais rápido!)
        yt_results = yt_client.search(query, filter="songs", limit=limit)
        
        with engine.connect() as conn:
            for track in yt_results:
                vid = track.get('videoId')
                if not vid: continue
                
                track_name = track['title']
                arts = ", ".join([a['name'] for a in track.get('artists', [])])
                img_url = track['thumbnails'][-1]['url'] if 'thumbnails' in track and track['thumbnails'] else None
                
                if not img_url:
                    img_url = get_itunes_cover(track_name, arts)
                
                # Faz o match no nosso Banco de Dados para ver se a música já existe
                # Pegamos apenas o primeiro artista para a busca ficar mais tolerante, mas evitar misturar bandas
                first_artist = track.get('artists', [{'name': ''}])[0]['name']
                
                db_match = conn.execute(
                    text("""
                        SELECT track_id, track_genre FROM tracks 
                        WHERE track_name ILIKE :nome 
                        AND artists ILIKE :artista
                        LIMIT 1
                    """),
                    {
                        "nome": f"%{track_name}%",
                        "artista": f"%{first_artist}%"
                    }
                ).mappings().first()
                
                if db_match:
                    lista.append({
                        "track_id": db_match['track_id'], # Passamos o ID do Banco para ser instantâneo na hora de recomendar
                        "track_name": track_name,
                        "artists": arts,
                        "genre": db_match['track_genre'],
                        "thumbnail": img_url,
                        "source": "database"
                    })
                else:
                    lista.append({
                        "track_id": vid, # Passamos o ID do YT para fazer o Cold-Start se o usuário clicar
                        "track_name": track_name,
                        "artists": arts,
                        "genre": "Descoberta da Web",
                        "thumbnail": img_url,
                        "source": "youtube"
                    })
    except Exception as e:
        print("Erro na busca unificada:", e)

    return {"results": lista}

import subprocess
from fastapi.responses import RedirectResponse

@app.get("/play")
def play_audio(videoId: str = None, query: str = None):
    """Retorna um redirecionamento para a URL de stream direta de áudio do YouTube."""
    try:
        if not videoId and query:
            yt_res = yt_client.search(query, filter="songs", limit=1)
            if yt_res:
                videoId = yt_res[0].get('videoId')
                
        if not videoId:
            raise HTTPException(status_code=404, detail="Música não encontrada no YT.")
            
        # Pega a URL direta do arquivo de áudio (MP4/M4A/WEBM) dos servidores do Google
        cmd = ['yt-dlp', '-f', 'bestaudio', '-g', f'https://music.youtube.com/watch?v={videoId}']
        url = subprocess.check_output(cmd).decode('utf-8').strip()
        
        return RedirectResponse(url)
    except Exception as e:
        print("Erro no streaming:", e)
        raise HTTPException(status_code=500, detail="Erro ao processar áudio.")

def get_itunes_cover(track_name, artists):
    """Busca a capa do álbum em alta resolução no iTunes."""
    try:
        query = f"{track_name} {artists}".replace(";", " ").replace(" ", "+")
        url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data['resultCount'] > 0:
                img = data['results'][0].get('artworkUrl100', '')
                return img.replace("100x100bb.jpg", "600x600bb.jpg") # Pega versão HQ
    except Exception as e:
        pass
    return None

def get_yt_info(track_name, artists=""):
    """Busca informações no YT Music e faz fallback de capa na Apple."""
    try:
        clean_query = f"{track_name} {artists}".replace(";", " ").strip()
        res = yt_client.search(clean_query, filter="songs", limit=1)
        if res:
            vid = res[0]['videoId']
            thumbnails = res[0].get('thumbnails', [])
            img_url = thumbnails[-1]['url'] if thumbnails else ""
            
            # Se a capa vier vazia ou bugar, pede socorro pra Apple
            if not img_url:
                img_url = get_itunes_cover(track_name, artists)
                
            return {
                "videoId": vid,
                "url": f"https://music.youtube.com/watch?v={vid}",
                "thumbnail": img_url
            }
    except Exception as e:
        print(f"Erro YT API: {e}")
        
    # Se o YT cair, ainda tentamos pegar a capa da Apple
    cover = get_itunes_cover(track_name, artists)
    return {
        "videoId": None,
        "url": None,
        "thumbnail": cover
    }

def find_similar(track_id: str, track_name: str, artists: str, genre: str, embedding: str, top_n: int):
    # Enriquecer recomendação de referência via YT
    ref_yt = get_yt_info(track_name, artists)
    referencia = {
        "track_name": track_name,
        "artists": artists,
        "genre": genre,
        "thumbnail": ref_yt['thumbnail'] if ref_yt else None,
        "url": ref_yt['url'] if ref_yt else None
    }

    # Pega o gênero principal apenas para caso queira usar na UI depois, mas NÃO no SQL
    primary_genre = genre.split(',')[0].strip() if genre else ""

    with engine.connect() as conn:
        top_rows = conn.execute(
            text("""
                SELECT track_id, track_name, artists, track_genre, 
                (1 - (embedding <=> :emb)) AS similarity
                FROM tracks 
                WHERE track_id != :id
                ORDER BY embedding <=> :emb
                LIMIT :limit_extra
            """),
            {"emb": embedding, "id": track_id, "limit_extra": top_n * 4}
        ).mappings().all()
        
    recomendacoes = []
    artist_counts = {}
    
    for r in top_rows:
        if len(recomendacoes) >= top_n:
            break
            
        main_artist = r['artists'].split(';')[0].strip().lower()
        if artist_counts.get(main_artist, 0) >= 2:
            continue
            
        artist_counts[main_artist] = artist_counts.get(main_artist, 0) + 1
        
        yt_data = get_yt_info(r['track_name'], r['artists'])
        
        similarity_val = max(0.0, min(1.0, float(r['similarity'])))
        
        recomendacoes.append({
            "track_id": r['track_id'],
            "track_name": r['track_name'],
            "artists": r['artists'],
            "genre": r['track_genre'],
            "similarity": similarity_val,
            "thumbnail": yt_data['thumbnail'] if yt_data else None,
            "url": yt_data['url'] if yt_data else None
        })
        
    return {
        "reference": referencia,
        "recommendations": recomendacoes
    }


import requests

def guess_genre_from_features(features: dict) -> list:
    """Fallback de IA: Retorna uma lista rica de possíveis subgêneros."""
    energy = features.get('energy', 0.5)
    acousticness = features.get('acousticness', 0.5)
    danceability = features.get('danceability', 0.5)
    tempo = features.get('tempo', 120)
    instrumental = features.get('instrumentalness', 0.0)
    valence = features.get('valence', 0.5)
    speechiness = features.get('speechiness', 0.0)
    liveness = features.get('liveness', 0.15)
    
    genres = []
    
    # Lógica Acústica / Clássica / Ambiente
    if acousticness > 0.8:
        if instrumental > 0.8:
            if tempo < 80: genres.extend(["Ambient", "Lofi", "Música de Fundo"])
            else: genres.extend(["Música Clássica", "Instrumental", "Erudita"])
        else:
            if valence < 0.4: genres.extend(["Folk Triste", "Acústico Melancólico"])
            else: genres.extend(["Folk", "Acústico", "MPB", "Bossa Nova"])
            
    # Lógica de Rap / Hip-Hop
    if speechiness > 0.3:
        if tempo < 100: genres.extend(["Rap", "Hip-Hop", "Lo-Fi Hip Hop"])
        else: genres.extend(["Trap", "Rap Rápido"])
        
    # Lógica Pesada / Rock
    if energy > 0.85 and acousticness < 0.1:
        if tempo > 160 and danceability < 0.5: genres.extend(["Heavy Metal", "Hardcore", "Punk"])
        elif tempo > 120: genres.extend(["Hard Rock", "Rock Alternativo", "Indie Rock"])
        else: genres.extend(["Rock"])
        
    # Lógica de Dança / Eletrônica
    if danceability > 0.75:
        if energy > 0.8:
            if tempo > 120: genres.extend(["House", "Techno", "EDM", "Música Eletrônica"])
            else: genres.extend(["Dance", "Club"])
        elif valence > 0.7:
            genres.extend(["Disco", "Funk", "Groove"])
            
    # Pop / Comercial
    if danceability > 0.6 and energy > 0.6 and acousticness < 0.3:
        if valence > 0.7: genres.extend(["Pop Animado", "Dance-Pop", "Hit de Verão"])
        else: genres.extend(["Pop", "Synth-pop"])
        
    # Reggae / Relax
    if tempo > 60 and tempo < 90 and danceability > 0.6 and energy < 0.6:
        genres.extend(["Reggae", "Dub", "Chillout"])
        
    # Ao Vivo
    if liveness > 0.7:
        genres.append("Ao Vivo / Live")
        
    if not genres:
        genres.extend(["Alternativa", "Indie", "Experimental"])
        
    return genres

import re

# De-Para de Gêneros: Converte os nomes da Apple para o exato formato do Dataset Kaggle
ITUNES_TO_KAGGLE_GENRES = {
    "hip-hop/rap": "hip-hop",
    "hard rock": "hard-rock",
    "forró": "forro",
    "r&b/soul": "r-n-b",
    "new age": "new-age",
    "heavy metal": "heavy-metal",
    "alternative": "indie",
    "world": "world-music",
    "música sertaneja": "sertanejo",
    "brazilian": "brazil",
    "singer/songwriter": "singer-songwriter",
    "indie rock": "indie",
    "indie pop": "indie-pop",
    "rock & roll": "rock-n-roll",
    "children's music": "children",
    "standup comedy": "comedy",
    "death metal/black metal": "black-metal"
}

def get_genres_combined(track_name: str, artists: str, raw_features: dict = None) -> str:
    """
    Tenta buscar no iTunes. Se achar, usa o gênero oficial.
    Somente se falhar totalmente, usamos a IA matemática.
    """
    final_genres = []
    
    # 1. iTunes (Gênero Oficial)
    try:
        # Limpa caracteres especiais mantendo os acentos
        clean_str = f"{track_name} {artists}".replace(";", " ").replace(",", " ").replace("&", " ").replace("(", " ").replace(")", " ")
        # Remove espaços duplicados
        clean_str = " ".join(clean_str.split())
        query = clean_str.replace(" ", "+")
        url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data['resultCount'] > 0:
                genre = data['results'][0].get('primaryGenreName')
                if genre:
                    g_lower = genre.lower()
                    g_mapped = ITUNES_TO_KAGGLE_GENRES.get(g_lower, g_lower)
                    final_genres.append(g_mapped)
    except Exception as e:
        print("Erro ao buscar gênero no iTunes:", e)
        
    # 2. Nossa IA (Apenas se o iTunes falhar completamente)
    if not final_genres and raw_features:
        ai_genres = guess_genre_from_features(raw_features)
        # Pega só os 2 melhores chutes da IA para não poluir
        for g in ai_genres[:2]:
            g_lower = g.lower()
            g_mapped = ITUNES_TO_KAGGLE_GENRES.get(g_lower, g_lower)
            final_genres.append(g_mapped)
                
    if not final_genres:
        final_genres.append("descoberta da web")
        
    return ", ".join(final_genres)

def ensure_track_in_db(track_id: str) -> dict:
    with engine.connect() as conn:
        ref_row = conn.execute(
            text("SELECT track_id, track_name, artists, track_genre, embedding FROM tracks WHERE track_id = :id"),
            {"id": track_id}
        ).mappings().first()
        
    if ref_row:
        return dict(ref_row)
        
    # --- PROCESSO COLD START ---
    print(f"Música não encontrada no banco. Iniciando download do YT VideoID: {track_id}...")
    try:
        song_info = yt_client.get_song(track_id)
        track_name = song_info['videoDetails']['title']
        artists = song_info['videoDetails']['author']
    except Exception as e:
        track_name = "Faixa Desconhecida"
        artists = "YouTube"
        
    try:
        raw_features = analyze_youtube_song(track_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar áudio: {str(e)}")
        
    normalized_vec = []
    for feat in FEATURES:
        mean = NORMALIZATION_STATS['medias'][feat] if NORMALIZATION_STATS else 0
        std = NORMALIZATION_STATS['desvios'][feat] if NORMALIZATION_STATS else 1
        val = raw_features[feat]
        z = (val - mean) / std if std != 0 else 0
        
        # Multiplica o z-score pelo peso da feature!
        weight = FEATURE_WEIGHTS.get(feat, 1.0)
        normalized_vec.append(z * weight)
        
    embedding_str = "[" + ",".join(map(str, normalized_vec)) + "]"
    real_genre = get_genres_combined(track_name, artists, raw_features)
    
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO tracks (track_id, track_name, artists, track_genre, embedding)
                VALUES (:id, :nome, :artistas, :genero, :emb)
                ON CONFLICT (track_id) DO NOTHING
            """),
            {
                "id": track_id,
                "nome": track_name,
                "artistas": artists,
                "genero": real_genre,
                "emb": embedding_str
            }
        )
        conn.commit()
        
    return {
        "track_id": track_id,
        "track_name": track_name,
        "artists": artists,
        "track_genre": real_genre,
        "embedding": embedding_str
    }

@app.post("/recommend")
def recommend_unified(req: RecommendationRequest):
    track = ensure_track_in_db(req.track_id)
    return find_similar(track['track_id'], track['track_name'], track['artists'], track['track_genre'], track['embedding'], req.top_n)

@app.post("/recommend_playlist")
def recommend_playlist(req: PlaylistRecommendationRequest):
    if not req.track_ids:
        raise HTTPException(400, "Lista de músicas vazia.")
        
    embeddings_list = []
    # Garante que todas as músicas da playlist estejam no banco e pega os embeddings
    for tid in req.track_ids:
        track = ensure_track_in_db(tid)
        # O embedding pode vir como string do banco ou do cold_start
        emb_str = track['embedding']
        if isinstance(emb_str, str):
            # Parse string "[0.1, 0.2, ...]" to list of floats
            vec = json.loads(emb_str)
        else:
            # Se for array ou lista (pgvector parse)
            vec = list(emb_str)
        embeddings_list.append(vec)
        
    # Calcula o centroide (média de todos os vetores)
    centroid_vec = np.mean(embeddings_list, axis=0)
    centroid_str = "[" + ",".join(map(str, centroid_vec)) + "]"
    
    # Fazemos uma busca como se o "Centróide" fosse uma música!
    # Criamos IDs para ignorar (os que o usuário selecionou)
    ids_to_ignore = tuple(req.track_ids)
    
    with engine.connect() as conn:
        top_rows = conn.execute(
            text("""
                SELECT track_id, track_name, artists, track_genre, (1 - (embedding <=> :emb)) AS similarity
                FROM tracks 
                WHERE track_id NOT IN :ignore_ids
                ORDER BY embedding <=> :emb
                LIMIT :limit_extra
            """),
            {"emb": centroid_str, "ignore_ids": ids_to_ignore, "limit_extra": req.top_n * 4}
        ).mappings().all()

    recomendacoes = []
    artist_counts = {}
    
    for r in top_rows:
        if len(recomendacoes) >= req.top_n:
            break
            
        main_artist = r['artists'].split(';')[0].strip().lower()
        if artist_counts.get(main_artist, 0) >= 2:
            continue
            
        artist_counts[main_artist] = artist_counts.get(main_artist, 0) + 1
        
        yt_data = get_yt_info(r['track_name'], r['artists'])
        similarity_val = max(0.0, min(1.0, float(r['similarity'])))
        
        recomendacoes.append({
            "track_id": r['track_id'],
            "track_name": r['track_name'],
            "artists": r['artists'],
            "genre": r['track_genre'],
            "similarity": similarity_val,
            "thumbnail": yt_data['thumbnail'] if yt_data else None,
            "url": yt_data['url'] if yt_data else None
        })

    return {
        "reference": {
            "track_name": f"Playlist Personalizada ({len(req.track_ids)} músicas)",
            "artists": "Vários Artistas",
            "genre": "Mix",
            "thumbnail": None,
            "url": None
        },
        "recommendations": recomendacoes
    }
