import sys
import os
import random
import pandas as pd
from pathlib import Path
from ytmusicapi import YTMusic

# Ferramenta de manutenção (roda fora do container/app principal), por isso
# aponta manualmente para api/ e src/shared/ em vez de depender do cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "api"))
sys.path.insert(0, '/src/shared')
from audio_analyzer import extract_features, download_audio_snippet
from dados import carregar_dataset, construir_df_unique

FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
]

def main():
    print("Iniciando calibração com 15 músicas aleatórias...")
    df = carregar_dataset(Path("/data/raw/dataset.csv"))
    df_unique = construir_df_unique(df)
    
    # Amostra de 15 músicas DIFERENTES (mudamos o random_state)
    sample = df_unique.sample(n=15, random_state=100)
    
    yt = YTMusic()
    
    results = []
    
    for _, row in sample.iterrows():
        track_name = row['track_name']
        artists = row['artists']
        print(f"\n--- Analisando: {track_name} - {artists} ---")
        
        # Busca YT
        search_res = yt.search(f"{track_name} {artists}", filter="songs", limit=1)
        if not search_res:
            print("Não achou no YT.")
            continue
            
        vid = search_res[0]['videoId']
        print(f"Baixando {vid}...")
        try:
            audio_path = download_audio_snippet(vid)
            if not audio_path:
                continue
                
            calc_features = extract_features(audio_path)
            
            diff_row = {}
            # Compara
            for f in FEATURES:
                real_val = row[f]
                calc_val = calc_features[f]
                diff_row[f] = real_val - calc_val
                
            results.append(diff_row)
            os.remove(audio_path)
        except Exception as e:
            print(f"Erro: {e}")

    print("\n===============================")
    print("DOMAIN SHIFT CALCULADO (Spotify - Librosa):")
    print("Subtraia isso do Librosa para alinhar ao Spotify!")
    df_res = pd.DataFrame(results)
    means = df_res.mean()
    for f in FEATURES:
        print(f"'{f}': {means[f]:.4f},")
    print("===============================\n")

if __name__ == "__main__":
    main()
