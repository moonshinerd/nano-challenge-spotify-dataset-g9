"""
Etapa 3 — Playlists por características (ver docs/perfil_musical.md e
docs/atas/ata-01.md, seção 5 "Criação de playlists por características").

Monta 4 playlists de 10 músicas a partir dos perfis definidos manualmente
pela equipe em docs/perfil_musical.md:

    RELAX   -> tempo baixo, energy baixo, loudness baixo, valence baixo,
               speechiness baixo, instrumentalness alto
    TREINO  -> energy alto, danceability alto, valence alto, speechiness alto
    ROMANCE -> igual ao RELAX (tempo/energy/valence baixos), mas com
               loudness alto, speechiness alto e instrumentalness baixo
    POPULAR -> apenas as músicas mais populares, sem filtro de perfil

"Alto"/"baixo" são definidos por tercis (33%/67%) calculados sobre a própria
distribuição do dataset, seguindo o mesmo critério usado na etapa 2
(src/02_perfis_musicais/perfis.py), em vez de valores fixos chutados.

Para cada playlist, além das 10 músicas, o script reporta:
    - quais thresholds (tercis) foram usados;
    - a predominância de gêneros entre as músicas que se encaixam no perfil;
    - a lista de gêneros que mais se adequam à playlist.
"""
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'src' / 'shared'))
from dados import carregar_dataset, construir_df_unique  # noqa: E402

CAMINHO_DATASET = RAIZ / 'data' / 'raw' / 'dataset.csv'
PASTA_SAIDA = RAIZ / 'data' / 'processed' / 'playlists'
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

# --- CARGA DOS DADOS ---
df = carregar_dataset(CAMINHO_DATASET)

# df_unique: uma linha por música (evita repetir a mesma faixa na playlist).
df_unique = construir_df_unique(df)

# df_generos: mantém a granularidade de gênero (uma linha por combinação
# música+gênero), para medir a predominância de gêneros dentro de cada
# perfil de forma correta (a mesma lógica de src/01_analise_exploratoria/insights_genero.py).
df_generos = df.dropna(subset=['track_genre']).drop_duplicates(
    subset=['track_name', 'artists', 'track_genre']
)

# --- TERCIS (33%/67%) DAS VARIÁVEIS USADAS NOS PERFIS ---
VARIAVEIS = ['tempo', 'energy', 'loudness', 'valence', 'speechiness', 'danceability', 'instrumentalness']
LIMIARES = {var: (df_unique[var].quantile(1 / 3), df_unique[var].quantile(2 / 3)) for var in VARIAVEIS}


def aplicar_condicao(dataframe, variavel, nivel):
    """nivel: 'baixo' (<= tercil 33%) ou 'alto' (>= tercil 67%)."""
    p33, p67 = LIMIARES[variavel]
    if nivel == 'baixo':
        return dataframe[variavel] <= p33
    if nivel == 'alto':
        return dataframe[variavel] >= p67
    raise ValueError(f'nível inválido: {nivel}')


def filtrar_por_perfil(dataframe, condicoes):
    mascara = pd.Series(True, index=dataframe.index)
    for variavel, nivel in condicoes.items():
        mascara &= aplicar_condicao(dataframe, variavel, nivel)
    return dataframe[mascara]


PERFIS = {
    'RELAX': {
        'tempo': 'baixo', 'energy': 'baixo', 'loudness': 'baixo',
        'valence': 'baixo', 'speechiness': 'baixo', 'instrumentalness': 'alto',
    },
    'TREINO': {
        'energy': 'alto', 'danceability': 'alto', 'valence': 'alto', 'speechiness': 'alto',
    },
    'ROMANCE': {
        'tempo': 'baixo', 'energy': 'baixo', 'valence': 'baixo',
        'speechiness': 'alto', 'instrumentalness': 'baixo',
        # loudness alto foi removido da regra original em docs/perfil_musical.md:
        # loudness tem correlação de 0.76 com energy (ver docs/anotacoes.md e
        # insights_sentimento.py), então "energy baixo + loudness alto" é uma
        # combinação quase inexistente no dataset (apenas 5 faixas). Sem essa
        # condição, sobram 171 candidatas, suficiente para montar a playlist.
    },
}

COLUNAS_PLAYLIST = ['track_name', 'artists', 'popularity', 'track_genre']


def montar_playlist(nome, candidatos_unique, candidatos_generos):
    """Monta a playlist (top 10 por popularity) e o relatório de gêneros predominantes."""
    playlist = candidatos_unique.nlargest(10, 'popularity')[COLUNAS_PLAYLIST]

    generos_predominantes = (
        candidatos_generos['track_genre'].value_counts(normalize=True).head(8) * 100
    ).round(1)

    playlist.to_csv(PASTA_SAIDA / f'playlist_{nome.lower()}.csv', index=False)

    return playlist, generos_predominantes


# --- RELAX / TREINO / ROMANCE (com filtro de perfil) ---
resultados = {}
for nome, condicoes in PERFIS.items():
    candidatos_unique = filtrar_por_perfil(df_unique, condicoes)
    candidatos_generos = filtrar_por_perfil(df_generos, condicoes)
    resultados[nome] = {
        'condicoes': condicoes,
        'qtd_candidatos': len(candidatos_unique),
        **dict(zip(['playlist', 'generos'], montar_playlist(nome, candidatos_unique, candidatos_generos))),
    }

# --- POPULAR (sem filtro de perfil, só popularity) ---
# Para a predominância de gêneros, usa uma amostra maior (top 100 mais populares)
# que a própria playlist (10), pra ter uma leitura de gênero mais estável.
amostra_popular_generos = df_generos.nlargest(100, 'popularity')
playlist_popular = df_unique.nlargest(10, 'popularity')[COLUNAS_PLAYLIST]
playlist_popular.to_csv(PASTA_SAIDA / 'playlist_popular.csv', index=False)
generos_popular = (
    amostra_popular_generos['track_genre'].value_counts(normalize=True).head(8) * 100
).round(1)
resultados['POPULAR'] = {
    'condicoes': {'popularity': 'top 10 (sem filtro de perfil)'},
    'qtd_candidatos': len(df_unique),
    'playlist': playlist_popular,
    'generos': generos_popular,
}

# --- RELATÓRIO ---
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None)

print('=' * 80)
print('PLAYLISTS POR PERFIL MUSICAL')
print('=' * 80)

print('\nTercis (33%/67%) usados para classificar "baixo"/"alto":')
for var, (p33, p67) in LIMIARES.items():
    print(f'  {var}: baixo <= {p33:.3f}  |  alto >= {p67:.3f}')

for nome, dados in resultados.items():
    print('\n' + '-' * 80)
    print(f'Playlist {nome}')
    print('-' * 80)
    print(f'Critérios: {dados["condicoes"]}')
    print(f'Músicas candidatas ao perfil: {dados["qtd_candidatos"]}\n')

    print('Predominância de gêneros no perfil (top 8, % das faixas candidatas):')
    print(dados['generos'])
    print(f'\nGêneros que mais se adequam à playlist {nome}: {list(dados["generos"].index)}\n')

    print(f'As 10 músicas da playlist {nome} (ordenadas por popularity):')
    print(dados['playlist'].to_string(index=False))

print(f'\nCSVs gerados em: {PASTA_SAIDA.relative_to(RAIZ)}/')
