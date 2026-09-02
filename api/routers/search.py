"""GET /search — busca unificada: YT Music + match no catálogo local."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import Track
from services import youtube_service
from services.genre_service import get_genres_combined, get_itunes_cover, genre_needs_refresh

router = APIRouter()


@router.get("/search")
def search_unified(query: str, limit: int = 5, db: Session = Depends(get_db)):
    """
    Pesquisa rápida: Faz UMA única busca no YT Music para pegar os resultados.
    Depois, faz um match no banco local pelo Nome + Artista para ver se já temos a música (Cache).
    Tempo total estimado: ~1 a 2 segundos.
    """
    lista = []
    try:
        # Busca 1 única vez na API do Youtube (Muito mais rápido!)
        yt_results = youtube_service.yt_client.search(query, filter="songs", limit=limit)

        for track in yt_results:
            vid = track.get('videoId')
            if not vid:
                continue

            track_name = track['title']
            arts = ", ".join([a['name'] for a in track.get('artists', [])])
            img_url = track['thumbnails'][-1]['url'] if 'thumbnails' in track and track['thumbnails'] else None

            if not img_url:
                img_url = get_itunes_cover(track_name, arts)

            # Faz o match no nosso Banco de Dados para ver se a música já existe.
            # Pegamos apenas o primeiro artista para a busca ficar mais tolerante,
            # mas evitar misturar bandas.
            first_artist = track.get('artists', [{'name': ''}])[0]['name']

            db_match = (
                db.query(Track)
                .filter(Track.track_name.ilike(f"%{track_name}%"))
                .filter(Track.artists.ilike(f"%{first_artist}%"))
                .first()
            )

            if db_match:
                db_genre = db_match.track_genre
                if genre_needs_refresh(db_genre):
                    new_genre = get_genres_combined(track_name, arts)
                    if new_genre and new_genre.lower() != "descoberta da web":
                        db_genre = new_genre
                        db_match.track_genre = new_genre
                        db.commit()

                lista.append({
                    "track_id": db_match.track_id,
                    "track_name": track_name,
                    "artists": arts,
                    "genre": db_genre,
                    "thumbnail": img_url,
                    "source": "database",
                })
            else:
                lista.append({
                    "track_id": vid,  # Passamos o ID do YT para fazer o Cold-Start se o usuário clicar
                    "track_name": track_name,
                    "artists": arts,
                    "genre": "Descoberta da Web",
                    "thumbnail": img_url,
                    "source": "youtube",
                })
    except Exception as e:
        print("Erro na busca unificada:", e)

    return {"results": lista}
