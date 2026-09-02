"""Cliente do YouTube Music (busca, metadata) e helpers de enriquecimento
(thumbnail/URL de uma faixa), com fallback de capa via iTunes."""
from ytmusicapi import YTMusic

from services.genre_service import get_itunes_cover

yt_client: YTMusic | None = None


def init_yt_client() -> YTMusic:
    """Cria o cliente do YT Music. Chamado uma vez na subida do servidor
    (main.py:lifespan) — antes disso, yt_client fica None."""
    global yt_client
    yt_client = YTMusic()
    return yt_client


def get_yt_info(track_name, artists=""):
    """Busca informações no YT Music e faz fallback de capa na Apple."""
    try:
        clean_query = f"{track_name} {artists}".replace(";", " ").strip()
        res = yt_client.search(clean_query, filter="songs", limit=1)
        if res:
            vid = res[0]['videoId']
            thumbnails = res[0].get('thumbnails', [])
            img_url = thumbnails[-1]['url'] if thumbnails else ""

            if not img_url:
                img_url = get_itunes_cover(track_name, artists)

            return {
                "videoId": vid,
                "url": f"https://music.youtube.com/watch?v={vid}",
                "thumbnail": img_url,
            }
    except Exception as e:
        print(f"Erro YT API: {e}")

    # Se o YT cair, ainda tentamos pegar a capa da Apple
    cover = get_itunes_cover(track_name, artists)
    return {
        "videoId": None,
        "url": None,
        "thumbnail": cover,
    }
