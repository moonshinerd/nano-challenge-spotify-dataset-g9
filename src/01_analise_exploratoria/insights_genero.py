## generos
##Quais gêneros têm maior valence, (key e mode) e como isso se relaciona com o restante da variaveis?
##Quais generos tem mais acusticos e como isso se relaciona com o restante das variaveis?
##quais generos tem speechiness e como isso se relaciona com o restante das variaveis?
##Quais gêneros possuem BPM mais alto? -> perfil musical 
##Quais características diferenciam generos(rock, acoustic, hip-hop, classical etc.)? 

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shared'))
from dados import carregar_dataset  # noqa: E402

CAMINHO_DATASET = Path(__file__).resolve().parents[2] / 'data' / 'raw' / 'dataset.csv'

# Carrega o dataset (mojibake corrigido) e remove faixas sem identificação de gênero.
df = carregar_dataset(CAMINHO_DATASET)
df.dropna(subset=['track_genre'], inplace=True)


# Evita que relançamentos da mesma música pesem várias vezes no perfil do gênero.
df_unique = df.sort_values('popularity', ascending=False).drop_duplicates(
	subset=['track_name', 'artists', 'track_genre']
)

colunas_audio = [
	'popularity', 'danceability', 'energy', 'valence', 'acousticness',
	'instrumentalness', 'loudness', 'speechiness', 'liveness', 'tempo',
	'key', 'mode'
]

perfil_generos = df_unique.groupby('track_genre')[colunas_audio].mean()
quantidade_por_genero = df_unique.groupby('track_genre').size().rename('quantidade')
perfil_generos = perfil_generos.join(quantidade_por_genero)


def ranking_por(variavel, quantidade=10):
	return perfil_generos.sort_values(variavel, ascending=False)[
		[variavel, 'quantidade']
	].head(quantidade)


def percentual(valor):
	return f'{valor * 100:.1f}%'


# 1. Gêneros com maior valence, além de key e mode mais frequentes.
top_valence = ranking_por('valence')
key_mais_frequente = df_unique.groupby('track_genre')['key'].agg(
	lambda valores: valores.mode().iloc[0]
)
mode_mais_frequente = df_unique.groupby('track_genre')['mode'].agg(
	lambda valores: valores.mode().iloc[0]
)
perfil_tonal = pd.DataFrame({
	'key_mais_frequente': key_mais_frequente,
	'modo_mais_frequente': mode_mais_frequente,
	'valence_media': perfil_generos['valence'],
	'energy_media': perfil_generos['energy'],
	'danceability_media': perfil_generos['danceability'],
}).sort_values('valence_media', ascending=False)


# 2. Gêneros mais acústicos e relação da acousticness com as demais variáveis.
top_acousticness = ranking_por('acousticness')
correlacoes_acousticness = df_unique[
	colunas_audio
].corr()['acousticness'].drop('acousticness').sort_values(ascending=False)


# 3. Gêneros com maior speechiness e relação entre speechiness e o restante.
top_speechiness = ranking_por('speechiness')
correlacoes_speechiness = df_unique[
	colunas_audio
].corr()['speechiness'].drop('speechiness').sort_values(ascending=False)


# 4. Gêneros com maior BPM.
top_tempo = ranking_por('tempo')


# 5. Perfis médios para gêneros de referência presentes na planilha.
generos_referencia = ['rock', 'acoustic', 'hip-hop', 'classical', 'pop']
generos_presentes = [
	genero for genero in generos_referencia if genero in perfil_generos.index
]
colunas_perfil = [
	'danceability', 'energy', 'valence', 'acousticness',
	'instrumentalness', 'speechiness', 'liveness', 'tempo'
]
comparacao_generos = perfil_generos.loc[generos_presentes, colunas_perfil]


pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print('=' * 70)
print('ANÁLISE DE GÊNEROS')
print('=' * 70)
print(f'Faixas analisadas: {len(df_unique)} | Gêneros: {len(perfil_generos)}\n')

print('1. Gêneros com maior valence e perfil tonal (key/mode):')
print(top_valence)
print('\nPerfil tonal dos gêneros ordenado por valence:')
print(perfil_tonal.head(10))
print('\nInterpretação: valence mais alto indica associação com um caráter mais positivo.\n')

print('2. Gêneros mais acústicos:')
print(top_acousticness)
print('\nCorrelação da acousticness com as demais variáveis:')
print(correlacoes_acousticness.round(3))
print('\nInterpretação: correlação positiva indica que as duas variáveis tendem a subir juntas; negativa indica tendência oposta.\n')

print('3. Gêneros com maior speechiness:')
print(top_speechiness)
print('\nCorrelação da speechiness com as demais variáveis:')
print(correlacoes_speechiness.round(3))
print()

print('4. Gêneros com BPM médio mais alto:')
print(top_tempo)
print()

print('5. Características dos gêneros de referência presentes:')
if comparacao_generos.empty:
	print('Nenhum dos gêneros de referência foi encontrado na planilha.')
else:
	print(comparacao_generos.round(3))
