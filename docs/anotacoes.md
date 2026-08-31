# Anotações

1) Análise exploratória de dados

## popularity
Quais gêneros têm maior popularity média?
Músicas populares tendem a ser mais danceability?
Música só são mais populares por causa da popularidade do artista? 
As músicas mais populares são relacionadas a algum artista em específico?
Músicas explícitas são, em média, mais populares?
Músicas instrumentais são menos populares?
Músicas com BPM mais alto são mais populares?

## sentimento que a musica evoca (key, mode, valence, energy)
Existe relação entre energy e loudness?
Músicas acousticness tendem se relacionam a quais variaveis?
a relação do sentimento gerado pela muica com a dançabilidade e como isso se relaciona com o restante das variaveis?
a relação entre liveness com danceability e loudness?

## generos
Quais gêneros têm maior valence, (key e mode) e como isso se relaciona com o restante da variaveis?
Quais generos tem mais acusticos e como isso se relaciona com o restante das variaveis?
quais generos tem speechiness e como isso se relaciona com o restante das variaveis?
Quais gêneros possuem BPM mais alto?
Quais características diferenciam generos(rock, acoustic, hip-hop, classical etc.)?

Por exemplo, você poderia produzir uma matriz de correlação entre:

popularity
danceability
energy
loudness
speechiness
acousticness
instrumentalness
liveness
valence
tempo

E descobrir relações como:

energy ↑  <-> loudness ↑
acousticness ↑ <-> energy ↓

Não significa necessariamente causalidade, mas ajuda a entender os dados.

2. Criar perfis de músicas

Você pode transformar os valores numéricos em uma espécie de perfil musical.

Imagine:

Música A

Danceability:       0.82
Energy:             0.91
Valence:            0.78
Acousticness:       0.05
Instrumentalness:   0.00
Tempo:              128 BPM

Você poderia descrevê-la como:

Música energética, dançante, positiva e pouco acústica.

Enquanto outra:

Danceability:       0.31
Energy:             0.22
Valence:            0.18
Acousticness:       0.91
Instrumentalness:   0.03
Tempo:              72 BPM

seria algo como:

Música lenta, acústica, pouco energética e com caráter emocional mais melancólico.

Isso permite criar playlists automáticas por características.

Por exemplo:

Playlist "Academia"
energy > 0.75
danceability > 0.60
tempo > 110

Playlist "Relaxar"
energy < 0.40
acousticness > 0.60
tempo < 100

Playlist "Festa"
danceability > 0.75
energy > 0.70
valence > 0.60

Playlist "Sofrência"
valence < 0.30
energy < 0.50

Isso já poderia virar um projeto bem legal.

3. Machine Learning

A. Prever a popularidade de uma música

Você poderia usar:

Entradas:

danceability
energy
loudness
speechiness
acousticness
instrumentalness
liveness
valence
tempo
duration_ms
explicit
...

Para prever:

popularity

Isso seria um problema de regressão.

Por exemplo:

Características musicais
        ↓
Modelo
        ↓
Popularidade prevista = 68

Você poderia testar:

Regressão Linear
Decision Tree
Random Forest
Gradient Boosting
XGBoost

E comparar os resultados com métricas como:

MAE
MSE
RMSE
R²

B. Prever o gênero da música

Aqui temos outro problema.

Entradas:

danceability
energy
tempo
valence
acousticness
speechiness
instrumentalness
...

Saída:

track_genre

Agora temos um problema de classificação multiclasse.

Por exemplo:

energy = 0.91
danceability = 0.62
acousticness = 0.02
tempo = 142
instrumentalness = 0.01

                ↓

Random Forest

                ↓

rock

Você poderia usar:

KNN
Decision Tree
Random Forest
Logistic Regression
SVM
XGBoost
Redes neurais

E avaliar com:

accuracy
precision
recall
F1-score
confusion matrix

Esse é provavelmente um dos projetos de ML mais naturais para esse dataset.

4. Sistema de recomendação musical


Você pode criar um recomendador baseado em conteúdo.

Imagine que alguém escolha:

"Comedy — Gen Hoshino"

Você pega:

danceability
energy
acousticness
instrumentalness
valence
tempo
...

e representa a música como um vetor:

Comedy =
[0.676,
 0.461,
 0.0322,
 0.000001,
 0.715,
 87.917,
 ...]

Então compara com todas as outras músicas do dataset.

Uma forma muito comum seria usar similaridade de cosseno.

Comedy
   ↓
calcular similaridade
   ↓
Todas as músicas
   ↓
