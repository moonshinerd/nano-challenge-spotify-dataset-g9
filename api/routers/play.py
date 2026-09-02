"""GET /play — áudio do YouTube, baixado e cacheado em disco (não em stream
ao vivo): necessário pra a barra de progresso funcionar de verdade.

Antes isso fazia streaming ao vivo via pipe do yt-dlp (subprocess.Popen +
StreamingResponse). Um pipe assim não sabe responder a requisições HTTP
Range, então o <audio> do navegador não consegue "pular" para um ponto do
áudio — ao arrastar a barra de progresso, ele só reabre a conexão do zero,
o que looks like a música reiniciando. Baixando pra um arquivo e servindo
com FileResponse, o Starlette já lida com Range automaticamente, e como
fica em cache por videoId, tocar a mesma música de novo nem baixa de novo.
"""
import os
import tempfile

import yt_dlp
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from services import youtube_service

router = APIRouter()

_CACHE_DIR = os.path.join(tempfile.gettempdir(), "play_cache")


def _download_for_playback(video_id: str) -> str:
    """Baixa (ou reaproveita do cache) o áudio completo de um vídeo e
    retorna o caminho do arquivo mp3 resultante."""
    os.makedirs(_CACHE_DIR, exist_ok=True)
    final_path = os.path.join(_CACHE_DIR, f"{video_id}.mp3")
    if os.path.exists(final_path):
        return final_path

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(_CACHE_DIR, f"{video_id}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'https://music.youtube.com/watch?v={video_id}'])

    return final_path


@router.get("/play")
def play_audio(videoId: str = None, query: str = None):
    """Retorna o arquivo de áudio (com suporte a seek via Range requests)."""
    try:
        if not videoId and query:
            yt_res = youtube_service.yt_client.search(query + " audio", limit=3)
            # Tenta achar um videoId válido (não None)
            for res in yt_res:
                if res.get('videoId'):
                    videoId = res.get('videoId')
                    break

        if not videoId:
            raise HTTPException(status_code=404, detail="Música não encontrada no YT.")

        file_path = _download_for_playback(videoId)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="Erro ao processar áudio.")

        return FileResponse(file_path, media_type="audio/mpeg")
    except HTTPException:
        raise
    except Exception as e:
        print("Erro no streaming:", e)
        raise HTTPException(status_code=500, detail="Erro ao processar áudio.")
