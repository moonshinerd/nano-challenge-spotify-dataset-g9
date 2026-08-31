"""
Funções de carregamento e limpeza de dados compartilhadas entre os scripts
de análise (insights_popularity.py, insights_genero.py, insights_sentimento.py
e os scripts da etapa src/02_perfis_musicais).

Centraliza o tratamento que antes estava duplicado em cada script:
- correção de mojibake (acentos quebrados) em texto;
- remoção de faixas sem nome/artista;
- deduplicação de músicas que aparecem mais de uma vez no dataset
  (mesmo nome + artista, mas track_id diferente por conta de álbum/single),
  mantendo a versão mais popular e concatenando os gêneros/ids.
"""
import pandas as pd


def fix_mojibake(text):
    """Corrige acentos quebrados (ex: TitÃ­ Me PreguntÃ³) causados por encoding errado."""
    if not isinstance(text, str):
        return text
    try:
        return text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def carregar_dataset(caminho):
    """Carrega o dataset bruto, remove faixas sem nome/artista e corrige o encoding dos textos."""
    df = pd.read_csv(caminho, index_col=0)
    df.dropna(subset=['track_name', 'artists'], inplace=True)
    for col in ['track_name', 'album_name', 'artists']:
        df[col] = df[col].apply(fix_mojibake)
    return df


def construir_df_unique(df):
    """
    Remove a duplicidade de faixas (mesma música, IDs diferentes por álbum/single).
    Mantém a linha com maior popularity e concatena os gêneros/ids únicos da música
    em uma só linha. Use esta versão sempre que a análise NÃO for por track_genre
    (caso contrário, uma mesma música com 3 gêneros pesaria 3x).
    """
    agrupado_por_musica = df.groupby(['track_name', 'artists'], dropna=False).agg({
        'track_genre': lambda x: ', '.join(x.dropna().astype(str).unique()),
        'track_id': lambda x: ', '.join(x.dropna().astype(str).unique())
    }).reset_index()

    df_unique = df.sort_values('popularity', ascending=False).drop_duplicates(
        subset=['track_name', 'artists']
    )
    df_unique = pd.merge(
        df_unique.drop(columns=['track_genre', 'track_id']),
        agrupado_por_musica,
        on=['track_name', 'artists'],
        how='left'
    )
    return df_unique


def carregar_df_unique(caminho):
    """Atalho: carrega o dataset já tratado e deduplicado por música."""
    return construir_df_unique(carregar_dataset(caminho))
