| Coluna             | Tipo / representação         | Significado                                                                                                                                                                                       |
| ------------------ | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `track_id`         | `string`                     | Identificador único da música no Spotify. Cada faixa possui um código próprio, como `5SuOikwiRyPMVoIQDJUgSV`.                                                                                     |
| `artists`          | `string`                     | Nome do artista ou dos artistas responsáveis pela faixa. Quando há colaboração, os nomes podem aparecer separados por `;`, como `Ingrid Michaelson;ZAYN`.                                         |
| `album_name`       | `string`                     | Nome do álbum ao qual a faixa pertence.                                                                                                                                                           |
| `track_name`       | `string`                     | Nome da música/faixa.                                                                                                                                                                             |
| `popularity`       | `int` — 0 a 100              | Índice de popularidade da faixa no Spotify. Quanto maior o valor, mais popular é a música. `0` representa baixa ou nenhuma popularidade e `100`, popularidade muito alta.                         |
| `duration_ms`      | `int`, em milissegundos      | Duração total da música em milissegundos. Para converter para segundos, divide-se por `1000`. Ex.: `230666 ms ≈ 230,7 s ≈ 3min51s`.                                                               |
| `explicit`         | `boolean` (`True` / `False`) | Indica se a faixa contém conteúdo considerado explícito. `True` = possui conteúdo explícito; `False` = não possui.                                                                                |
| `danceability`     | `float` — 0 a 1              | Mede o quanto uma música é adequada para dançar, considerando elementos como ritmo, estabilidade da batida e regularidade. Valores próximos de `1` indicam maior dançabilidade.                   |
| `energy`           | `float` — 0 a 1              | Representa a intensidade e atividade percebidas da música. Valores altos normalmente correspondem a músicas rápidas, intensas ou "energéticas"; valores baixos indicam músicas mais calmas.       |
| `key`              | `int` — 0 a 11               | Representa a tonalidade musical estimada da faixa. Os números correspondem às 12 notas da escala cromática.                                                                                       |
| `loudness`         | `float`, em dB               | Volume médio da faixa em **decibéis (dB)**. Normalmente possui valores negativos. Quanto mais próximo de `0`, maior tende a ser o volume percebido. Ex.: `-6 dB` é mais alto que `-17 dB`.        |
| `mode`             | `int` — 0 ou 1               | Indica o modo da escala musical: `1` = maior (som mais claro, feliz, estável) e `0` = menor (som mais sombrio, melancólico, tenso). Junto com `key`, define a tonalidade aproximada da música.    |
| `speechiness`      | `float` — 0 a 1              | Mede a presença de palavras/fala na faixa. Valores baixos são comuns em músicas; valores mais altos podem indicar rap muito falado, podcasts, discursos ou audiobooks.                            |
| `acousticness`     | `float` — 0 a 1              | Probabilidade/confiança de que a faixa seja acústica. Quanto mais próximo de `1`, maior a presença de características acústicas.                                                                  |
| `instrumentalness` | `float` — 0 a 1              | Estima a probabilidade de a faixa não possuir vocais. Valores próximos de `1` indicam músicas predominantemente instrumentais.                                                                    |
| `liveness`         | `float` — 0 a 1              | Mede a probabilidade de haver público ou características de uma apresentação ao vivo na gravação. Valores maiores sugerem maior possibilidade de ser uma gravação ao vivo.                        |
| `valence`          | `float` — 0 a 1              | Representa a positividade emocional percebida da música. Valores altos indicam músicas mais alegres, positivas ou eufóricas; valores baixos indicam músicas mais tristes, tensas ou melancólicas. |
| `tempo`            | `float`, em BPM              | Tempo estimado da música em **batidas por minuto (BPM)**. Ex.: `87.917` corresponde a aproximadamente 88 batidas por minuto.                                                                      |
| `time_signature`   | `int`                        | Compasso estimado da música, ou seja, quantas batidas existem em cada compasso. `4` normalmente representa o compasso **4/4**.                                                                    |
| `track_genre`      | `string` / categórica        | Gênero musical atribuído à faixa no dataset, como `acoustic`, `rock`, `pop`, `jazz`, etc.                                                                                                         |

Detalhe importante sobre KEY e MODE

`key` e `mode` aparecem separados no dataset, mas juntos eles definem a tonalidade aproximada da música. Em música, a tonalidade é formada por:

- `key`: a nota base da escala (ex.: C, D, G♯, etc.);
- `mode`: a qualidade dessa escala (maior ou menor).

Em outras palavras, `key` responde "qual nota é a base?" e `mode` responde "a música soa mais em tom maior ou menor?".

O `key` é representado por um número de 0 a 11:

| `key` | Nota                               |
| ----: | ---------------------------------- |
|     0 | C (Dó)                             |
|     1 | C♯ / D♭ (Dó sustenido / Ré bemol)  |
|     2 | D (Ré)                             |
|     3 | D♯ / E♭ (Ré sustenido / Mi bemol)  |
|     4 | E (Mi)                             |
|     5 | F (Fá)                             |
|     6 | F♯ / G♭ (Fá sustenido / Sol bemol) |
|     7 | G (Sol)                            |
|     8 | G♯ / A♭ (Sol sustenido / Lá bemol) |
|     9 | A (Lá)                             |
|    10 | A♯ / B♭ (Lá sustenido / Si bemol)  |
|    11 | B (Si)                             |

Já o `mode` é binário:

- `0` = menor
- `1` = maior

Isso significa que a música não é apenas "na nota C♯"; ela também pode ser "C♯ menor" ou "C♯ maior".

Exemplos:

- `key = 1` e `mode = 0` → C♯/D♭ menor
- `key = 1` e `mode = 1` → C♯/D♭ maior

A diferença prática é emocional:

- maior costuma soar mais alegre, brilhante, otimista;
- menor costuma soar mais melancólico, sombrio, intenso ou emocional.

Então, se uma faixa tem `key = 1` e `mode = 0`, ela foi estimada como sendo em C♯/D♭ menor. Se tiver `key = 1` e `mode = 1`, ela foi estimada como C♯/D♭ maior.

Esse tipo de informação é útil para análise de sentimento, estilo e agrupamento de músicas por atmosfera e contexto emocional.

Como interpretar uma linha inteira

Pegando a primeira música:

Gen Hoshino — Comedy

popularity = 73 → relativamente popular;
duration_ms = 230666 → aproximadamente 3 min 51 s;
explicit = False → não explícita;
danceability = 0.676 → razoavelmente dançante;
energy = 0.461 → energia intermediária;
key = 1 → C♯/D♭;
mode = 0 → tonalidade menor;
loudness = -6.746 dB → relativamente alta em comparação com músicas muito suaves;
speechiness = 0.143 → existe alguma presença de fala/vocal rítmico, mas continua sendo predominantemente música;
acousticness = 0.0322 → muito pouca característica acústica;
instrumentalness ≈ 0 → claramente não instrumental;
liveness = 0.358 → alguma característica associada a performance ao vivo, mas não muito forte;
valence = 0.715 → sonoridade emocional relativamente positiva;
tempo = 87.917 → aproximadamente 88 BPM;
time_signature = 4 → compasso 4/4;
track_genre = acoustic → classificada como gênero acoustic no dataset.

Um detalhe importante para análise de dados: danceability, energy, 
speechiness, acousticness, instrumentalness, liveness e valence já estão normalizadas
aproximadamente entre 0 e 1. Isso é especialmente útil quando você começar a fazer análise exploratória,
correlação ou modelos de Machine Learning com esse dataset.