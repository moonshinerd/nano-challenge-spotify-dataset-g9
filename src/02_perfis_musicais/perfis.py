"""
Etapa 2 — Construção de perfis musicais (ver atas/ata-01.md, seção 3).

"Perfil musical" aqui não é o perfil de um usuário: é uma caracterização da
própria música a partir dos seus atributos de áudio, como descrito na ata:

    * altamente energética / pouco energética;
    * altamente dançante / pouco dançante;
    * pouco acústica / muito acústica;
    * positiva ou negativa em termos de valence;
    * instrumental ou predominantemente vocal;
    * rápida ou lenta.

Critério de classificação: tercis (baixo/médio/alto) calculados sobre a
própria distribuição do dataset (25%/50%/75% -> aqui usamos 3 grupos de
tamanho igual via pd.qcut), em vez de thresholds fixos. Isso deixa a
classificação relativa ao que o dataset realmente tem, e não a um valor
"chutado" (ex: "energy > 0.75").

Exceção: instrumentalness. Mais de 75% das faixas do dataset têm
instrumentalness muito próximo de 0 (a imensa maioria é vocal), então
dividir em tercis não separa nada de útil — os três grupos ficariam quase
idênticos. Por isso essa variável usa uma regra binária (instrumental via
instrumentalness >= 0.5, que é o próprio critério documentado no
dados_explicados.md) em vez de tercis.
"""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]

# Reutiliza a limpeza/deduplicação já feita na etapa 1.
sys.path.insert(0, str(RAIZ / 'src' / 'shared'))
from dados import carregar_df_unique  # noqa: E402

CAMINHO_DATASET = RAIZ / 'data' / 'raw' / 'dataset.csv'

df = carregar_df_unique(CAMINHO_DATASET)

# --- CLASSIFICAÇÃO POR TERCIS ---
VARIAVEIS_TERCIS = {
    # variavel: (rótulo baixo, rótulo médio, rótulo alto)
    'danceability': ('pouco dançante', 'moderadamente dançante', 'muito dançante'),
    'energy': ('calma', 'energia moderada', 'altamente energética'),
    'acousticness': ('pouco acústica', 'parcialmente acústica', 'altamente acústica'),
    'valence': ('melancólica/negativa', 'valence neutra', 'positiva/eufórica'),
    'tempo': ('lenta', 'tempo moderado', 'rápida'),
}


def classificar_por_tercis(serie, rotulos):
    """Divide a série em 3 grupos de tamanho igual (tercis) usando os rótulos dados."""
    return pd.qcut(serie, q=3, labels=list(rotulos), duplicates='drop')


for variavel, rotulos in VARIAVEIS_TERCIS.items():
    df[f'perfil_{variavel}'] = classificar_por_tercis(df[variavel], rotulos)

# instrumentalness: regra binária (ver docstring do módulo).
LIMIAR_INSTRUMENTAL = 0.5
df['perfil_instrumentalness'] = df['instrumentalness'].apply(
    lambda v: 'instrumental' if v >= LIMIAR_INSTRUMENTAL else 'predominantemente vocal'
)

COLUNAS_PERFIL = [f'perfil_{v}' for v in VARIAVEIS_TERCIS] + ['perfil_instrumentalness']

# Texto descritivo combinando as classificações (ex: "altamente energética, muito
# dançante, pouco acústica, positiva/eufórica, predominantemente vocal, rápida").
df['perfil_musical'] = df[COLUNAS_PERFIL].astype(str).agg(', '.join, axis=1)

# --- SAÍDA ---
COLUNAS_SAIDA = ['track_id', 'track_name', 'artists', 'track_genre'] + COLUNAS_PERFIL + ['perfil_musical']
df_perfis = df[COLUNAS_SAIDA]

CAMINHO_SAIDA = RAIZ / 'data' / 'processed' / 'perfis_musicais.csv'
df_perfis.to_csv(CAMINHO_SAIDA, index=False)

pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

print('=' * 70)
print('PERFIS MUSICAIS')
print('=' * 70)
print(f'Faixas classificadas: {len(df_perfis)}')
print(f'Arquivo gerado: {CAMINHO_SAIDA.name}\n')

print('Pontos de corte dos tercis (limites baixo/médio/alto):')
for variavel in VARIAVEIS_TERCIS:
    _, limites = pd.qcut(df[variavel], q=3, retbins=True, duplicates='drop')
    print(f'  {variavel}: {[round(l, 3) for l in limites]}')
print(f'  instrumentalness: regra binária, limiar = {LIMIAR_INSTRUMENTAL}\n')

print('Distribuição de exemplo (contagem por categoria de energy):')
print(df['perfil_energy'].value_counts())

print('\nExemplos de perfis (5 amostras aleatórias):')
print(df_perfis[['track_name', 'artists', 'perfil_musical']].sample(5, random_state=42))
