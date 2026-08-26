import pandas as pd

# carrega o dataset
df = pd.read_csv('dataset(in).csv')

generos = df['track_genre'].nunique()

popularidade_por_genero = (df.groupby('track_genre')['popularity'].mean()).sort_values(ascending=False)

colunas_numericas = [
    'popularity',
    'danceability',
    'energy',
    'valence',
    'acousticness',
    'instrumentalness',
    'tempo',
    'loudness',
    'speechiness',
    'liveness',
    'duration_ms',
    'explicit',
    'key',
    'mode',
    'time_signature',
]

pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

correlacoes_popularidade = df[colunas_numericas].corr()['popularity'].drop('popularity')
ordem_por_forca = correlacoes_popularidade.abs().sort_values(ascending=False).index
correlacoes = correlacoes_popularidade.reindex(ordem_por_forca)


def interpretar_correlacao(valor):
    direcao = "positiva" if valor >= 0 else "negativa"
    valor_abs = abs(valor)

    if valor_abs < 0.1:
        forca = "quase nula"
    elif valor_abs < 0.3:
        forca = "fraca"
    elif valor_abs < 0.5:
        forca = "moderada"
    else:
        forca = "forte"

    return f"relação {forca} {direcao} com a popularidade"


inferencias = correlacoes.apply(interpretar_correlacao)

tabela_correlacao = pd.DataFrame({
    'correlacao': correlacoes.round(3),
    'inferencia': inferencias,
})
tabela_correlacao.index.name = 'variavel'

qtd_por_genero = df['track_genre'].value_counts()

top5_generos = popularidade_por_genero.head(5).index

perfil_top5_generos = df[df['track_genre'].isin(top5_generos)].groupby('track_genre')[
    ['danceability', 'energy', 'valence', 'acousticness']
].mean()

# PRINTS DE INSIGHTS
print(f'Quantidade de gêneros distintos: {generos}\n')

print(f'Popularidade média por gênero (top 10):\n{popularidade_por_genero.head(10)}\n')

print(f'Correlações entre variáveis numéricas e popularidade:\n{tabela_correlacao}\n')

print(f'Quantidade de faixas por gênero (top 10):\n{qtd_por_genero.head(10)}\n')

print(f'Top 5 gêneros mais populares: {list(top5_generos)}\n')

print(f'Perfil médio (danceability, energy, valence, acousticness) dos top 5 gêneros:\n{perfil_top5_generos}\n')
