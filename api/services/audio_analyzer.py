import os
import librosa
import numpy as np
import yt_dlp
import uuid

def download_audio_snippet(video_id: str, duration: int = 300) -> str:
    """Baixa um trecho de áudio do YouTube usando yt-dlp e ffmpeg."""
    out_file = f"/tmp/{uuid.uuid4().hex}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': out_file + '.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        # Duração padrão de 300s (5min) para o librosa ter mais áudio para
        # analisar. Antes esse valor ficava fixo no código (ignorando o
        # parâmetro `duration`); agora usa o parâmetro normalmente, então
        # dá pra ajustar chamando download_audio_snippet(video_id, duration=N).
        'postprocessor_args': [
            '-ss', '00:00:00',
            '-t', str(duration)
        ],
        'quiet': True,
        'no_warnings': True
    }

    # Tenta music.youtube.com primeiro (resolve a maioria das faixas
    # exclusivas do YT Music, que costumam falhar com "Video unavailable"
    # pela URL genérica), e cai pra www.youtube.com como fallback — algumas
    # faixas dão o caminho inverso: bloqueadas/indisponíveis no YT Music mas
    # com uma versão normal (às vezes de outro canal/upload) acessível pelo
    # YouTube comum.
    urls = [
        f"https://music.youtube.com/watch?v={video_id}",
        f"https://www.youtube.com/watch?v={video_id}",
    ]

    last_error = None
    for url in urls:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return out_file + '.mp3'
        except Exception as e:
            last_error = e
            print(f"Erro ao baixar áudio de {url}: {e}")

    print(f"Falha em todas as fontes para {video_id}. Último erro: {last_error}")
    return None

def extract_features(audio_path: str):
    """
    Extrai as features do áudio usando Librosa e cria aproximações
    matemáticas das features de IA proprietárias do Spotify.
    """
    y, sr = librosa.load(audio_path, sr=22050)
    
    # --- Features Diretas (Sinal) ---
    # Tempo (BPM)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo[0]) if isinstance(tempo, np.ndarray) else float(tempo)
    
    # RMS (Root Mean Square) -> Proxy para Energy e Loudness
    rms = librosa.feature.rms(y=y)[0]
    mean_rms = np.mean(rms)
    
    # Loudness em dB (Adicionado +5.0dB para compensar a normalização do YouTube)
    loudness = float(librosa.amplitude_to_db(np.array([mean_rms]), ref=1.0)[0]) + 5.0
    
    # Energy (0 a 1) -> Melhorado com base na calibração
    energy = min(max(float(mean_rms) * 4.0, 0.0), 1.0)
    
    # Zero Crossing Rate -> Proxy para Speechiness (0 a 1)
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=y))
    speechiness = min(max((float(zcr) - 0.02) * 1.5, 0.0), 1.0)
    
    # Spectral Rolloff & Centroid -> Proxy para Acousticness
    rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    # Músicas acústicas tendem a ter o centro de massa espectral mais baixo
    acousticness = 1.0 - min(max((float(centroid) - 1000.0) / 3000.0, 0.0), 1.0)
    
    # Instrumentalness
    instrumentalness = max(0.0, 1.0 - (speechiness * 4.0))
    
    # Chroma (Notas) -> Proxy para Key e Mode
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    mean_chroma = np.mean(chroma, axis=1)
    key = int(np.argmax(mean_chroma)) # 0 = C, 1 = C#, etc.
    
    # Mode (Maior/Menor)
    mode = 1 if np.mean(mean_chroma) > 0.4 else 0
    
    # Danceability -> Baseado na Força de Ataque (Onset Strength)
    # Segundo fóruns de MIR (Music Info Retrieval), batidas marcadas (dance) geram altos onsets
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    danceability = min(max(float(np.mean(onset_env)) * 0.4, 0.0), 1.0)
    
    # Valence (Humor) -> Ajustado para depender de energia, acordes e brilho espectral
    valence = (energy * 0.3) + (mode * 0.4) + (min(centroid / 4000.0, 1.0) * 0.3)
    valence = min(max(valence, 0.0), 1.0)
    
    # Liveness (Difícil medir sem modelos de reverberação)
    liveness = 0.15 # Média do dataset
    
    # Time Signature
    time_signature = 4.0
    
    # --- DOMAIN SHIFT ADJUSTMENTS (Spotify - Librosa) ---
    return {
        'danceability': max(0.0, min(1.0, danceability + 0.0202)),
        'energy': max(0.0, min(1.0, energy - 0.1353)),
        'key': float(key),
        'loudness': loudness + 1.6032,
        'mode': float(mode),
        'speechiness': max(0.0, min(1.0, speechiness - 0.0210)),
        'acousticness': max(0.0, min(1.0, acousticness - 0.3180)),
        'instrumentalness': max(0.0, min(1.0, instrumentalness - 0.5539)),
        'liveness': max(0.0, min(1.0, liveness + 0.0488)),
        'valence': max(0.0, min(1.0, valence - 0.0221)),
        'tempo': max(0.0, tempo - 2.0613),
        'duration_ms': 60000.0,
        'explicit': 0.0,
        'time_signature': time_signature
    }

def analyze_youtube_song(video_id: str):
    """Baixa o trecho, analisa e limpa o arquivo."""
    audio_path = download_audio_snippet(video_id)
    if not audio_path:
        raise Exception("Falha ao baixar áudio.")
        
    features = extract_features(audio_path)
    
    # Limpa o arquivo
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return features