Top 10 mais semelhantes

O programa poderia retornar:

Você escolheu:

Comedy - Gen Hoshino

Músicas semelhantes:

1. Música X
2. Música Y
3. Música Z
4. Música W
5. Música K

Esse projeto é particularmente interessante porque envolve:

Pandas
NumPy
normalização de dados
distância entre vetores
Machine Learning
sistema de recomendação

E pode ficar muito bom no GitHub.

5. Descobrir grupos de músicas automaticamente

Você pode fazer Machine Learning não supervisionado.

Por exemplo, utilizar:

K-Means

sem passar os gêneros.

O algoritmo recebe:

danceability
energy
valence
tempo
acousticness
instrumentalness
...

e tenta descobrir grupos naturais.

Talvez apareça algo como:

Cluster 0
Alta energia
Alto BPM
Alta danceability

Cluster 1
Alta acousticness
Baixa energia
Baixo BPM

Cluster 2
Alta instrumentalness
Baixa speechiness

Cluster 3
Alta valence
Alta danceability

Depois você verifica quais gêneros aparecem nesses grupos.

Isso permite responder uma pergunta interessante:

As características acústicas das músicas conseguem reproduzir naturalmente os gêneros musicais?

Esse já é um problema de análise bastante interessante.

6. Criar um mapa das músicas

Você também pode usar redução de dimensionalidade, como:

PCA
t-SNE
UMAP

Imagine cada ponto abaixo representando uma música:

       • • •
     • • • •             × × ×
       • •             × × × ×
                          × ×


                 ▲ ▲ ▲
               ▲ ▲ ▲ ▲

E as cores representando gêneros.

Você poderia verificar se:

rock
metal
classical
acoustic
hip-hop
pop

se separam naturalmente quando analisamos suas características.

É uma visualização ótima para projeto acadêmico.

7. Investigar o que faz uma música popular

Esse seria um ótimo tema de análise.

Sua pergunta poderia ser:

Quais características musicais estão mais associadas à popularidade no Spotify?

Você analisaria variáveis como:

danceability
energy
valence
tempo
explicit
duration
acousticness
instrumentalness

contra:

popularity

Depois poderia usar um Random Forest, por exemplo, para obter feature importance:

danceability       █████████████
energy             ████████
loudness           ███████████████
valence            █████
tempo              ███
acousticness       ███████

E chegar a conclusões baseadas nos dados.

Só tomando cuidado para dizer:

"associado à popularidade"

e não:

"causa popularidade".

8. Analisar gêneros

Outra possibilidade é montar o perfil médio de cada gênero.

Por exemplo:

gênero	danceability	energy	acousticness	valence	tempo
acoustic	0.51	0.36	0.72	0.42	93
metal	0.43	0.91	0.03	0.38	138
pop	0.68	0.70	0.18	0.61	118
classical	0.29	0.18	0.89	0.22	85

E visualizar isso usando:

boxplots;
histogramas;
gráficos de dispersão;
radar charts;
heatmaps.

Se eu estivesse usando esse dataset para aprender Ciência de Dados/ML

Eu faria um projeto em sequência:

Spotify Music Analysis
        │
        ├── 1. Limpeza dos dados
        │
        ├── 2. Análise exploratória
        │
        ├── 3. Visualizações
        │
        ├── 4. Análise de correlação
        │
        ├── 5. Clustering de músicas
        │
        ├── 6. Classificação de gênero
        │
        ├── 7. Previsão de popularidade
        │
        └── 8. Sistema de recomendação

Isso te permitiria aprender praticamente todo o pipeline inicial de Data Science:

Pandas → NumPy → Matplotlib → Scikit-learn → avaliação de modelos → recomendação.

E há uma limitação importante: com essas colunas você consegue fazer principalmente um recomendador baseado nas características da música. Você não tem dados de comportamento de usuários, como quem ouviu o quê, likes ou playlists individuais, então não daria para fazer uma filtragem colaborativa de verdade apenas com esse dataset.

Para começar, eu escolheria uma pergunta de negócio/análise específica, como "é possível prever o gênero de uma música apenas pelas características de áudio?". É suficientemente interessante para você praticar EDA, pré-processamento, classificação e avaliação de modelos sem o projeto ficar gigantesco.


//Tratamento de dados
Dado que falta 
Dado duplicado
-> uma música pode ter mais de um gênero
observação: tratamento de dados 
-> é importante para não ter duplicidade de informações 
-> nomes das variáveis tratados
-> agrupamento dos ritmos 
