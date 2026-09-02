# Nano Challenge — Spotify Dataset

Análise exploratória e construção de perfis musicais a partir de um dataset
de faixas do Spotify (~114 mil linhas, atributos de áudio como `danceability`,
`energy`, `valence`, `acousticness`, etc.). Ver a definição completa do
problema e as decisões do grupo em [docs/atas/](docs/atas/).

📍 **Status atual e jornada completa do projeto:** [docs/README.md](docs/README.md).

## Estrutura do repositório

```
.
├── data/
│   ├── raw/                     # dataset original, não editado
│   └── processed/                # dados gerados pelos scripts (ex: perfis musicais)
├── docs/
│   ├── README.md                 # índice da documentação + status/jornada do projeto
│   ├── atas/                     # atas de reunião do grupo
│   ├── dados_explicados.md       # dicionário de dados (o que cada coluna significa)
│   ├── analise_sobreposicao_generos.md
│   ├── perfil_musical.md         # critérios das playlists da etapa 3
│   └── anotacoes.md
├── src/
│   ├── shared/
│   │   └── dados.py              # carregamento e limpeza de dados, usado por todas as etapas
│   ├── 01_analise_exploratoria/  # EDA: popularidade, gênero, sentimento/correlações
│   ├── 02_perfis_musicais/       # classificação das músicas em perfis (dançante, energética, etc.)
│   ├── 03_playlists/             # playlists temáticas (relax, treino, romance, popular)
│   └── 04_recomendacao/          # sugestão de músicas parecidas, por faixa ou por grupo
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

### 3. Playlists por características (`src/03_playlists/`)

`playlists.py` monta 4 playlists de 10 músicas (RELAX, TREINO, ROMANCE, POPULAR)
a partir dos critérios definidos em [docs/perfil_musical.md](docs/perfil_musical.md),
usando os mesmos tercis da etapa 2 para definir "alto"/"baixo" em cada variável.
Também reporta a predominância de gêneros em cada perfil. Resultado salvo em
`data/processed/playlists/`.

> Nota: o critério original de ROMANCE (loudness alto) foi ajustado — `energy`
> e `loudness` têm correlação de 0.76 no dataset, então exigir energy baixo
> junto com loudness alto deixava só 5 músicas candidatas. Ver comentário no
> próprio script para o detalhe.

### 4. Sugestão e recomendação de músicas (`src/04_recomendacao/`)

`recomendacao.py` recebe um `track_id` (ou uma lista de `track_id`s, definidos
em variáveis no topo do script) e retorna as 5 músicas mais parecidas, usando
similaridade de cosseno sobre todas as características de áudio normalizadas
(z-score) — `danceability`, `energy`, `key`, `loudness`, `mode`,
`speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`,
`tempo`, `duration_ms`, `explicit`, `time_signature` — exceto `popularity`
(propositalmente fora: é métrica de sucesso, não de som). Quando a entrada é
um grupo de músicas, a comparação é feita contra o perfil médio do grupo.
Resultado salvo em `data/processed/recomendacoes/`.

## Como rodar

Este projeto usa [uv](https://docs.astral.sh/uv/) para gerenciar dependências.

```bash
uv sync

# execute a partir da raiz do repositório
uv run python src/01_analise_exploratoria/insights_popularity.py
uv run python src/01_analise_exploratoria/insights_genero.py
uv run python src/01_analise_exploratoria/insights_sentimento.py
uv run python src/02_perfis_musicais/perfis.py
uv run python src/03_playlists/playlists.py
uv run python src/04_recomendacao/recomendacao.py
```

## Dicionário de dados

O significado de cada coluna do dataset (incluindo a relação entre `key` e
`mode`) está documentado em [docs/dados_explicados.md](docs/dados_explicados.md).
