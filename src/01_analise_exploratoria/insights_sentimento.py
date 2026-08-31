## sentimento que a musica evoca (key, mode, valence, energy)
# Existe relação entre energy e loudness?
# Músicas acousticness tendem se relacionam a quais variaveis?
# a relação do sentimento gerado pela muica com a dançabilidade e como isso se relaciona com o restante das variaveis?
# a relação entre liveness com danceability e loudness?

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shared'))
from dados import carregar_dataset, construir_df_unique  # noqa: E402

CAMINHO_DATASET = Path(__file__).resolve().parents[2] / 'data' / 'raw' / 'dataset.csv'

# carrega o dataset (com os mesmos tratamentos de popularidade)
df = carregar_dataset(CAMINHO_DATASET)
df_unique = construir_df_unique(df)


# --- ANÁLISES DE CORRELAÇÃO DE SENTIMENTOS ---
colunas_sentimento = [
    'danceability', 'energy', 'valence', 'acousticness', 
    'loudness', 'liveness', 'tempo', 'speechiness'
]

matriz_corr = df_unique[colunas_sentimento].corr()

def interpretar_correlacao(valor):
    if pd.isna(valor): return "N/A"
    direcao = "positiva" if valor >= 0 else "negativa"
    valor_abs = abs(valor)
    if valor_abs < 0.1: forca = "quase nula"
    elif valor_abs < 0.3: forca = "fraca"
    elif valor_abs < 0.6: forca = "moderada"
    elif valor_abs < 0.8: forca = "forte"
    else: forca = "muito forte"
    return f"relação {forca} {direcao}"

def formatar_relacoes(variavel):
    correlacoes = matriz_corr[variavel].drop(variavel).sort_values(ascending=False)
    resultado = pd.DataFrame({
        'correlacao': correlacoes.round(3),
        'inferencia': correlacoes.apply(interpretar_correlacao)
    })
    return resultado

# 1. Existe relação entre energy e loudness?
corr_energy_loudness = matriz_corr.loc['energy', 'loudness']
inferencia_energy_loudness = interpretar_correlacao(corr_energy_loudness)

# 2. Músicas acousticness tendem se relacionam a quais variaveis?
relacoes_acousticness = formatar_relacoes('acousticness')

# 3. A relação do sentimento gerado pela muica (valence) com a dançabilidade e com o restante?
corr_valence_danceability = matriz_corr.loc['valence', 'danceability']
inferencia_valence_danceability = interpretar_correlacao(corr_valence_danceability)
relacoes_valence = formatar_relacoes('valence')

# 4. A relação entre liveness com danceability e loudness?
corr_liveness_danceability = matriz_corr.loc['liveness', 'danceability']
corr_liveness_loudness = matriz_corr.loc['liveness', 'loudness']


# --- PRINTS DE INSIGHTS ---
print("="*60)
print("INSIGHTS DE SENTIMENTO E ACÚSTICA")
print("="*60)

print("\n1. Existe relação entre energy e loudness?")
print(f"Sim! Correlação de {corr_energy_loudness:.3f} ({inferencia_energy_loudness}).")
print("Músicas com mais energia são quase sempre mais altas (loudness).")

print("\n2. Músicas acústicas (acousticness) tendem a se relacionar a quais variáveis?")
print(relacoes_acousticness)
print("\nInsight: Músicas acústicas são fortemente ligadas a baixa energia e baixo volume.")

print("\n3. Qual a relação do sentimento gerado (valence/positividade) com a dançabilidade e outras variáveis?")
print(f"Com Danceability: Correlação de {corr_valence_danceability:.3f} ({inferencia_valence_danceability}).")
print("O sentimento (valence) se relaciona com as outras variáveis da seguinte forma:")
print(relacoes_valence)
print("\nInsight: Músicas mais felizes (alta valence) tendem a ser mais dançantes e ter um pouco mais de energia e volume.")

print("\n4. Qual a relação de músicas ao vivo (liveness) com danceability e loudness?")
print(f"Liveness vs Danceability: {corr_liveness_danceability:.3f} ({interpretar_correlacao(corr_liveness_danceability)})")
print(f"Liveness vs Loudness:     {corr_liveness_loudness:.3f} ({interpretar_correlacao(corr_liveness_loudness)})")
print("\nInsight: Músicas ao vivo não são necessariamente mais dançantes, e o volume tem pouquíssima relação.")
print("="*60)
