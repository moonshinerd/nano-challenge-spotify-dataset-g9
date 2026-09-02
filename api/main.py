"""Ponto de entrada da API: cria o app FastAPI, configura CORS, sobe as
dependências externas (stats de normalização, cliente do YT Music, warmup
do librosa) e registra os routers. A lógica de negócio vive em services/,
os modelos de banco em models.py, e os schemas de request em schemas.py."""
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from routers import play, recommend, search
from services import youtube_service


def _warmup_librosa():
    """Roda a extração de features numa vez com um áudio sintético curto,
    em background, assim que o servidor sobe.

    librosa usa funções decoradas com @numba.jit, que compilam (JIT) na
    primeira chamada de cada processo — isso sozinho pode levar dezenas de
    segundos. Sem esse warmup, é o primeiro usuário a buscar uma música nova
    (cold start) que paga esse custo; rodando em background na subida, ele
    já acontece antes de qualquer request real (e não bloqueia /search nem
    músicas já catalogadas nesse meio tempo).
    """
    try:
        import tempfile
        import time

        import numpy as np
        import soundfile as sf

        from audio_analyzer import extract_features

        t0 = time.time()
        sr = 22050
        dummy_audio = (np.random.randn(sr * 2) * 0.1).astype(np.float32)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            sf.write(tmp.name, dummy_audio, sr)
            extract_features(tmp.name)
        print(f"Warmup do librosa/numba concluído em {time.time() - t0:.1f}s.")
    except Exception as e:
        print("Aviso: warmup do librosa falhou (não é crítico):", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando API com PostgreSQL/pgvector...")
    config.load_normalization_stats()
    youtube_service.init_yt_client()
    threading.Thread(target=_warmup_librosa, daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan, title="Spotify Recommender API (pgvector + Cold Start)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(play.router)
app.include_router(recommend.router)
