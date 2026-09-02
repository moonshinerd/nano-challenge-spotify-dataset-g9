# Apresentacao — Spotify Dataset

## Narrativa central

**Descobrir musica nao precisa depender apenas do que ja e popular.** A analise mostrou que popularidade e atributos sonoros contam historias diferentes: as caracteristicas de audio isoladas explicam pouco o sucesso, mas combinadas formam uma representacao util para encontrar faixas com a mesma vibe. A partir disso, o projeto evoluiu de uma EDA para perfis musicais, playlists por contexto e recomendacao por similaridade.

A historia da apresentacao e:

> **Problema:** catalogos grandes dificultam descobrir musica relevante fora do obvio.  
> **Evidencia:** popularidade nao captura bem a semelhanca sonora; os atributos de audio revelam padroes e perfis.  
> **Oportunidade:** transformar caracteristicas sonoras em uma camada de descoberta.  
> **Solucao:** perfis, playlists e recomendacoes por similaridade, integrados em uma aplicacao web.  
> **Processo:** EDA primeiro, decisoes guiadas por evidencias e ajustes quando os dados contrariaram a ideia inicial.

> **Nota de integridade:** numeros de correlacao, popularidade, volumes e exemplos abaixo foram retirados dos documentos e outputs existentes. Onde nao ha metricas de produto ou contribuicoes individuais registradas, a apresentacao indica `[INFORMACAO A SER PREENCHIDA]`.

---

# PARTE 1 — PITCH DA SOLUCAO — 5 MINUTOS

## Slide 1 — O catalogo sabe o que e popular; nos queremos descobrir o que combina

**Objetivo do slide:** Abrir com o problema de descoberta e apresentar a tese do projeto.

**Conteudo:**

- Pergunta de abertura: **“Se uma musica nao e popular, como encontramos outra que tenha a mesma vibe?”**
- `81.341` musicas unicas apos limpeza e deduplicacao.
- `114` generos no dataset bruto.
- Frase de apoio: **Popularidade responde “o que fez sucesso”; similaridade sonora responde “o que combina comigo”.**

**Visual recomendado:** Tela escura com um mapa abstrato de pontos/faixas conectadas por proximidade sonora, usando uma faixa destacada no centro. Ao lado, os dois numeros grandes. Nao usar um grafico como se fosse resultado medido: e uma composicao conceitual.

**Mensagem principal:** O desafio nao e apenas encontrar hits; e transformar um catalogo enorme em descoberta relevante.

**Fala sugerida:** “Comecamos com uma pergunta simples: se eu gosto de uma musica, como encontro outra que combine comigo sem depender de ela ja ser famosa? Nosso projeto investiga justamente essa diferenca entre sucesso e semelhanca sonora.”

**Tempo estimado:** 35 segundos.

## Slide 2 — A popularidade sozinha nao explica a experiencia musical

**Objetivo do slide:** Mostrar a evidencia que muda o problema de previsao de popularidade para descoberta por similaridade.

**Conteudo:**

- `danceability x popularity`: correlacao **0,096**.
- `tempo x popularity`: correlacao **0,0**.
- `instrumentalness x popularity`: **-0,188**, a maior correlacao absoluta testada, ainda fraca.
- Popularidade media: explicitas **39,4**; nao explicitas **34,9**.
- Faixas populares: duracao media de **3,47 min**, contra **3,86 min** no restante.

**Visual recomendado:** Grafico de barras horizontal com as tres correlacoes, destacando que todas sao fracas; um callout separado para 39,4 versus 34,9. Evitar sugerir causalidade.

**Mensagem principal:** Atributos sonoros isolados nao sao uma explicacao confiavel para popularidade.

**Fala sugerida:** “A primeira hipotese era procurar o que torna uma faixa popular. Os dados foram claros: danceability praticamente nao se relaciona com popularidade, tempo nao se relaciona, e ate a maior correlacao em modulo e fraca. Isso nos levou a nao vender um preditor de sucesso e a focar em uma pergunta mais acionavel: quais faixas soam parecidas?”

