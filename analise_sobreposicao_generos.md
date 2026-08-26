# Análise de Sobreposição de Gêneros Musicais

Ao agruparmos as músicas que possuem mais de um gênero (retirando as duplicatas de `track_id`), notamos que muitas músicas recebem "combinações" repetidas de gêneros, como `latin, latino, reggae, reggaeton`. 

## Por que isso acontece?
Isso é uma característica da forma como a API do Spotify cataloga e retorna os dados:
1. **Sinônimos e Redundâncias:** O Spotify possui playlists e categorias ("seeds" de busca) com nomes praticamente idênticos. O caso mais claro é `singer-songwriter` e `songwriter`, ou `latin` e `latino`. Uma música classificada em um, frequentemente cai na rede do outro.
2. **Evolução Musical e Gêneros-Pai:** O `reggaeton` tem raízes diretas no `reggae` (especificamente no dancehall reggae) misturado com hip hop e ritmos latinos. Logo, artistas de reggaeton costumam herdar a tag de `reggae` na classificação algorítmica da plataforma.
3. **Múltiplos Públicos:** Músicas de extremo sucesso ("Me Porto Bonito", "La Bachata") são colocadas em milhares de playlists diferentes. Se uma playlist focada em "reggae" adiciona a música, o algoritmo passa a associar fortemente aquela música com a tag.

## Isso acontece em outros gêneros?
Sim, acontece em todo o dataset! Para entender a fundo, rodei um script para analisar a **coocorrência** de gêneros (quantas vezes duas tags aparecem juntas na mesma música). 

Aqui estão as 15 sobreposições mais comuns em todo o dataset:

| Gênero 1 | Gênero 2 | Músicas em Comum |
| :--- | :--- | :--- |
| `singer-songwriter` | `songwriter` | 788 |
| `dub` | `dubstep` | 678 |
| `punk` | `punk-rock` | 551 |
| `indie` | `indie-pop` | 464 |
| `reggae` | `reggaeton` | 432 |
| `alt-rock` | `alternative` | 431 |
| `latino` | `reggaeton` | 428 |
| `edm` | `house` | 398 |
| `latino` | `reggae` | 326 |
| `minimal-techno` | `techno` | 318 |
| `j-pop` | `j-rock` | 312 |
| `brazil` | `gospel` | 311 |
| `electro` | `house` | 271 |
| `chill` | `sad` | 270 |
| `latin` | `latino` | 270 |

> [!NOTE]
> Repare que de 1000 músicas possíveis por gênero, 788 músicas do gênero `songwriter` também são `singer-songwriter`! O mesmo vale para `dub` e `dubstep`.

## Existe tratamento necessário?
Depende do objetivo do seu projeto (Nano Challenge):

* **Para exploração e insights (O que estamos fazendo):** Não é obrigatório tratar. Apenas entender que as tags funcionam mais como "nuvem de palavras" da música do que como caixas exclusivas.
* **Para criação de um Modelo Preditivo (ex: IA para classificar o gênero da música a partir das variáveis de áudio):** É altamente recomendado tratar!
   - Você poderia criar um dicionário de mapeamento para fundir sinônimos (ex: substituir todos os `latino` por `latin`, `punk-rock` por `punk`).
   - Ou criar uma nova coluna de "Gênero Macro" (ex: EDM englobando house, electro, dubstep).
   - Se o modelo tentar diferenciar `latin` de `latino`, ele vai ficar confuso e errar muito, pois as características acústicas de ambos são literalmente as mesmas.

## Como printar o dataframe completo no terminal?
Para ver todas as linhas sem o Pandas resumir com `...`, você pode usar um contexto de configuração do Pandas logo antes do print:
```python
with pd.option_context('display.max_rows', None):
    print(seu_dataframe)
```
