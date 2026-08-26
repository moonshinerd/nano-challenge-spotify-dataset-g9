# Relatório de Definição da Análise — Spotify Dataset

## 1. Objetivo da discussão

A reunião teve como objetivo definir as possibilidades de análise e desenvolvimento a partir do **Spotify Dataset**, estabelecendo quais abordagens serão priorizadas e quais poderão ser desenvolvidas posteriormente, de acordo com os resultados encontrados durante a exploração dos dados.

A principal decisão foi iniciar o trabalho pela **Análise Exploratória de Dados (EDA)**. Essa etapa será utilizada para compreender a estrutura do dataset, identificar padrões, relações entre atributos e possíveis insights antes da definição definitiva das funcionalidades posteriores.

---

## 2. Análise Exploratória de Dados

A **Análise Exploratória de Dados** foi definida como a primeira etapa do projeto.

O grupo considerou necessário compreender os dados antes de implementar mecanismos mais complexos, como sistemas de recomendação ou modelos de Machine Learning.

A análise deverá investigar características disponíveis no dataset, como:

* popularidade;
* gênero musical;
* energia (`energy`);
* dançabilidade (`danceability`);
* valência (`valence`);
* acústica (`acousticness`);
* instrumentalidade (`instrumentalness`);
* tempo (`tempo`);
* duração das músicas;
* demais atributos musicais disponíveis.

A partir dessas variáveis, será possível procurar relações, padrões, agrupamentos e diferenças entre músicas e gêneros.

### 2.1. Geração de insights

Um dos principais resultados esperados da análise exploratória é a geração de **insights sobre o conjunto de dados**.

Entre as questões que poderão ser investigadas estão:

* Quais características aparecem com maior frequência em músicas populares?
* Existe relação entre `danceability` e popularidade?
* Existe relação entre `energy` e popularidade?
* Quais características diferenciam os gêneros musicais?
* Existem grupos de músicas com características semelhantes?
* Determinados gêneros apresentam perfis específicos de energia, valência ou acústica?
* Quais atributos parecem estar mais associados à popularidade?

Esses insights serão utilizados para orientar as próximas decisões do projeto.

> A escolha das funcionalidades posteriores não será feita apenas com base nas ideias iniciais. O objetivo é utilizar os resultados da análise exploratória para determinar quais abordagens fazem mais sentido para os dados disponíveis.

---

## 3. Criação de perfis musicais

Uma das possibilidades consideradas prioritárias é a criação de **perfis musicais a partir das características das próprias músicas**.

Nesse contexto, "perfil musical" não representa necessariamente o perfil de um usuário, mas uma caracterização de uma música com base em seus atributos.

Por exemplo, uma música poderá ser caracterizada como:

* altamente energética;
* altamente dançante;
* pouco acústica;
* positiva ou negativa em termos de `valence`;
* instrumental ou predominantemente vocal;
* rápida ou lenta.

A combinação dessas características permite representar músicas de maneira mais estruturada e posteriormente comparar músicas com perfis semelhantes.

---

## 4. Sugestão e recomendação de músicas

A partir dos perfis musicais, foi considerada a possibilidade de desenvolver um mecanismo de **sugestão de músicas**.

A ideia é utilizar as características das músicas para encontrar outras faixas semelhantes.

Um fluxo conceitual possível seria:

```text
Música selecionada
        ↓
Extração de suas características
        ↓
Construção do perfil musical
        ↓
Comparação com outras músicas
        ↓
Identificação das músicas mais semelhantes
        ↓
Sugestões
```

Dessa forma, o usuário poderia selecionar uma música e o sistema retornaria outras músicas que apresentam características próximas.

Exemplo:

> "Se você gosta desta música, estas são algumas músicas com características semelhantes."

Essa abordagem foi considerada interessante principalmente por permitir verificar visualmente e experimentalmente se as recomendações produzidas fazem sentido.

---

## 5. Criação de playlists por características

Outra possibilidade discutida foi utilizar os atributos musicais para criar **playlists temáticas**.

Em vez de depender exclusivamente do gênero musical, as músicas poderiam ser selecionadas de acordo com suas características.

Por exemplo, uma playlist para festa poderia priorizar músicas com:

* alta `danceability`;
* alta `energy`;
* determinadas faixas de `valence`;
* características acústicas compatíveis com o contexto.

Assim, seria possível criar categorias como:

```text
Spotify Dataset
      ↓
Características musicais
      ↓
Classificação por perfil
      ↓
┌──────────────┬──────────────┬──────────────┐
│    Festa     │   Relaxante  │  Energética  │
└──────────────┴──────────────┴──────────────┘
```