**Tempo estimado:** 45 segundos.

## Slide 3 — O som tem estrutura: energia, acustica e valencia se movem juntas

**Objetivo do slide:** Apresentar os principais padroes de audio que sustentam a construcao de perfis.

**Conteudo:**

- `energy x loudness`: **0,761**.
- `acousticness x energy`: **-0,731**.
- `acousticness x loudness`: **-0,582**.
- `valence x danceability`: **0,492**.
- Interpretacao: faixas mais acusticas tendem a ser menos energeticas; faixas mais positivas tendem a ser mais dancantes.

**Visual recomendado:** Matriz simplificada de quatro relacoes ou um diagrama de eixos “calma/acustica” e “energetica/dancante”, com os valores de correlacao como etiquetas. O grafico deve deixar claro que correlacao nao implica causalidade.

**Mensagem principal:** Os atributos formam combinacoes interpretaveis, nao uma lista solta de colunas.

**Fala sugerida:** “A analise deixou de ser apenas descritiva quando vimos as relacoes entre as variaveis. Energy e loudness caminham juntos; acousticness aponta na direcao oposta da energia; valence e danceability tem uma relacao moderada. Essas estruturas permitem descrever uma musica por perfil e comparar faixas de forma mais rica.”

**Tempo estimado:** 50 segundos.

## Slide 4 — A oportunidade esta entre o genero e a musica individual

**Objetivo do slide:** Conectar os insights a uma oportunidade de produto.

**Conteudo:**

- Generos possuem assinaturas sonoras distintas:
  - `classical`: acousticness **0,91** e energy **0,20**;
  - `hip-hop`: danceability **0,72** entre os generos de referencia;
  - `rock`: tempo medio **123 BPM** entre os generos de referencia.
- Extremos do dataset:
  - maior valence: `salsa` (**0,81**);
  - maior acousticness: `classical` (**0,91**);
  - maior speechiness: `comedy` (**0,76**);
  - maior BPM medio: `drum-and-bass` (**155**).
- Oportunidade: recomendar por caracteristicas, atravessando fronteiras de genero.

**Visual recomendado:** Quatro cards de generos com mini barras ou um radar simples por genero. Ao centro, uma seta “de tags de genero para perfil sonoro”.

**Mensagem principal:** Genero ajuda a nomear uma musica; o perfil sonoro ajuda a encontrar a proxima.

**Fala sugerida:** “Tambem vimos que generos se diferenciam em dimensoes concretas. Isso abre uma oportunidade: uma recomendacao nao precisa ficar presa a ‘mais do mesmo genero’. Ela pode buscar a mesma combinacao de energia, valencia, acustica e ritmo, mesmo quando o genero muda.”

**Tempo estimado:** 40 segundos.

## Slide 5 — Transformamos a vibe em uma experiencia de descoberta

**Objetivo do slide:** Apresentar a solucao de forma simples e demonstravel.

**Conteudo:**

- **Entrada:** uma musica ou um grupo de musicas.
- **Representacao:** 14 atributos de audio normalizados por z-score; `popularity` fica fora da similaridade.
- **Saida:** 5 faixas mais semelhantes; para grupos, o sistema calcula um centroide medio.
- **Produto:**
  - perfis musicais em tercis: baixo, medio e alto;
  - playlists RELAX, TREINO, ROMANCE e POPULAR;
  - recomendacao por faixa e por grupo;
  - aplicacao web com busca, player e fila.

**Visual recomendado:** Mockup/screenshot da interface existente em `web/src/App.jsx`, com tres passos visuais: buscar → analisar → ouvir. Se a captura ainda nao existir, usar `[INSERIR SCREENSHOT DA APLICACAO]`.

**Mensagem principal:** A solucao transforma atributos acusticos em uma jornada concreta de descoberta.

**Fala sugerida:** “A entrega combina analise e uso. Uma faixa vira um vetor acustico; o sistema procura vizinhas nesse espaco e devolve cinco recomendacoes. Para um conjunto de faixas, usamos o centro do gosto representado por elas. Na interface, isso aparece como busca, recomendacao, Super Mix, player e fila.”

