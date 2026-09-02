# Análise Exploratória — Resultados

Resumo dos achados da EDA, respondendo às perguntas levantadas em
[docs/anotacoes.md](../../docs/anotacoes.md). Os números vêm da execução dos
3 scripts desta pasta sobre `data/raw/dataset.csv` (114 gêneros, ~1000 faixas
cada, 81.341 músicas únicas após remover duplicatas de relançamento).

Para reproduzir: `uv run python src/01_analise_exploratoria/insights_<nome>.py`.

---

## Popularidade (`insights_popularity.py`)

* **Gêneros mais populares em média:** `pop-film` (59,3), `k-pop` (57,0), `chill` (53,7), `sad` (52,4), `grunge` (49,6).
* **Danceability e popularidade:** correlação de **0,096** — praticamente nula. Ser dançante não torna uma música mais popular.
* **Popularidade depende do artista?** Sim, fortemente: os 10 artistas com maior popularidade média (ex: Sam Smith;Kim Petras, Bizarrap;Quevedo, Bad Bunny) coincidem quase exatamente com os artistas das 10 faixas mais populares do dataset — indício forte de que popularidade está muito ligada ao artista, não só à música isolada.
* **Faixas explícitas:** popularidade média de **39,4** contra **34,9** das não explícitas — faixas explícitas são, em média, mais populares.
* **Instrumentalidade:** correlação de **-0,188** com popularidade (fraca, negativa) — músicas mais instrumentais tendem a ser um pouco menos populares. É a variável com correlação mais forte (em módulo) com popularity entre as testadas.
* **BPM (tempo):** correlação de **0,0** — tempo não influencia popularidade.
* **Duração:** as 100 músicas mais populares duram em média 3,47 min, contra 3,86 min do restante — faixas populares tendem a ser um pouco mais curtas.
* Cada gênero tem exatamente 1000 faixas no dataset bruto (amostragem uniforme por gênero).

## Sentimento e acústica (`insights_sentimento.py`)

* **Energy × Loudness:** correlação **forte positiva de 0,761** — a mais forte encontrada em toda a EDA. *(Importante: essa correlação foi o motivo de termos ajustado o critério da playlist ROMANCE na etapa 3 — "energy baixo + loudness alto" é quase inexistente no dataset.)*
* **Acousticness** se relaciona fortemente com **energy (-0,731)** e moderadamente com **loudness (-0,582)** — músicas acústicas são tipicamente calmas e mais baixas em volume. Relação praticamente nula com speechiness e liveness.
* **Valence (positividade) × Danceability:** correlação moderada positiva de **0,492** — músicas mais "felizes" tendem a ser mais dançantes. Valence também se relaciona fraco/positivo com loudness (0,289) e energy (0,254).
* **Liveness:** relação fraca negativa com danceability (-0,133) e quase nula com loudness (0,081) — gravações ao vivo não são nem mais dançantes nem necessariamente mais altas.

## Gêneros (`insights_genero.py`)

* **Maior valence (mais "positivos"):** `salsa` (0,81), `forro` (0,76), `rockabilly` (0,71), `ska` (0,70), `afrobeat` (0,70) — gêneros latinos/dançantes dominam o topo.
* **Mais acústicos:** `classical` (0,91), `romance` (0,87), `tango` (0,85), `new-age` (0,83), `opera` (0,80).
* **Maior speechiness:** `comedy` se destaca isolado com 0,76 (conteúdo majoritariamente falado); em seguida `j-dance`, `dancehall`, `funk`, `kids`, todos abaixo de 0,22 — a diferença de comedy pro resto é enorme.
* **Maior BPM médio:** `drum-and-bass` (155), `happy` (153), `hardstyle` (147), `forro` (140), `j-idol` (136).
* **Gêneros de referência (rock, acoustic, hip-hop, classical, pop):** confirmam o padrão esperado — `classical` com acousticness altíssima (0,91) e energy baixíssima (0,20); `hip-hop` com maior danceability (0,72) do grupo; `rock` com tempo mais alto (123 BPM) do grupo.

---

## Conclusões que orientaram as próximas etapas

1. **`energy`, `loudness` e `acousticness` são as variáveis mais correlacionadas entre si** (energy↔loudness: 0,76; energy↔acousticness: -0,73) — por isso, na etapa 2 (perfis musicais) e 3 (playlists), perfis que misturam essas três variáveis em direções opostas geram poucos ou nenhum resultado.
2. **Popularidade não é bem explicada pelos atributos de áudio isolados** (todas as correlações ficaram abaixo de 0,2 em módulo) — reforça a decisão da ata-01 de não priorizar Machine Learning para prever popularidade nesta fase.
3. **Gêneros têm perfis de áudio bem diferenciados** (valence, acousticness, speechiness, tempo variam muito entre eles) — validou a decisão de seguir para a construção de perfis musicais por características (etapa 2) e não só por gênero.

Ver o andamento completo do projeto em [docs/README.md](../../docs/README.md).