As categorias definitivas deverão ser determinadas posteriormente, considerando os padrões encontrados durante a análise exploratória.

---

## 6. Similaridade entre músicas

Também foi discutida uma abordagem baseada na **proximidade entre músicas**.

A proposta consiste em representar cada música por um conjunto de características e calcular o quanto uma música está próxima de outra.

Características como:

```text
danceability
energy
valence
acousticness
instrumentalness
tempo
```

podem formar uma representação numérica de cada faixa.

Conceitualmente:

```text
                 Música A
                    ●
                  /   \
                 /     \
            ● Música B  ● Música C


                          ● Música D
```

Quanto mais próximas estiverem duas músicas nesse espaço de características, maior poderá ser sua similaridade musical de acordo com os critérios definidos.

Essa abordagem poderia posteriormente ser utilizada como base para um mecanismo de recomendação.

Devido ao tamanho do dataset, também foi discutida a possibilidade de trabalhar inicialmente com um subconjunto de músicas, como as faixas mais populares, caso seja necessário reduzir o custo computacional ou facilitar a visualização.

---

## 7. Machine Learning e previsão de popularidade

Outra proposta discutida foi utilizar **Machine Learning** para estimar a popularidade de uma música com base em suas características.

O problema poderia ser estruturado de forma semelhante a:

```text
Características da música
        ↓
danceability
energy
tempo
valence
acousticness
...
        ↓
Modelo de Machine Learning
        ↓
Popularidade estimada
```

A ideia seria permitir que determinadas características de uma música fossem fornecidas ao modelo e, a partir delas, fosse realizada uma previsão relacionada à sua popularidade.

Entretanto, o grupo identificou que essa abordagem apresenta maior complexidade técnica, envolvendo conceitos como:

* preparação dos dados;
* seleção de atributos;
* treinamento do modelo;
* separação entre dados de treino e teste;
* avaliação do modelo;
* problemas de regressão;
* análise dos resultados.

Por esse motivo, **Machine Learning não será a prioridade inicial do projeto**.

A possibilidade não foi descartada. Ela poderá ser retomada caso o andamento do projeto e o tempo disponível permitam.

---

## 8. Priorização definida

Com base na discussão, foi estabelecida a seguinte ordem geral de desenvolvimento:

```text
1. Tratamento e compreensão dos dados
                 ↓
2. Análise Exploratória de Dados
                 ↓
3. Identificação de insights
                 ↓
4. Construção de perfis musicais
                 ↓
5. Sugestão/recomendação de músicas
                 ↓
6. Possíveis extensões
      ├── Playlists temáticas
      ├── Similaridade entre músicas
      └── Machine Learning
```

A **Análise Exploratória de Dados** constitui, portanto, o núcleo inicial do projeto.

As demais funcionalidades serão definidas e refinadas conforme os resultados encontrados nessa etapa.

---

## 9. Decisões consolidadas

| Proposta                        | Decisão                         | Prioridade      |
| ------------------------------- | ------------------------------- | --------------- |
| Análise Exploratória de Dados   | Desenvolver                     | **Muito alta**  |
| Geração de insights             | Desenvolver durante a EDA       | **Muito alta**  |
| Perfil das músicas              | Desenvolver                     | **Alta**        |
| Sugestão de músicas             | Desenvolver a partir dos perfis | **Alta**        |
| Playlists por características   | Possível extensão               | **Média**       |
| Similaridade entre músicas      | Possível extensão               | **Média/Baixa** |
| Previsão de popularidade com ML | Avaliar posteriormente          | **Baixa**       |

---

## 10. Conclusão

A principal conclusão da reunião foi que o projeto deve ser conduzido de maneira incremental, começando pela **compreensão e exploração do Spotify Dataset**.

Antes de escolher definitivamente um algoritmo ou uma aplicação específica, o grupo deverá identificar o que os próprios dados permitem descobrir.

A análise exploratória será responsável por revelar relações entre características musicais, gêneros e popularidade, além de fornecer os insights necessários para fundamentar as etapas posteriores.

A partir desses resultados, a direção considerada mais promissora é a construção de **perfis de músicas**, seguida pela utilização desses perfis para **identificar músicas semelhantes e produzir sugestões ou recomendações**.

Funcionalidades mais complexas, especialmente modelos de **Machine Learning para previsão de popularidade**, permanecem como possibilidades de extensão e deverão ser avaliadas de acordo com o tempo disponível, a qualidade dos dados e os resultados obtidos nas etapas anteriores.