**Tempo estimado:** 55 segundos.

## Slide 6 — O diferencial e recomendar pelo som, com contexto e escala

**Objetivo do slide:** Explicar proposta de valor, impacto e limites sem inventar resultados de negocio.

**Conteudo:**

**Valor para o usuario**

- Descoberta alem do ranking de popularidade.
- Playlists orientadas a contexto: relaxar, treinar, romance e popularidade.
- Recomendacao de uma faixa ou de uma playlist inteira.
- Limite de ate dois resultados por artista para reduzir concentracao.

**Capacidade tecnica documentada**

- PostgreSQL + pgvector.
- API FastAPI.
- Frontend React + Vite + TailwindCSS.
- Dataset adicional declarado de aproximadamente **740 mil** faixas e catalogo final declarado com **mais de 820 mil** musicas.

**Metricas que devem ser acompanhadas, ainda sem resultado registrado**

- taxa de cliques em recomendacoes;
- play-through e tempo de escuta;
- diversidade por artista/genero;
- avaliacao subjetiva de relevancia;
- latencia de busca e recomendacao;
- taxa de sucesso do cold start.

Use a legenda: **“Hipoteses de impacto; ainda nao sao resultados medidos.”**

**Visual recomendado:** Dois blocos “valor” e “como escala”, com um funil curto da busca ate o play. Nao apresentar `820 mil` como contagem auditada se ela nao tiver sido recalculada; rotular como “declarado na documentacao”.

**Mensagem principal:** O projeto propoe uma camada de descoberta acustica utilizavel, mas a qualidade de produto ainda precisa ser medida com usuarios.

**Fala sugerida:** “O valor nao e prometer que a faixa mais popular sera sempre a melhor. E dar ao usuario uma rota de descoberta baseada no som, com contextos e diversidade. A arquitetura sustenta escala, mas ainda nao temos experimento de usuario ou KPI de recomendacao; esses sao os proximos criterios de validacao.”

**Tempo estimado:** 55 segundos.

## Transicao entre as partes

> **“A solucao parece simples na tela, mas cada parte dela nasceu de uma decisao orientada pelos dados. Agora vamos voltar ao inicio para mostrar como investigamos, o que descartamos e por que o produto terminou com exatamente essas escolhas.”**

---

# PARTE 2 — PROCESSO, RACIOCINIO E TOMADA DE DECISAO — 5 MINUTOS

## Slide 7 — Comecamos antes do recomendador: primeiro entendemos o dado

**Objetivo do slide:** Contextualizar o desafio inicial, os dados e as perguntas do grupo.

**Conteudo:**

- Desafio inicial: explorar um dataset de faixas do Spotify e decidir que produto ou analise fazia sentido.
- Dataset bruto: aproximadamente **114 mil linhas**, com **114 generos** e cerca de 1.000 faixas por genero.
- Limpeza: correcao de mojibake, remocao de faixas sem nome/artista e deduplicacao por `track_name + artists`, preservando a versao mais popular.
- Resultado usado na EDA: **81.341 musicas unicas**.
- Perguntas iniciais:
  - O que se relaciona com popularidade?
  - Como os generos diferem?
  - E possivel formar perfis?
  - A similaridade acustica gera recomendacoes plausiveis?

**Visual recomendado:** “Bruto → limpeza → perguntas” em tres blocos, com o numero 114 mil diminuindo para 81.341. Ao lado, icones de audio, genero e popularidade.

**Mensagem principal:** A qualidade da descoberta dependia primeiro de entender e limpar a unidade correta de analise: a faixa.

**Fala sugerida:** “Nao partimos de um modelo pronto. O primeiro problema era saber o que cada linha representava e evitar que relancamentos ou tags repetidas distorcessem a analise. A limpeza reduziu o conjunto para 81.341 musicas unicas e criou uma base mais coerente para comparar faixas.”

