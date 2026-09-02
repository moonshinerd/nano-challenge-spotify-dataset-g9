import pandas as pd

FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 
    'speechiness', 'acousticness', 'instrumentalness', 
    'liveness', 'valence', 'tempo'
]

print("Carregando CSV original (Kaggle Base)...")
df_orig = pd.read_csv("../data/raw/dataset.csv")
# Remove duplicatas
df_orig = df_orig.drop_duplicates(subset=['track_name', 'artists'])
print(f"Total base: {len(df_orig)}")

print("Carregando CSV Novo (1 Milhão)...")
df_new = pd.read_csv("../data/raw/dataset_new.csv")
print(f"Total novo: {len(df_new)}")

# Limpeza para Join
df_orig['join_name'] = df_orig['track_name'].astype(str).str.lower().str.strip()
df_orig['join_artist'] = df_orig['artists'].astype(str).str.lower().str.split(';').str[0].str.strip()

df_new['join_name'] = df_new['name'].astype(str).str.lower().str.strip()
df_new['join_artist'] = df_new['artists'].astype(str).str.replace(r"[\['\]]", "", regex=True).str.split(',').str[0].str.strip().str.lower()

print("Cruzando os datasets...")
# Faz inner join
df_merged = pd.merge(df_orig, df_new, on=['join_name', 'join_artist'], suffixes=('_orig', '_new'))
print(f"Encontramos {len(df_merged)} MÚSICAS EM COMUM!")

if len(df_merged) > 0:
    print("\n==============================================")
    print("DIFERENÇA MÉDIA ABSOLUTA (NOVO DATASET - DATASET ORIGINAL)")
    print("Valores muito próximos de zero significam que os datasets são da mesma fonte (API Spotify original)!")
    print("==============================================")
    
    for f in FEATURES:
        diff = df_merged[f + '_new'] - df_merged[f + '_orig']
        mean_diff = diff.abs().mean()
        print(f"'{f}': {mean_diff:.6f}")
