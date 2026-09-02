import pandas as pd
from ftfy import fix_text

def fix_mojibake(text):
    if not isinstance(text, str):
        return text
    try:
        fixed = text.encode('windows-1252').decode('utf-8')
        if fixed != text:
            return fixed
    except Exception:
        pass
    
    return fix_text(text)

def clean_artists(text):
    if not isinstance(text, str):
        return "Unknown"
    if text.startswith("['") and text.endswith("']"):
        import ast
        try:
            arr = ast.literal_eval(text)
            return "; ".join(arr)
        except:
            pass
    return text.replace("['", "").replace("']", "").replace("', '", "; ").replace('"', '').replace("'", "")

print("Carregando CSV massivo (dataset_new.csv)...")
df = pd.read_csv("/data/raw/dataset_new.csv")
print(f"Total inicial: {len(df)} linhas")

print("Removendo duplicatas de nome e artista...")
df['name_lower'] = df['name'].astype(str).str.lower().str.strip()
df['artist_lower'] = df['artists'].astype(str).str.lower().str.strip()
df = df.drop_duplicates(subset=['name_lower', 'artist_lower'], keep='first')
df = df.drop(columns=['name_lower', 'artist_lower'])
print(f"Total após remover duplicatas: {len(df)} linhas")

print("Limpando Mojibake (Caracteres quebrados) e formatando artistas...")
df['name'] = df['name'].apply(fix_mojibake)
df['artists'] = df['artists'].apply(clean_artists)
df['artists'] = df['artists'].apply(fix_mojibake)

print("Salvando CSV comprimido (GZIP) para não pesar no GitHub...")
df.to_csv("/data/raw/dataset_1M_clean.csv.gz", index=False, compression='gzip')

print("Feito! Limpando os lixos temporários...")
import os
if os.path.exists("/data/raw/dataset_new.csv"):
    os.remove("/data/raw/dataset_new.csv")

print("Sucesso! CSV limpo, formatado, e super comprimido salvo em /data/raw/dataset_1M_clean.csv.gz")