**Tempo estimado:** 45 segundos.

## Slide 8 — O caminho foi desafio → evidencia → decisao → produto

**Objetivo do slide:** Mostrar visualmente o fluxo de raciocinio pedido no challenge.

**Conteudo:**

```text
Desafio
   ↓
Tratamento e exploracao dos dados
   ↓
Perguntas sobre popularidade, genero e som
   ↓
Correlacoes, medias por genero e verificacao de sobreposicoes
   ↓
Hipoteses validadas e descartadas
   ↓
Perfis musicais por tercis
   ↓
Playlists por contexto
   ↓
Similaridade por cosseno
   ↓
API + banco vetorial + interface web
   ↓
Solucao final e metricas a validar
```

**Visual recomendado:** Fluxograma horizontal ou vertical com cinco cores por etapa: investigar, medir, decidir, construir, validar. Destacar as setas de retorno quando uma regra precisou ser ajustada.

**Mensagem principal:** A solucao final foi uma consequencia do processo, nao uma escolha arbitraria.

**Fala sugerida:** “A cada etapa, a pergunta conduzia a proxima. A EDA revelou os padroes; os padroes definiram os perfis; os perfis viraram playlists; e a representacao numerica permitiu recomendacao. Quando uma regra nao cabia nos dados, voltamos uma etapa e ajustamos.”

**Tempo estimado:** 45 segundos.

## Slide 9 — Cada analise respondeu uma pergunta e mudou o proximo passo

**Objetivo do slide:** Demonstrar capacidade analitica sem transformar o slide em inventario tecnico.

**Conteudo:**

| Pergunta | Evidencia encontrada | Decisao influenciada |
| --- | --- | --- |
| O audio explica popularidade? | Correlacoes abaixo de 0,2 em modulo; danceability = 0,096 | Nao priorizar ML preditivo de popularidade |
| Quais dimensoes se movem juntas? | energy/loudness = 0,761; acousticness/energy = -0,731 | Criar perfis e evitar combinacoes inviaveis |
| Genero basta para diferenciar faixas? | Grandes diferencas em valence, acousticness, speechiness e BPM | Recomendar por caracteristicas, nao apenas por genero |
| As tags sao caixas exclusivas? | Sobreposicoes: songwriter/singer-songwriter = 788; dub/dubstep = 678 | Nao consolidar tags na EDA; tratar genero como nuvem de sinais |

**Visual recomendado:** Quatro linhas grandes com a estrutura “queriamos saber → descobrimos → fizemos”. A tabela pode ser usada apenas como guia de producao; no slide, reduzir texto.

**Mensagem principal:** O valor da analise esta nas decisoes que ela tornou possiveis.

**Fala sugerida:** “Analisamos popularidade porque queriamos saber se era uma boa funcao objetivo; a resposta foi nao. Medimos correlacoes porque queriamos construir perfis coerentes; isso revelou quais combinacoes eram raras. Investigamos tags porque queriamos saber se genero era uma categoria limpa; descobrimos que nao era, entao mantivemos a leitura exploratoria sem fingir exclusividade.”

**Tempo estimado:** 60 segundos.

## Slide 10 — Quando os dados contrariaram a ideia inicial, mudamos a regra

**Objetivo do slide:** Mostrar pensamento critico e a evolucao da solucao.

**Conteudo:**

**Caso principal: playlist ROMANCE**

```text
Duvida: como selecionar uma playlist romantica?
        ↓
Ideia inicial: energy baixo + loudness alto
        ↓
Evidencia: energy e loudness tem correlacao 0,761
        ↓
Resultado: apenas 5 musicas candidatas
        ↓
Decisao: remover loudness alto e manter tempo, energy,
         valence baixos; speechiness alto; instrumentalness baixa
```

**Outras decisoes relevantes**

- Popularidade ficou fora do vetor de similaridade: sucesso nao e o mesmo que som.
- Tercis foram usados para tornar “baixo/medio/alto” relativo a distribuicao do dataset.
- ML de previsao, clustering e mapa musical ficaram como extensoes de baixa prioridade.
- `key` e tratada numericamente, uma simplificacao reconhecida no codigo.

