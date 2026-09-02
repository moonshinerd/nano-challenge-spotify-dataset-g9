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

---

# 🚀 Spotify Recommender (Aplicação Full-Stack & AI)

Na fase mais avançada do projeto, a lógica de recomendação baseada em Z-Score e Distância de Cosseno foi encapsulada em uma API de alta performance e conectada a uma interface web moderna inspirada no Spotify. 

A arquitetura agora evoluiu para um sistema distribuído usando **Docker Compose**, contendo:
- **Banco de Dados Vetorial (PostgreSQL + pgvector)**
- **API Backend (Python + FastAPI)**
- **Aplicação Frontend (React + Vite + TailwindCSS)**

## 🌟 Funcionalidades da Interface

A nova interface web (`web/src/App.jsx`) não é apenas um buscador; é um ecossistema musical completo que funciona da seguinte forma:

1. **Busca Híbrida Inteligente:**
   - O usuário pode digitar o nome de qualquer música no campo de busca.
   - O sistema procura primeiro no **Catálogo Local (Banco de Dados Vetorial)** que agora contém **mais de 820.000 músicas**.
   - **Músicas Inéditas (Cold Start):** Se a música não for encontrada localmente, a API bate no YouTube em tempo real, faz o download do áudio, extrai os 11 atributos acústicos vitais com o *Librosa*, ajusta o *Domain Shift* matemático (para compensar o algoritmo do Spotify vs. Librosa) e injeta a nova música imediatamente no banco como um novo vetor.

2. **Recomendações Acústicas Profundas:**
   - Ao clicar em "Analisar & Recomendar" numa música, o banco vetorial usa **Cosine Similarity** sobre as 14 dimensões padronizadas para achar músicas exatamente com a mesma "Vibe" (mesma valência, energia, dançabilidade, etc).
   - Não importa o gênero: você pode descobrir um jazz que soa identicamente como uma música de rock que você escolheu.
   - **Garantia de Diversidade:** A recomendação é filtrada para trazer, no máximo, 2 músicas do mesmo artista, evitando bolhas de catálogo.

3. **Geração de "Super Mix" (Playlist Centróide):**
   - O usuário pode montar uma Playlist Base adicionando várias músicas num carrinho lateral.
   - Clicando em "Gerar Super Mix ✨", a IA calcula o **Centróide Matemático** (a média perfeita multidimensional de todas as faixas escolhidas) e busca novas músicas que orbitam o centro absoluto do seu gosto musical recente.

4. **Descoberta de Gêneros em Tempo Real (Lazy Load):**
   - Músicas cadastradas massivamente que vieram sem a tag de "Gênero" entram como "desconhecido" para não engasgar o carregamento.
   - Quando elas aparecem na tela, a API busca automaticamente as tags oficias via *iTunes API* por baixo dos panos, renderiza, e atualiza o banco de dados.

5. **Audio Player Global & Queue:**
   - Reprodução direta do áudio pelo navegador! As músicas são roteadas do *YouTube Music* através da nossa API (com um bypass do `yt-dlp` para evitar os bloqueios de estrangulamento (Bot/403) do YouTube).
   - O player suporta tocar faixas individuais ou a playlist completa, avançando e retrocedendo (Skip Next/Prev) a fila automaticamente, com animações responsivas e um *Marquee Effect* (texto deslizante) elegante para nomes compridos.

## 🛠️ Como Rodar a Interface Completa

Toda a arquitetura, as dependências, e a ingestão massiva de dados estão automatizadas num orquestrador do **Docker**. Basta rodar um único comando:

```bash
docker compose up --build
```

**O que o Docker vai fazer automaticamente por você:**
1. Subir o container `db` (Postgres com extensão de IA `pgvector`).
2. Subir o container temporário `setup`, que vai:
   - Carregar o Dataset Original (81k).
   - Aplicar normalização estatística (Z-Score) baseado nas médias absolutas.
   - Importar o Dataset Gigante Adicional (~740k músicas limpas), descartando as duplicatas (`ON CONFLICT DO NOTHING`).
3. Somente quando o setup finalizar a ingestão dos quase **1 Milhão de vetores acústicos**, a `api` ligará na porta `:8000`.
4. O `web` ligará na porta `:5173`. 
5. Acesse `http://localhost:5173` no seu navegador e desfrute da recomendação pura.
