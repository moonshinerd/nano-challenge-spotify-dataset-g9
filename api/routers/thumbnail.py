"""GET /thumbnail — faz proxy de imagens de capa (YouTube/iTunes).

Existe porque algumas redes/navegadores (bloqueadores de anúncio por DNS,
modo privacidade em navegadores mobile) bloqueiam domínios de CDN do Google
como googleusercontent.com, tratando-os como rastreamento. Servindo a
imagem a partir do nosso próprio domínio, o navegador não sabe (nem
precisa saber) que a origem real é outra — contorna esse tipo de bloqueio.

Só permite proxy para os hosts de imagem que a API realmente usa (YouTube e
Apple/iTunes), pra não virar um proxy aberto pra qualquer URL.
"""
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, HTTPException, Response

router = APIRouter()

_ALLOWED_HOSTS = (
    "googleusercontent.com",
    "ytimg.com",
    "mzstatic.com",
)


def _host_allowed(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return any(host == h or host.endswith("." + h) for h in _ALLOWED_HOSTS)


@router.get("/thumbnail")
def proxy_thumbnail(url: str):
    if not url.startswith(("http://", "https://")) or not _host_allowed(url):
        raise HTTPException(status_code=400, detail="Host de imagem não permitido.")

    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
    except Exception:
        raise HTTPException(status_code=502, detail="Não foi possível buscar a imagem.")

    return Response(
        content=res.content,
        media_type=res.headers.get("content-type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=86400"},
    )