**Visual recomendado:** Antes/depois da regra ROMANCE, com uma linha de candidatas “5” e a nova regra. Usar um selo “ajuste guiado por evidencia”.

**Mensagem principal:** O produto melhorou porque a equipe aceitou revisar uma regra plausivel, mas incompatível com a distribuicao observada.

**Fala sugerida:** “Esse foi o melhor teste de pensamento critico. A regra parecia intuitiva, mas a correlacao entre energy e loudness tornava energy baixo com loudness alto quase inexistente. Em vez de forcar a base a obedecer a ideia, ajustamos o criterio e registramos o motivo.”

**Tempo estimado:** 60 segundos.

## Slide 11 — O produto final conecta insight, decisao e funcionalidade

**Objetivo do slide:** Explicitar a rastreabilidade entre a EDA e a implementacao.

**Conteudo:**

| Insight | Decisao | Funcionalidade |
| --- | --- | --- |
| Audio isolado explica pouco a popularidade | Nao otimizar recomendacao por popularity | Similaridade sobre atributos de audio |
| energy/loudness/acousticness tem relacoes fortes | Evitar filtros acusticos contraditorios | Perfis e criterios de playlist baseados em tercis |
| Generos tem perfis distintos, mas tags se sobrepoem | Usar genero como contexto, nao como unica distancia | Recomendacao pode atravessar generos |
| Um grupo de faixas representa um gosto | Calcular media multidimensional | Super Mix por centroide |
| Catalogo maior aumenta descoberta, mas traz faixas sem genero | Enriquecer sob demanda | Lazy load via iTunes e cold start |
| Recomendacoes podem concentrar no mesmo artista | Limitar a dois resultados por artista | Diversidade no resultado |

**Arquitetura a exibir:** `React/Vite → FastAPI → PostgreSQL + pgvector`, com `Librosa/yt-dlp` no fluxo de cold start.

**Visual recomendado:** Diagrama de duas camadas: “evidencia → decisao” em cima e “componente da solucao” embaixo. Incluir screenshot da interface ao lado, se disponivel: `[INSERIR SCREENSHOT DO FLUXO DE BUSCA E RECOMENDACAO]`.

**Mensagem principal:** Cada funcionalidade importante tem uma justificativa analitica ou de experiencia.

**Fala sugerida:** “Aqui esta a ponte entre analise e produto. A exclusao de popularidade vem do resultado da EDA; o centroide vem da ideia de representar um grupo; o limite por artista responde ao risco de uma recomendacao pouco diversa. A arquitetura torna essas decisoes executaveis em uma interface.”

**Tempo estimado:** 50 segundos.

## Slide 12 — O aprendizado foi transformar incerteza em decisoes verificaveis

**Objetivo do slide:** Fechar o processo, reconhecer limites e apresentar o time.

**Conteudo:**

**Aprendizados**

- Limpar e definir a unidade de analise muda a confiabilidade dos insights.
- Correlacao serve para orientar decisoes, nao para provar causalidade.
- Uma boa recomendacao pode priorizar semelhanca sonora em vez de popularidade.
- Hipoteses precisam ser testadas contra a distribuicao real, como no caso da ROMANCE.
- A proxima etapa de rigor e medir relevancia com usuarios e dados de uso.

**Contribuicoes documentadas**

- **Victor:** coordenacao e analise.
- **Milena:** documentacao e analise.
- **Marlon e Ian:** analise critica do tratamento de dados.
- Entregas individuais adicionais e quem apresentara cada slide: **[INFORMACAO A SER PREENCHIDA]**.
- Trabalho colaborativo: definicao do escopo, discussao das hipoteses, revisao dos criterios e consolidacao da solucao: **[CONFIRMAR PELO GRUPO]**.

**Fechamento visual:** Uma linha que reconecta `dados → insights → decisoes → experiencia`, com a frase final em destaque.

