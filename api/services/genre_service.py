"""Identificação de gênero: iTunes (oficial) com fallback por IA a partir
das features de áudio, e busca de capa em alta resolução na Apple."""
import requests

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
    "death metal/black metal": "black-metal",
}


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
                return img.replace("100x100bb.jpg", "600x600bb.jpg")  # Pega versão HQ
    except Exception:
        pass
    return None


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
    if 60 < tempo < 90 and danceability > 0.6 and energy < 0.6:
        genres.extend(["Reggae", "Dub", "Chillout"])

    # Ao Vivo
    if liveness > 0.7:
        genres.append("Ao Vivo / Live")

    if not genres:
        genres.extend(["Alternativa", "Indie", "Experimental"])

    return genres


def get_genres_combined(track_name: str, artists: str, raw_features: dict = None) -> str:
    """
    Tenta buscar no iTunes. Se achar, usa o gênero oficial.
    Somente se falhar totalmente, usamos a IA matemática.
    """
    final_genres = []

    # 1. iTunes (Gênero Oficial)
    try:
        clean_str = f"{track_name} {artists}".replace(";", " ").replace(",", " ").replace("&", " ").replace("(", " ").replace(")", " ")
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
        for g in ai_genres[:2]:
            g_lower = g.lower()
            g_mapped = ITUNES_TO_KAGGLE_GENRES.get(g_lower, g_lower)
            final_genres.append(g_mapped)

    if not final_genres:
        final_genres.append("descoberta da web")

    return ", ".join(final_genres)


def genre_needs_refresh(genre: str) -> bool:
    """True se o gênero salvo está vazio ou é só um placeholder de fallback."""
    if not genre or not genre.strip():
        return True
    return genre.lower() in ("descoberta da web", "desconhecido", "desconhecida")
