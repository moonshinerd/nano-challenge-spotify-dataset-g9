"""
Etapa 4 — Sugestão e recomendação de músicas
(ver docs/atas/ata-01.md, seções 4 "Sugestão e recomendação de músicas"
e 6 "Similaridade entre músicas").

Duas formas de uso, configuradas nas variáveis TRACK_ID_EXEMPLO e
GRUPO_TRACK_IDS lá embaixo:

  1. Uma música (TRACK_ID_EXEMPLO) -> retorna as 5 músicas mais parecidas
     com ELA.
  2. Um grupo de músicas (GRUPO_TRACK_IDS) -> calcula o perfil médio do
     grupo e retorna as 5 músicas mais parecidas com esse perfil combinado
     (ex: "a partir dessas 3 músicas que você curte, sugere mais 5").

Método: similaridade de cosseno sobre as variáveis de áudio normalizadas
(z-score), usando todas as características de áudio disponíveis, exceto
popularity (não é uma característica sonora, é uma métrica de sucesso —
incluí-la faria a recomendação puxar por popularidade em vez de por som):

    danceability, energy, key, loudness, mode, speechiness, acousticness,
    instrumentalness, liveness, valence, tempo, duration_ms, explicit,
    time_signature

Normalizamos porque essas variáveis estão em escalas muito diferentes
(tempo em BPM ~50–220, duration_ms na casa das centenas de milhares,
loudness em dB negativo, o resto entre 0 e 1) — sem normalizar, as de
maior escala dominariam sozinhas o cálculo de distância.

Nota sobre key: é uma variável categórica (a nota musical, 0=C, 1=C#, ...,
11=B) e cíclica (a nota 11 está musicalmente "perto" da nota 0, mas
numericamente longe). Tratá-la como número contínuo no z-score é uma
simplificação — ela pesa no cálculo, mas sem captar essa proximidade
circular entre notas extremas.

Usa data/processed em vez do dataset bruto direto: uma linha por música
(construir_df_unique), pra não recomendar duas vezes a "mesma" faixa por
ela aparecer em vários gêneros ou álbuns diferentes.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'src' / 'shared'))
from dados import carregar_dataset, construir_df_unique  # noqa: E402

CAMINHO_DATASET = RAIZ / 'data' / 'raw' / 'dataset.csv'
PASTA_SAIDA = RAIZ / 'data' / 'processed' / 'recomendacoes'
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

FEATURES = [
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
    'duration_ms', 'explicit', 'time_signature',
]
COLUNAS_RESULTADO = ['track_id', 'track_name', 'artists', 'track_genre', 'popularity']

df = carregar_dataset(CAMINHO_DATASET)
df_unique = construir_df_unique(df)
df_unique['explicit'] = df_unique['explicit'].astype(int)

# --- NORMALIZAÇÃO (z-score) E MATRIZ DE CARACTERÍSTICAS ---
MEDIAS = df_unique[FEATURES].mean()
DESVIOS = df_unique[FEATURES].std()
MATRIZ_NORMALIZADA = ((df_unique[FEATURES] - MEDIAS) / DESVIOS).to_numpy()
NORMAS_CANDIDATOS = np.linalg.norm(MATRIZ_NORMALIZADA, axis=1)


def localizar_por_track_id(track_id):
    """
    Acha a linha em df_unique correspondente a um track_id. Como df_unique
    concatena os ids de uma mesma música (mesmo nome+artista) que aparece
    repetida por gênero ou álbum, o id buscado pode estar dentro de uma
    lista "id1, id2, id3" em vez de sozinho.
    """
    encontrada = df_unique[df_unique['track_id'].apply(lambda ids: track_id in ids.split(', '))]
    if encontrada.empty:
        raise ValueError(f'track_id não encontrado no dataset: {track_id}')
    return encontrada.iloc[0]


def vetor_normalizado(linha):
    return ((linha[FEATURES] - MEDIAS) / DESVIOS).to_numpy(dtype=float)


def recomendar_por_vetor(vetor_perfil, indices_excluidos, top_n=5):
    """Similaridade de cosseno entre vetor_perfil e todas as candidatas, excluindo indices_excluidos."""
    norma_perfil = np.linalg.norm(vetor_perfil)
    similaridades = (MATRIZ_NORMALIZADA @ vetor_perfil) / (NORMAS_CANDIDATOS * norma_perfil + 1e-9)
    serie = pd.Series(similaridades, index=df_unique.index).drop(index=indices_excluidos, errors='ignore')
    top = serie.sort_values(ascending=False).head(top_n)
    resultado = df_unique.loc[top.index, COLUNAS_RESULTADO].copy()
    resultado['similaridade'] = top.round(4).values
    return resultado


def recomendar_por_musica(track_id, top_n=5):
    linha = localizar_por_track_id(track_id)
    vetor = vetor_normalizado(linha)
    recomendacoes = recomendar_por_vetor(vetor, indices_excluidos=[linha.name], top_n=top_n)
    return linha, recomendacoes


def recomendar_por_grupo(lista_track_ids, top_n=5):
    linhas = [localizar_por_track_id(tid) for tid in lista_track_ids]
    indices = [linha.name for linha in linhas]
    perfil_medio = np.mean([vetor_normalizado(linha) for linha in linhas], axis=0)
    recomendacoes = recomendar_por_vetor(perfil_medio, indices_excluidos=indices, top_n=top_n)
    return linhas, recomendacoes


# --- CONFIGURAÇÃO: troque pelos track_ids que quiser testar ---
TRACK_ID_EXEMPLO = '3nqQXoyQOWXiESFLlDF1hG'  # Unholy - Sam Smith;Kim Petras (ver docs/dados_explicados.md)

GRUPO_TRACK_IDS = [
    '3nqQXoyQOWXiESFLlDF1hG',  # Unholy - Sam Smith;Kim Petras
]


if __name__ == '__main__':
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)

    print('=' * 80)
    print('RECOMENDAÇÃO POR UMA MÚSICA')
    print('=' * 80)
    musica, recomendacoes_musica = recomendar_por_musica(TRACK_ID_EXEMPLO)
    print(f'Música de referência: {musica["track_name"]} — {musica["artists"]} ({musica["track_genre"]})')
    print(f'Perfil: {musica[FEATURES].to_dict()}\n')
    print('5 músicas mais parecidas:')
    print(recomendacoes_musica.to_string(index=False))
    recomendacoes_musica.to_csv(PASTA_SAIDA / f'recomendacao_{TRACK_ID_EXEMPLO}.csv', index=False)

    print('\n' + '=' * 80)
    print('RECOMENDAÇÃO POR UM GRUPO DE MÚSICAS')
    print('=' * 80)
    musicas_grupo, recomendacoes_grupo = recomendar_por_grupo(GRUPO_TRACK_IDS)
    print('Músicas do grupo:')
    for linha in musicas_grupo:
        print(f'  - {linha["track_name"]} — {linha["artists"]} ({linha["track_genre"]})')
    print('\n5 músicas mais parecidas com o perfil médio do grupo:')
    print(recomendacoes_grupo.to_string(index=False))
    recomendacoes_grupo.to_csv(PASTA_SAIDA / 'recomendacao_grupo.csv', index=False)

    print(f'\nCSVs gerados em: {PASTA_SAIDA.relative_to(RAIZ)}/')