**Mensagem principal:** O projeto demonstra nao apenas uma solucao, mas um caminho justificavel para chegar ate ela.

**Fala sugerida:** “Nosso principal aprendizado foi que produto e analise avancam juntos: os dados limitaram o que fazia sentido, as decisoes transformaram os insights em regras e a aplicacao tornou essas regras experimentaveis. Ainda precisamos medir a relevancia com usuarios, mas sabemos explicar por que a solucao tem esse desenho.”

**Tempo estimado:** 55 segundos.

---

# Materiais visuais a preparar

O repositorio contem CSVs de perfis, playlists e recomendacoes, alem da implementacao da interface, mas nao contem graficos exportados. Para finalizar o deck:

1. Recriar um grafico de barras das correlacoes de Slide 2 a partir dos numeros em `src/01_analise_exploratoria/analise.md`.
2. Recriar uma matriz/diagrama de correlacoes do Slide 3.
3. Criar cards comparativos de generos para o Slide 4.
4. Capturar a interface rodando para os Slides 5 e 11: `[INSERIR SCREENSHOT]`.
5. Usar uma amostra dos CSVs processados como evidencia visual, sem apresentar a amostra como avaliacao estatistica.
6. Confirmar com o time a divisao de apresentacao e as entregas individuais.

Nao ha, nos arquivos analisados, metricas de precision/recall, avaliacao humana, CTR, retencao, latencia ou experimento A/B. Esses numeros nao devem ser improvisados no pitch.

---

# Entregas e evidencias do projeto

- EDA e resumo dos resultados: [src/01_analise_exploratoria/analise.md](src/01_analise_exploratoria/analise.md)
- Scripts da EDA: `src/01_analise_exploratoria/insights_popularity.py`, `insights_genero.py`, `insights_sentimento.py`
- Limpeza e deduplicacao: [src/shared/dados.py](src/shared/dados.py)
- Perfis musicais: [src/02_perfis_musicais/perfis.py](src/02_perfis_musicais/perfis.py) e `data/processed/perfis_musicais.csv`
- Playlists: [src/03_playlists/playlists.py](src/03_playlists/playlists.py), `data/processed/playlists/` e [docs/perfil_musical.md](docs/perfil_musical.md)
- Recomendacao: [src/04_recomendacao/recomendacao.py](src/04_recomendacao/recomendacao.py) e `data/processed/recomendacoes/`
- Sobreposicao de generos: [docs/analise_sobreposicao_generos.md](docs/analise_sobreposicao_generos.md)
- Arquitetura da aplicacao: [api/main.py](api/main.py), [api/init_db.py](api/init_db.py), [api/ingest_1m.py](api/ingest_1m.py), [web/src/App.jsx](web/src/App.jsx), [docker-compose.yml](docker-compose.yml)
- Decisoes e jornada: [docs/README.md](docs/README.md), [docs/atas/ata-01.md](docs/atas/ata-01.md), [docs/atas/ata-02.md](docs/atas/ata-02.md), [docs/atas/ata-03.md](docs/atas/ata-03.md)

---

# Respostas rapidas para a banca

## 1. Por que nao usar popularidade para recomendar?

**Resposta sugerida:** Porque a EDA nao encontrou evidencia forte de que os atributos sonoros isolados expliquem popularity: danceability teve correlacao 0,096, tempo 0,0 e instrumentalness -0,188. Popularidade tambem se mostrou muito ligada aos artistas das faixas mais populares. Por isso, o projeto separa duas tarefas: popularidade pode compor uma playlist POPULAR, mas a recomendacao acustica exclui essa variavel para buscar semelhanca de som.

**Cuidado:** isso nao prova que popularidade seja inutil; mostra apenas que ela nao e uma boa distancia sonora para o objetivo definido.

## 2. Como voces sabem que as recomendacoes sao boas?

