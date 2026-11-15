# PRD — ALNS no laboratório de metaheurísticas (Mochila 0-1)

## Contexto

A aula do Tema 7 apresenta a **Adaptive Large Neighbourhood Search (ALNS)**, de Ropke e Pisinger (2006). Em cada iteração, um operador de **remoção** destrói parte da solução e um operador de **inserção** a reconstrói. Os dois são sorteados por roleta, com pesos que se adaptam ao desempenho de cada operador, e a aceitação segue o Simulated Annealing.

O repositório já separa SA, ILS e VNS em peças trocáveis (`metaheuristics/utils/`), com histórico, gráficos e depurador comuns. Esta entrega coloca a ALNS no mesmo padrão. O PRD anterior, do laboratório de peças trocáveis, está no histórico do git, e as decisões dele continuam valendo, registradas em [`utils/README.md`](metaheuristics/utils/README.md).

## Objetivo

Implementar a ALNS como mais um esqueleto que recebe peças, com operadores de remoção e de inserção nas duas representações (binária e por ordem), e mostrar a adaptação dos pesos no histórico e no gráfico comum. As misturas continuam a cargo de quem faz o exercício, no notebook do laboratório.

## Decisões

| Tema | Decisão |
|---|---|
| Problema | Mochila 0-1, a mesma de SA, ILS e VNS |
| Representações | binária (padrão) **e** por ordem. A ordem é mais lenta, mas fica para estudo, com o custo documentado |
| Remoções (nas duas) | `remocao_aleatoria`; `remocao_pior` (tira os itens de dentro com menor densidade valor/peso); `remocao_shaw` (sorteia um item de dentro e tira os mais parecidos com ele, por \|Δpeso\|/max_peso + \|Δvalor\|/max_valor) |
| Inserções | binária: `insercao_aleatoria` e `insercao_gulosa` (a cada passo, entra o item de fora que cabe e mais aumenta o valor). Ordem: as mesmas e `insercao_arrependimento` |
| Arrependimento | **só na ordem**: ele compara a melhor posição de um item com a segunda melhor, e só a ordem tem posições. Na binária, um item de fora só tem um jeito de entrar. O exemplo da aula (roteamento de veículos) é uma representação por ordem, em que cada rota é uma sequência. A binária fica completa com 5 operadores (3 remoções e 2 inserções) |
| Encaixes novos | remoção `(solucao, itens, capacidade, k, debug=None) -> solucao`, o mesmo da perturbação, por isso as duas são trocáveis. Inserção `(solucao, itens, capacidade, debug=None) -> solucao`: completa uma solução parcial sem desfazer o que já está nela |
| Laço | o do slide 16: uma iteração por temperatura (`temperaturas(T0, Tf, α)`) e aceitação padrão `metropolis(niveis, 1)`. Um candidato que melhora é sempre aceito; uma piora ou um empate só é aceito se a solução ainda **não tiver sido encontrada** |
| Pontuações σ | padrão **(33, 13, 9)**, na ordem do slide (σ1 > σ2 > σ3). O README cita o (33, 9, 13) do artigo da ALNS para o PDPTW. σ1 vai para um novo melhor global, σ2 para uma melhora nova e σ3 para uma piora nova aceita. A remoção e a inserção da iteração recebem a mesma pontuação (slide 20) |
| Pesos | começam em 1. No fim de cada segmento, `π ← (1 − r)·π + r·p/θ`; um operador que não foi usado (θ = 0) mantém o peso. Padrões do artigo: `tamanho_segmento=100` e `fator_reacao=0.1` |
| Grau de remoção | `grau_remocao=0.2`: a cada iteração, q é sorteado em `[1, round(0,2·n)]`. Com cerca de metade dos itens dentro da mochila, isso equivale aos "até 40%" do artigo (slide 15: intensificação × diversificação) |
| "Já encontrada" | conjunto com `tuple(solucao)` de todos os candidatos gerados. Na ordem, ordens diferentes com a mesma decodificação contam como novas (efeito da redundância, explicado no README) |
| Histórico | o formato comum, mais `temperatura` e `peso <nome do operador>` por iteração (os pesos vigentes ao fim da iteração; na iteração 0, os pesos iniciais) |
| Gráfico | o **mesmo painel de extras** do `plotar_historico`: os pesos no eixo da esquerda, uma linha por operador, com legenda, e a temperatura no eixo da direita. Continua um gráfico de 2 painéis; o de SA, ILS e VNS não muda |
| Busca local | parâmetro opcional `busca_local=None`, aplicado depois da inserção, como no SA |
| Reaproveitamento | avaliação, construtivas, aceitação (`temperaturas` + `metropolis`), buscas locais, histórico, gráficos, experimento e depurador. Perturbação e movimento têm o encaixe da remoção e podem entrar na lista de remoções. As remoções por ordem decodificam a solução e chamam a remoção binária correspondente |

### Nomes das peças

| Encaixe | Binária | Ordem |
|---|---|---|
| remoção | `binaria.remocao_aleatoria` | `ordem.remocao_aleatoria` |
| remoção | `binaria.remocao_pior` | `ordem.remocao_pior` |
| remoção | `binaria.remocao_shaw` | `ordem.remocao_shaw` |
| inserção | `binaria.insercao_aleatoria` | `ordem.insercao_aleatoria` |
| inserção | `binaria.insercao_gulosa` | `ordem.insercao_gulosa` |
| inserção | — | `ordem.insercao_arrependimento` |

O esquema se chama `adaptive_large_neighborhood_search_mochila` e fica em `metaheuristics/adaptive_large_neighborhood_search/`.

## Escopo

- Esqueleto da ALNS com README de teoria (slides do Tema 7 e o artigo), pseudocódigo, parâmetros e suas fontes, histórico, exemplo e questões de revisão.
- Peças `remocao.py` e `insercao.py` em `utils/binaria/` e `utils/ordem/`, exportadas pelos `__init__.py`.
- `plotar_historico` com os pesos no painel de extras.
- Testes de cada peça nova, do esqueleto nas duas representações e do gráfico.
- READMEs (raiz, conceitos e `utils/`) e notebook do laboratório atualizados.

## Fora do escopo

- Roteamento de veículos (VRP com backhauls), o problema do artigo.
- Temperatura inicial automática pelo parâmetro `w` do artigo.
- Remoção por cluster e remoções baseadas em histórico (neighbor graph e request graph).
- Arrependimento com mais de 2 posições (regret-k).
- Otimizar o custo da inserção por ordem.

## Critérios de aceite

- A ALNS aceita quaisquer remoções, inserções, construtiva, busca local e aceitação compatíveis passadas por parâmetro, sem editar o esquema.
- Peças existentes com o encaixe da remoção (perturbação e movimento) funcionam como operadores de remoção.
- O histórico da ALNS segue o formato comum, e `plotar_historico` mostra os pesos e a temperatura no mesmo painel. Os gráficos de SA, ILS e VNS não mudam.
- `pytest` passa a partir da raiz, e os testes que já existiam não foram alterados.
- O notebook roda do começo ao fim sem erro.

## Próximos passos

- **Busca Tabu:** esqueleto próprio; precisa de memória (lista tabu) e de uma vizinhança que se possa listar.
- **Algoritmo genético:** esqueleto populacional, com peças novas por representação (cruzamento, mutação, seleção).
- **GRASP:** construtiva gulosa aleatorizada (lista restrita de candidatos) seguida da busca local que já existe.
- **ALNS:** temperatura inicial pelo parâmetro `w` do artigo e remoções baseadas em histórico.
