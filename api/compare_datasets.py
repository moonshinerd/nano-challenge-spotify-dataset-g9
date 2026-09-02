import pandas as pd
import psycopg2

FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 
    'speechiness', 'acousticness', 'instrumentalness', 
    'liveness', 'valence', 'tempo'
]

print("Conectando ao banco...")
conn = psycopg2.connect(host="db", dbname="spotify", user="user", password="password")
cur = conn.cursor()

# Buscar músicas do dataset original
cur.execute(f"SELECT track_name, artists, {', '.join(FEATURES)} FROM tracks LIMIT 50000;")
rows = cur.fetchall()

# Criar dicionário de (track_name_lower, artist_lower) -> features
original_data = {}
for row in rows:
    t_name = row[0].lower().strip()
    t_artists = row[1].lower().strip()
    
    # row[2:] são as features
    features = {FEATURES[i]: float(row[2+i]) for i in range(len(FEATURES))}
    
    # Se houver múltiplos artistas separados por ; no original, pegamos o primeiro
    primary_artist = t_artists.split(';')[0].strip()
    key = (t_name, primary_artist)
    original_data[key] = features

print(f"Carregadas {len(rows)} músicas do banco original.")

print("Carregando novo dataset CSV...")
df_new = pd.read_csv("../data/raw/dataset_new.csv")
print(f"Total no novo dataset: {len(df_new)}")

diffs = {f: [] for f in FEATURES}
matches = 0

for idx, row in df_new.iterrows():
    t_name = str(row.get('name', '')).lower().strip()
    t_artists = str(row.get('artists', '')).lower().strip()
    
    # No novo dataset pode vir como "['Artist Name']" ou "Artist Name, Another"
    # Vamos fazer um replace bruto pra pegar o primeiro nome
    primary_artist = t_artists.replace("['", "").replace("']", "").replace("'", "").split(',')[0].strip()
    
    key = (t_name, primary_artist)
    if key in original_data:
        matches += 1
        orig_f = original_data[key]
        for f in FEATURES:
            new_val = float(row[f])
            orig_val = orig_f[f]
            # Desvio = NOVO - ORIGINAL
            diffs[f].append(new_val - orig_val)

print(f"\nEncontramos {matches} MÚSICAS EM COMUM!")

if matches > 0:
    print("\n==============================================")
    print("DIFERENÇA MÉDIA (NOVO DATASET - DATASET ORIGINAL)")
    print("Valores muito próximos de zero significam que os datasets estão perfeitamente alinhados!")
    print("==============================================")
    for f in FEATURES:
        mean_diff = sum(diffs[f]) / matches
        print(f"'{f}': {mean_diff:.6f}")
else:
    print("Nenhuma música em comum encontrada. Tente melhorar o cruzamento de nomes.")
