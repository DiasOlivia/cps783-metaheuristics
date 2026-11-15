# PRD — Busca Tabu no laboratório de metaheurísticas (Mochila 0-1)

## Contexto

A aula do Tema 8 apresenta a **Busca Tabu**, de Glover (1986, 1989). Em cada iteração, a busca vai para a **melhor vizinha admissível**, mesmo que ela piore a solução. Uma memória de curto prazo, a lista tabu, proíbe por |T| iterações os movimentos que desfariam os mais recentes, o que evita a ciclagem. Os critérios de aspiração liberam um movimento tabu quando vale a pena.

O repositório já separa SA, ILS, VNS e ALNS em peças trocáveis (`metaheuristics/utils/`), com histórico, gráficos e depurador comuns. Esta entrega coloca a Busca Tabu no mesmo padrão. O PRD anterior, da ALNS, está no histórico do git, e as decisões dele continuam valendo, registradas em [`utils/README.md`](metaheuristics/utils/README.md) e no [README da ALNS](metaheuristics/adaptive_large_neighborhood_search/README.md).

## Objetivo

Implementar a Busca Tabu como mais um esqueleto que recebe peças, com um encaixe novo de **vizinhança** (a Busca Tabu precisa listar todas as vizinhas) e a **avaliação penalizada** do slide, e reproduzir nos testes o exemplo da mochila da aula.

## Decisões

| Tema | Decisão |
|---|---|
| Esquema | `tabu_search_mochila` em `metaheuristics/tabu_search/`, seguindo o nome em inglês dos outros |
| Algoritmo | o do slide 20: em cada iteração, avalia toda a vizinhança e vai para a melhor vizinha admissível (não tabu ou aspirada), mesmo que piore; atualiza a lista tabu; guarda s*; para quando `Iter − MelhorIter > BTmax` |
| Lista tabu | **vetor de prazo tabu** (slide 29), indexado pelo item: um movimento é tabu se algum item que ele altera tem `prazo[i] ≥ iter`; depois do movimento, `prazo[i] = iter + |T|` |
| Aspiração | **por objetivo**: um movimento tabu é admissível se a vizinha supera s* (`f(s') > f(s*)`, slide 21). **Por default**: se nenhum movimento é admissível, faz o de prazo mais antigo (slides 15 e 29) |
| Desempate | a primeira vizinha na ordem da vizinhança (no slide, o menor índice) |
| Avaliação | **penalizada**, como no slide 23: `f(s) = valor − α·max(0, peso − C)`, com `α = Σ valores`. Peça nova `binaria.avaliar_penalizada`, que qualquer esquema pode usar. Com esse α, uma solução inviável vale no máximo 0, e a melhor solução encontrada é sempre viável |
| Encaixe novo | **vizinhança** `(solucao, itens, capacidade) -> [(rotulo, itens_alterados, vizinha)]`: lista todas as vizinhas, inclusive as inviáveis, com os itens que viram tabu |
| Vizinhanças | `binaria.vizinhanca_flip` (inverte um bit, a do slide; padrão); `binaria.vizinhanca_flip_troca` (acrescenta a troca 1-por-1, a mesma vizinhança das buscas locais binárias); `ordem.vizinhanca_troca` (troca duas posições; o tabu fica nos dois itens trocados) |
| Extensões | **lista tabu dinâmica** (slide 30): `tamanho_tabu=(Tmin, Tmax)` sorteia |T| no início e a cada `τ·Tmax` iterações. **Parada por valor alvo** (slide 19): `valor_alvo=None` por padrão |
| Histórico | o formato comum, mais `tamanho_tabu`. `valor_candidato` e `valor_atual` são o valor da vizinha escolhida, porque a busca sempre se move. Cada vizinha avaliada conta 1 avaliação |
| Depurador | sem mudança: cada iteração gera um passo "vizinhança" com todas as vizinhas, as tabu rotuladas com "(tabu)", e a nota "aspiração" ou "todas tabu: a de prazo mais antigo" |
| Representações | binária (padrão) e por ordem. Na ordem, a vizinhança custa O(n³) por iteração, como a busca local por ordem |
| Reaproveitamento | construtivas, `ordem.avaliar`, os movimentos da busca local binária (para a `vizinhanca_flip_troca`), histórico, gráficos, experimento e depurador |

### Nomes das peças

| Encaixe | Binária | Ordem |
|---|---|---|
| avaliar | `binaria.avaliar_penalizada` (nova) | `ordem.avaliar` (a ordem já é sempre viável) |
| vizinhança | `binaria.vizinhanca_flip`, `binaria.vizinhanca_flip_troca` | `ordem.vizinhanca_troca` |

## Escopo

- Esqueleto da Busca Tabu com README de teoria (slides do Tema 8), pseudocódigo, o exemplo do slide passo a passo, parâmetros, histórico e questões de revisão.
- Peças `vizinhanca.py` em `utils/binaria/` e `utils/ordem/` e `binaria.avaliar_penalizada`, exportadas pelos `__init__.py`.
- Testes de cada peça nova e do esquema, incluindo o exemplo do slide.
- READMEs (raiz, conceitos e `utils/`) e notebook do laboratório atualizados.

## Fora do escopo

- Regiões planas (slide 31) e oscilação estratégica (slide 34).
- Intensificação, diversificação e memória de longo prazo (slides 32, 33 e 35).
- Path-relinking (slides 36 a 43), o tema da próxima aula.

## Critérios de aceite

- A Busca Tabu aceita qualquer avaliação, construtiva e vizinhança compatíveis passadas por parâmetro, sem editar o esquema.
- O exemplo do slide é reproduzido: partindo de (01010), com |T| = 1 e BTmax = 1, a busca para na iteração 5 e devolve (00111), de valor 11.
- O histórico segue o formato comum, e `plotar_historico` funciona sem mudanças.
- `pytest` passa a partir da raiz, e os testes que já existiam não foram alterados.
- O notebook roda do começo ao fim sem erro.

## Próximos passos

- **Busca Tabu:** regiões planas, oscilação estratégica (variando α) e memória de longo prazo.
- **Path-relinking:** intensificação entre soluções elite, tema da próxima aula.
- **Algoritmo genético:** esqueleto populacional, com peças novas por representação (cruzamento, mutação, seleção).
- **GRASP:** construtiva gulosa aleatorizada (lista restrita de candidatos) seguida da busca local que já existe.
