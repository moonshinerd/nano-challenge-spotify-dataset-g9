"""GET /play — stream de áudio direto do YouTube (via yt-dlp, sem salvar em disco)."""
import subprocess

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from services import youtube_service

router = APIRouter()


@router.get("/play")
def play_audio(videoId: str = None, query: str = None):
    """Retorna um stream de áudio direto do YouTube."""
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

        def iterfile():
            process = subprocess.Popen(
                ['yt-dlp', '-f', 'bestaudio', '-o', '-', f'https://music.youtube.com/watch?v={videoId}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            try:
                while True:
                    chunk = process.stdout.read(65536)
                    if not chunk:
                        break
                    yield chunk
            finally:
                process.terminate()

        return StreamingResponse(iterfile(), media_type="audio/mp4")
    except HTTPException:
        raise
    except Exception as e:
        print("Erro no streaming:", e)
        raise HTTPException(status_code=500, detail="Erro ao processar áudio.")
