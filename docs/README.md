# Documentação — Nano Challenge Spotify Dataset

Índice da documentação e status atual do projeto. Para a estrutura de pastas
e como rodar os scripts, ver o [README.md](../README.md) na raiz.

## Jornada do projeto

```
Definição do escopo (ata-01)
        ↓
1. Análise Exploratória de Dados ................ ✅ concluída
        ↓
2. Construção de perfis musicais ................. ✅ concluída
        ↓
3. Playlists por características ................. ✅ concluída
        ↓
4. Sugestão/recomendação de músicas .............. ✅ concluída
        ↓
5. Extensões (clustering, ML, mapa de músicas) ... 💤 não iniciadas
```

| Etapa | Status | Onde está | Resumo |
| --- | --- | --- | --- |
| 0. Definição do escopo | ✅ | [atas/ata-01.md](atas/ata-01.md), [atas/ata-02.md](atas/ata-02.md) | Decisão de começar pela EDA; priorização das próximas etapas; divisão de tarefas do time. |
| 1. Análise Exploratória | ✅ | [src/01_analise_exploratoria/](../src/01_analise_exploratoria/) | Todas as perguntas de [anotacoes.md](anotacoes.md) respondidas. Resumo dos achados em [analise.md](../src/01_analise_exploratoria/analise.md). |
| 2. Perfis musicais | ✅ | [src/02_perfis_musicais/](../src/02_perfis_musicais/) | Cada música classificada em tercis (baixo/médio/alto) de danceability, energy, acousticness, valence, tempo + regra binária de instrumentalness. Saída: `data/processed/perfis_musicais.csv`. |
| 3. Playlists por características | ✅ | [src/03_playlists/](../src/03_playlists/) | 4 playlists de 10 músicas (RELAX, TREINO, ROMANCE, POPULAR) definidas em [perfil_musical.md](perfil_musical.md). Saída: `data/processed/playlists/`. |
| 4. Sugestão/recomendação de músicas | ✅ | [src/04_recomendacao/](../src/04_recomendacao/) | Dado um `track_id` (ou uma lista deles), retorna as 5 músicas mais parecidas por similaridade de cosseno sobre todas as características de áudio normalizadas (exceto `popularity`). Saída: `data/processed/recomendacoes/`. |
| 5. Extensões (ML, clustering, mapa de músicas) | 💤 não iniciadas | — | Baixa prioridade, ver [anotacoes.md](anotacoes.md) e ata-01 seção 7. |

## Achados que atravessaram várias etapas

* **`energy` e `loudness` têm correlação de 0,76** (a mais forte do dataset) e
  `acousticness` correlaciona fortemente (negativo) com ambas. Isso limitou
  quais combinações de perfil fazem sentido pedir nas etapas 2 e 3 — por
  exemplo, a playlist ROMANCE originalmente pedia "energy baixo + loudness
  alto", uma combinação quase inexistente nos dados (só 5 músicas), então o
  critério foi ajustado. Ver comentário em
  [src/03_playlists/playlists.py](../src/03_playlists/playlists.py).
* **Atributos de áudio isolados explicam pouco da popularidade** (todas as
  correlações abaixo de 0,2 em módulo) — reforça a decisão de não priorizar
  Machine Learning preditivo nesta fase do projeto.

## Índice de documentos

| Documento | Conteúdo |
| --- | --- |
| [dados_explicados.md](dados_explicados.md) | Dicionário de dados: o que cada coluna do dataset significa. |
| [anotacoes.md](anotacoes.md) | Perguntas de análise levantadas pelo grupo e ideias de projeto (EDA, perfis, ML, recomendação, clustering). Marcadas conforme respondidas. |
| [analise_sobreposicao_generos.md](analise_sobreposicao_generos.md) | Por que uma mesma música aparece com vários gêneros no dataset (ex: `latin`/`latino`, `dub`/`dubstep`) e quando isso precisa ser tratado. |
| [perfil_musical.md](perfil_musical.md) | Especificação dos critérios de cada playlist temática (etapa 3). |
| [atas/](atas/) | Atas das reuniões do grupo. |
