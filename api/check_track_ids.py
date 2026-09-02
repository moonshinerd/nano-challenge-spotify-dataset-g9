import pandas as pd

df_orig = pd.read_csv("../data/raw/dataset.csv")
df_orig = df_orig.drop_duplicates(subset=['track_name', 'artists'])

df_new = pd.read_csv("../data/raw/dataset_1M_clean.csv.gz", compression='gzip')

df_orig['join_name'] = df_orig['track_name'].astype(str).str.lower().str.strip()
df_orig['join_artist'] = df_orig['artists'].astype(str).str.lower().str.split(';').str[0].str.strip()

df_new['join_name'] = df_new['name'].astype(str).str.lower().str.strip()
df_new['join_artist'] = df_new['artists'].astype(str).str.lower().str.split(';').str[0].str.strip()

df_merged = pd.merge(df_orig, df_new, on=['join_name', 'join_artist'], suffixes=('_orig', '_new'))

same_id = (df_merged['track_id'] == df_merged['id']).sum()
total = len(df_merged)

print(f"Total de músicas em comum (por Nome+Artista): {total}")
print(f"Dessas, músicas que possuem EXATAMENTE o MESMO track_id: {same_id}")
print(f"Músicas em comum com track_ids DIFERENTES: {total - same_id}")

