import pandas as pd
import random
from audio_analyzer import analyze_youtube_song
import main
from ytmusicapi import YTMusic

FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 
    'speechiness', 'acousticness', 'instrumentalness', 
    'liveness', 'valence', 'tempo'
]

def carregar_novo_dataset(caminho):
    print("Carregando novo dataset...")
    df = pd.read_csv(caminho, nrows=50000)
    df = df.rename(columns={"name": "track_name", "id": "track_id"})
    return df

def run():
    # Inicializa o yt_client do main
    main.yt_client = YTMusic()
    
    df = carregar_novo_dataset("../data/raw/dataset_new.csv")
    amostra = df.sample(15)
    
    results = []
    
    print("\nIniciando calibração com 15 músicas aleatórias do NOVO dataset...")
    for idx, row in amostra.iterrows():
        t_name = row['track_name']
        t_artists = row['artists']
        print(f"\n--- Analisando: {t_name} - {t_artists} ---")
        
        yt_data = main.get_yt_info(t_name, t_artists)
        if not yt_data:
            print("Não encontrado no YT.")
            continue
            
        vid = yt_data.get('videoId')
        if not vid:
            continue
            
        try:
            calc_features = analyze_youtube_song(vid)
            if not calc_features:
                continue
            
            diff_row = {}
            for f in FEATURES:
                real_val = float(row[f])
                calc_val = calc_features[f]
                diff_row[f] = real_val - calc_val
                
            results.append(diff_row)
        except Exception as e:
            print(f"Erro: {e}")

    print("\n===============================")
    print("DESVIO DO NOVO DATASET (Dataset Novo - Nosso Padrão Atual):")
    df_res = pd.DataFrame(results)
    means = df_res.mean()
    for f in FEATURES:
        print(f"'{f}': {means[f]:.4f},")
    print("===============================\n")

if __name__ == "__main__":
    run()
