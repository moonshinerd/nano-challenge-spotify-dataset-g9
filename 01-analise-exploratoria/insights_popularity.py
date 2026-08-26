# Quais gêneros têm maior popularity média? respondida
# Músicas populares tendem a ser mais danceability? respondida
# Música só são mais populares por causa da popularidade do artista? 
# As músicas mais populares são relacionadas a algum artista em específico?
# Músicas explícitas são, em média, mais populares?
# Músicas instrumentais são menos populares?
# Músicas com BPM mais alto são mais populares?
import pandas as pd

# carrega o dataset
df = pd.read_csv('dataset(in).csv')

# Criação de um dataframe sem faixas duplicadas (para análises que não envolvem track_genre)
# Isso evita que faixas com múltiplos gêneros entrem várias vezes na mesma conta
df_unique = df.drop_duplicates(subset=['track_id'])

# --- ANÁLISES DE GÊNERO (Usa df com as duplicatas de gênero mantidas) ---
generos = df['track_genre'].nunique()
popularidade_por_genero = (df.groupby('track_genre')['popularity'].mean()).sort_values(ascending=False)
qtd_por_genero = df['track_genre'].value_counts()
top5_generos = popularidade_por_genero.head(5).index
perfil_top5_generos = df[df['track_genre'].isin(top5_generos)].groupby('track_genre')[
    ['danceability', 'energy', 'valence', 'acousticness']
].mean()


# --- ANÁLISES GERAIS (Usa df_unique para não enviesar resultados) ---
colunas_numericas = [
    'popularity', 'danceability', 'energy', 'valence', 'acousticness',
    'instrumentalness', 'tempo', 'loudness', 'speechiness', 'liveness',
    'duration_ms', 'explicit', 'key', 'mode', 'time_signature'
]

pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

correlacoes_popularidade = df_unique[colunas_numericas].corr()['popularity'].drop('popularity')
ordem_por_forca = correlacoes_popularidade.abs().sort_values(ascending=False).index
correlacoes = correlacoes_popularidade.reindex(ordem_por_forca)

def interpretar_correlacao(valor):
    direcao = "positiva" if valor >= 0 else "negativa"
    valor_abs = abs(valor)
    if valor_abs < 0.1: forca = "quase nula"
    elif valor_abs < 0.3: forca = "fraca"
    elif valor_abs < 0.5: forca = "moderada"
    else: forca = "forte"
    return f"relação {forca} {direcao} com a popularidade"

inferencias = correlacoes.apply(interpretar_correlacao)
tabela_correlacao = pd.DataFrame({
    'correlacao': correlacoes.round(3),
    'inferencia': inferencias,
})
tabela_correlacao.index.name = 'variavel'

# 1. Quais gêneros têm maior popularity média? 
top_generos_popularity = popularidade_por_genero.head(10)

# 2. Músicas populares tendem a ser mais danceability?
tendencia_danceability = tabela_correlacao.loc['danceability']

# 3. Música só são mais populares por causa da popularidade do artista?
popularidade_media_por_artista = df_unique.groupby('artists')['popularity'].mean().sort_values(ascending=False)
top_10_artistas_populares = popularidade_media_por_artista.head(10)

# 4. As músicas mais populares são relacionadas a algum artista em específico?
musicas_mais_populares = df_unique.nlargest(10, 'popularity')[['track_name', 'artists', 'popularity']]

# 5. Músicas explícitas são, em média, mais populares?
popularidade_explicitas = df_unique.groupby('explicit')['popularity'].mean()

# 6. Músicas instrumentais são menos populares?
tendencia_instrumentalness = tabela_correlacao.loc['instrumentalness']

# 7. Músicas com BPM mais alto são mais populares?
tendencia_bpm = tabela_correlacao.loc['tempo']

# --- INSIGHTS ADICIONAIS ---
# Insight Adicional 1: Quais artistas possuem mais músicas e qual a sua popularidade?
artistas_produtividade = df_unique['artists'].value_counts().head(10)

# Insight Adicional 2: Qual a correlação mais forte com a popularidade, seja ela positiva ou negativa?
variavel_mais_correlacionada = tabela_correlacao.iloc[0]

# Insight Adicional 3: Duração média das 100 músicas mais populares vs O Restante
top_100_musicas = df_unique.nlargest(100, 'popularity')
resto_musicas = df_unique.drop(top_100_musicas.index)
duracao_media_top_100_min = top_100_musicas['duration_ms'].mean() / 60000
duracao_media_resto_min = resto_musicas['duration_ms'].mean() / 60000


# PRINTS DE INSIGHTS
print(f'Quantidade de gêneros distintos: {generos}\n')

print(f'1. Quais gêneros têm maior popularity média? (Top 10):\n{top_generos_popularity}\n')

print(f'2. Músicas populares tendem a ser mais danceability?\nDanceability tem correlação de {tendencia_danceability["correlacao"]} ({tendencia_danceability["inferencia"]})\n')

print(f'3. Artistas com maior média de popularidade nas suas músicas (Top 10):\n{top_10_artistas_populares}\n')

print(f'4. As músicas mais populares (Top 10 únicas) e seus artistas:\n{musicas_mais_populares}\n')

print(f'5. Popularidade média por ser explícita ou não:\n{popularidade_explicitas}\n')

print(f'6. Músicas instrumentais são menos populares?\nInstrumentalness tem correlação de {tendencia_instrumentalness["correlacao"]} ({tendencia_instrumentalness["inferencia"]})\n')

print(f'7. Músicas com BPM mais alto são mais populares?\nTempo (BPM) tem correlação de {tendencia_bpm["correlacao"]} ({tendencia_bpm["inferencia"]})\n')

print('--- INSIGHTS ADICIONAIS ---\n')
print(f'Variável com influência mais forte na popularidade:\n{variavel_mais_correlacionada.name} ({variavel_mais_correlacionada["correlacao"]} - {variavel_mais_correlacionada["inferencia"]})\n')

print(f'Top 10 artistas com mais músicas lançadas:\n{artistas_produtividade}\n')

print(f'Duração média das 100 músicas mais populares: {duracao_media_top_100_min:.2f} minutos')
print(f'Duração média do restante das músicas: {duracao_media_resto_min:.2f} minutos\n')

print(f'Quantidade de faixas por gênero (top 10):\n{qtd_por_genero.head(10)}\n')

print(f'Top 5 gêneros mais populares: {list(top5_generos)}\n')

print(f'Perfil médio (danceability, energy, valence, acousticness) dos top 5 gêneros:\n{perfil_top5_generos}\n')
