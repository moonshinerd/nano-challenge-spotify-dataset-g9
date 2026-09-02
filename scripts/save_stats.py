import sys
import json
from pathlib import Path
sys.path.insert(0, '/src/shared')
from dados import carregar_dataset, construir_df_unique

FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
    'duration_ms', 'explicit', 'time_signature',
]

print("Calculando médias e desvios para o normalizador em tempo real...")
df = carregar_dataset(Path("/data/raw/dataset.csv"))
df_unique = construir_df_unique(df)
df_unique['explicit'] = df_unique['explicit'].astype(int)

medias = df_unique[FEATURES].mean().to_dict()
desvios = df_unique[FEATURES].std().to_dict()

with open("/app/stats.json", "w") as f:
    json.dump({"medias": medias, "desvios": desvios}, f)
print("Salvo em stats.json")
