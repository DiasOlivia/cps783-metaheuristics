# PRD — Colônia de Formigas (ACO) no laboratório de metaheurísticas (Mochila 0-1)

## Contexto

A aula do Tema 12 apresenta a **Otimização por Colônia de Formigas** (*Ant Colony Optimization*, ACO), de Dorigo (Ant System, 1992) e Dorigo e Gambardella (Ant Colony System, 1997). Cada formiga constrói uma solução de forma probabilística, guiada pelo **feromônio**, a experiência coletiva, e pela **informação heurística** do problema. Depois, o feromônio evapora, e as formigas depositam mais nas boas soluções.

Os slides aplicam o ACO ao caixeiro viajante, com feromônio nas arestas. O repositório já separa SA, ILS, VNS, ALNS, Busca Tabu, GRASP, PSO e AG em peças trocáveis (`metaheuristics/utils/`), com histórico, gráficos e depurador comuns. Esta entrega adapta o ACO à mochila e o coloca no mesmo padrão. O PRD anterior, do AG, está no histórico do git, e as decisões dele continuam valendo, registradas em [`utils/README.md`](metaheuristics/utils/README.md) e no [README do AG](metaheuristics/genetic_algorithm/README.md).

## Objetivo

Implementar o ACO como mais um esqueleto que recebe peças, com a regra de transição e as atualizações de feromônio dos slides, um modelo de feromônio próprio de cada representação e as variantes EAS, ASrank e ACS, sem mudar o que já existe.

## Medições que embasaram as decisões

Protótipo na instância correlacionada de 50 itens (a da linha de base do notebook), 10 sementes, 20 formigas:

| Configuração | Gap | Ótimos | Avaliações até o melhor |
|---|---|---|---|
| AS, feromônio por item, β = 2, parada em 100 sem melhora | 0,00% | 10/10 | 948 |
| AS, por item, α = β = 1, parada em 100 | 0,49% | 2/10 | 756 |
| AS, por transição, β = 2 | 0,06% | 9/10 | 1.668 |
| Só a heurística (α = 0, β = 2) | 0,74% | 0/10 | 1.280 |
| EAS (e = 5), β = 2 | 0,00% | 10/10 | 278 |
| ASrank (w = 6), β = 2 | 0,06% | 9/10 | 142 |
| ACS (q0 = 0,9; ξ = 0,1; ρ = 0,1), β = 2 | 0,00% | 10/10 | 6 |

## Decisões

| Tema | Decisão |
|---|---|
| Esquema | `ant_colony_optimization_mochila` em `metaheuristics/ant_colony_optimization/` |
| Construção | cada formiga escolhe, entre os itens que ainda cabem, o próximo com `p ∝ τ^α · η^β` (slide 17), por roleta, e para quando nenhum cabe. `η = valor/peso` (densidade), a "atratividade" do slide 18 |
| Feromônio | um dicionário **componente → τ** (`Feromonio`, em `utils/feromonio.py`). Um componente que nenhuma formiga usou vale o **fundo**: τ0 evaporado junto com os outros. Assim, o esquema não depende do formato da trilha |
| Binária | feromônio **por item**: o componente é o item, e a solução são os itens escolhidos |
| Ordem | feromônio **por transição** `(anterior, j)`, como as arestas do caixeiro; o primeiro item sai de `None`. A ordem é a sequência escolhida, seguida do resto por densidade |
| Depósito | `Δτ = valor(S_k) / valor da gulosa` em cada componente de S_k: o `Q/L_k` do slide 25 para maximização. Uma formiga tão boa quanto a gulosa deposita ≈ 1 = τ0. Só a razão Q/τ0 importa, então não há parâmetro Q |
| Variantes | `deposito='todas'` (Ant System, padrão), `'elitista'` (EAS, `peso_elite` = e), `'ranking'` (ASrank, `w`) e `'melhor'` (ACS: só o best-so-far, `τ = (1 − ρ)τ + ρΔτ^bs`); `q0` (regra pseudoaleatória) e `atualizacao_local` (ξ). O ACS completo é `deposito='melhor', q0=0.9, atualizacao_local=0.1, evaporacao=0.1` |
| Atualização local | `τ = (1 − ξ)τ + ξτ0` nos componentes de cada formiga, logo depois de ela construir. Equivale a aplicar "após atravessar a aresta" (slide 35), porque uma formiga não repete componente |
| Parâmetros | `numero_formigas=20`, `alfa=1`, `beta=1` (slide 19), `evaporacao=0.5` (slide 27), `feromonio_inicial=1`, `max_sem_melhora=100`, `peso_elite=5`, `w=6` |
| Parada | `max_sem_melhora` iterações sem melhorar o best-so-far (slides 12, 28 e 30) |
| Busca local | opcional (`busca_local=None`), na solução de cada formiga antes do depósito |
| Histórico | por iteração, a partir da 1, como no GRASP: `valor_candidato` = média das formigas, `valor_atual` = melhor formiga da iteração, `melhor_valor` = best-so-far, `avaliacoes` (uma por formiga, mais a busca local) e o extra `distintos` (soluções diferentes entre as formigas); 1 é a estagnação dos slides 28 e 29 |
| Depurador | sem mudança: um passo "formigas" por iteração, com todas as soluções no plano peso × valor, e a figura da iteração |
| Reaproveitamento | avaliações, decodificador, construtiva gulosa (referência do depósito), buscas locais, histórico, gráficos, experimento e depurador |

### Nomes das peças

| Encaixe | Raiz de `utils/` | Binária | Ordem |
|---|---|---|---|
| construção da formiga `(itens, capacidade, feromonio=None, alfa=1, beta=1, q0=0) -> solucao` | — | `construtiva_formiga` (τ por item) | `construtiva_formiga` (τ por transição) |
| trilha `(solucao, itens, capacidade) -> [componentes]` | — | `trilha`: os itens dentro | `trilha`: as transições entre os itens colocados |
| feromônio | `Feromonio` (dicionário com fundo e `evaporar`) | — | — |

## Escopo

- Esqueleto do ACO com README de teoria (slides do Tema 12), a adaptação para a mochila, parâmetros, histórico e questões de revisão.
- `Feromonio` e as peças de construção e trilha nas duas representações, exportadas pelos `__init__.py`.
- Testes de cada peça nova (com o exemplo do slide 27) e do esquema.
- READMEs (raiz, conceitos e `utils/`) e notebook do laboratório atualizados.

## Fora do escopo

- MAX-MIN Ant System e outras variantes que não estão nos slides.

## Critérios de aceite

- O ACO aceita qualquer avaliação, construção, trilha e busca local compatíveis passadas por parâmetro, sem editar o esquema.
- A parada acontece `max_sem_melhora` iterações depois da última melhora.
- O histórico segue o formato comum, e `plotar_historico` funciona sem mudanças.
- `pytest` passa a partir da raiz, e os testes que já existiam não foram alterados.
- O notebook roda do começo ao fim sem erro.

## Próximos passos

- **ACO:** MAX-MIN Ant System (limites para o feromônio contra a estagnação).
- **AG:** eliminação de duplicados e probabilidades adaptativas.
- **PSO:** c1 e c2 adaptativos e topologias de vizinhança.