**Resposta sugerida:** Temos outputs de similaridade, incluindo uma recomendacao com score 0,9505 e outras com 0,9360 e 0,9303, mas ainda nao temos avaliacao humana ou metrica formal de relevancia. Portanto, hoje podemos demonstrar coerencia matematica do ranking, nao afirmar qualidade percebida. O proximo passo e um protocolo com usuarios, avaliando relevancia, diversidade e taxa de play.

**Cuidado:** score de cosseno nao deve ser apresentado como “acuracia”.

## 3. O que muda quando entram musicas fora do dataset original?

**Resposta sugerida:** O fluxo de cold start usa busca no YouTube Music, download e extracao de atributos com Librosa, aplica um ajuste de domain shift calibrado com amostras de 15 musicas e insere a nova faixa no banco. Isso amplia a cobertura, mas e uma aproximacao dos atributos proprietarios do Spotify e ainda precisa de validacao sistematica. Generos ausentes entram como `desconhecido` e podem ser enriquecidos sob demanda via iTunes.

**Cuidado:** o volume final do banco e os tempos de ingestao estao declarados na documentacao, mas nao foram auditados neste material; usar `[INFORMACAO A SER PREENCHIDA]` caso a banca exija contagem confirmada.

---

# Frases obrigatorias

**Abertura do pitch:**

> “Se eu gosto de uma musica, como encontro outra com a mesma vibe sem depender de ela ja ser popular?”

**Transicao:**

> “A solucao parece simples na tela, mas cada parte dela nasceu de uma decisao orientada pelos dados. Agora vamos mostrar como investigamos e por que chegamos a esse produto.”

**Frase final:**

> “Transformamos atributos de audio em decisoes de produto para que descobrir musica parecida seja possivel mesmo quando ela ainda nao e popular.”

---

# Tres insights para enfatizar

1. **Popularidade e semelhanca sonora sao problemas diferentes:** danceability x popularity = 0,096; tempo x popularity = 0,0; instrumentalness x popularity = -0,188.
2. **O espaco sonoro tem estrutura:** energy x loudness = 0,761, acousticness x energy = -0,731 e valence x danceability = 0,492.
3. **A analise mudou o produto:** a regra inicial da playlist ROMANCE gerava apenas 5 candidatas por combinar energy baixo e loudness alto; a equipe ajustou o criterio com base na evidencia.

---

# Divisao sugerida de apresentacao

A documentacao registra Victor, Milena, Marlon e Ian, mas nao registra qual pessoa deve apresentar cada slide. A divisao abaixo e uma sugestao operacional e precisa ser confirmada pelo grupo:

- **Victor:** Slides 1–2 e 7–8 — abertura, problema, escopo e fluxo de investigacao.
- **Milena:** Slides 3–4 e 9 — insights, generos, analises e narrativa dos achados.
- **Marlon:** Slides 5–6 e 10 — solucao, proposta de valor e decisao da playlist ROMANCE.
- **Ian:** Slides 11–12 — arquitetura, rastreabilidade, aprendizados e encerramento.
- **Todos:** demonstracao da aplicacao e respostas da banca.

Antes da apresentacao, substituir a sugestao pelas entregas reais de cada integrante:

- Victor: `[CONFIRMAR ENTREGAS E SLIDES]`
- Milena: `[CONFIRMAR ENTREGAS E SLIDES]`
- Marlon: `[CONFIRMAR ENTREGAS E SLIDES]`
- Ian: `[CONFIRMAR ENTREGAS E SLIDES]`

---

# Checklist de preparacao

- [ ] Confirmar nomes, entregas e ordem de fala de cada integrante.
- [ ] Executar a aplicacao e capturar a busca, recomendacao, Super Mix e player.
- [ ] Recriar os graficos sem inventar pontos individuais nao presentes nos arquivos.
- [ ] Confirmar se o catalogo final ultrapassou 820 mil musicas e registrar a contagem auditada.
- [ ] Definir uma avaliacao futura de relevancia com usuarios.
- [ ] Ensaiar para manter a Parte 1 em 5 minutos e a Parte 2 em 5 minutos.
- [ ] Preparar uma demonstracao de contingencia com os CSVs caso a API nao esteja disponivel.
