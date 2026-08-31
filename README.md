# Nano Challenge — Spotify Dataset

Análise exploratória e construção de perfis musicais a partir de um dataset
de faixas do Spotify (~114 mil linhas, atributos de áudio como `danceability`,
`energy`, `valence`, `acousticness`, etc.). Ver a definição completa do
problema e as decisões do grupo em [docs/atas/](docs/atas/).

## Estrutura do repositório

```
.
├── data/
│   ├── raw/                     # dataset original, não editado
│   └── processed/                # dados gerados pelos scripts (ex: perfis musicais)
├── docs/
│   ├── atas/                     # atas de reunião do grupo
│   ├── dados_explicados.md       # dicionário de dados (o que cada coluna significa)
│   ├── analise_sobreposicao_generos.md
│   └── anotacoes.md
├── src/
│   ├── shared/
│   │   └── dados.py              # carregamento e limpeza de dados, usado por todas as etapas
│   ├── 01_analise_exploratoria/  # EDA: popularidade, gênero, sentimento/correlações
│   └── 02_perfis_musicais/       # classificação das músicas em perfis (dançante, energética, etc.)
├── pyproject.toml
└── uv.lock
```

Cada etapa em `src/` é numerada na ordem em que foi (ou será) desenvolvida,
seguindo a priorização definida em [docs/atas/ata-01.md](docs/atas/ata-01.md).

## Etapas

### 1. Análise exploratória (`src/01_analise_exploratoria/`)

Scripts que respondem as perguntas levantadas em [docs/anotacoes.md](docs/anotacoes.md)
sobre popularidade, gênero e sentimento das faixas:

- `insights_popularity.py` — o que está associado à popularidade de uma música;
- `insights_genero.py` — perfil médio de cada gênero e o que os diferencia;
- `insights_sentimento.py` — correlações entre energy, loudness, valence, acousticness etc.

### 2. Perfis musicais (`src/02_perfis_musicais/`)

`perfis.py` classifica cada música em tercis (baixo/médio/alto, calculados sobre
a própria distribuição do dataset) para danceability, energy, acousticness,
valence e tempo, além de uma regra binária para instrumentalness. O resultado
é salvo em `data/processed/perfis_musicais.csv` e serve de base para a próxima
etapa do projeto: sugestão/recomendação de músicas por similaridade de perfil.

## Como rodar

Este projeto usa [uv](https://docs.astral.sh/uv/) para gerenciar dependências.

```bash
uv sync

# execute a partir da raiz do repositório
uv run python src/01_analise_exploratoria/insights_popularity.py
uv run python src/01_analise_exploratoria/insights_genero.py
uv run python src/01_analise_exploratoria/insights_sentimento.py
uv run python src/02_perfis_musicais/perfis.py
```

## Dicionário de dados

O significado de cada coluna do dataset (incluindo a relação entre `key` e
`mode`) está documentado em [docs/dados_explicados.md](docs/dados_explicados.md).
