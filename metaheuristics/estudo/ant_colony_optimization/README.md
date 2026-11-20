# Otimização por Colônia de Formigas (ACO)

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 12.

A **Otimização por Colônia de Formigas** (*Ant Colony Optimization*, ACO) é um método populacional: a cada iteração, várias **formigas** constroem soluções de forma probabilística, guiadas por duas informações, o **feromônio** (a experiência da colônia, que muda ao longo da busca) e a **informação heurística** (o conhecimento do problema). Depois, o feromônio evapora, e as formigas depositam mais feromônio nas soluções melhores. O **Ant System** é de **Marco Dorigo** (1992), e o **Ant Colony System**, de Dorigo e **Luca Maria Gambardella** (1997).

Esta implementação segue os slides do Tema 12 (Profª Laura Bahiense), que aplicam o ACO ao caixeiro viajante. A adaptação para a mochila (seção 6) é **desta implementação**.

## 1. Inspiração biológica (slides 2 a 9)

- Muitas espécies de formigas são quase cegas. Ao caminhar, elas liberam no chão um hormônio, o **feromônio**, que forma uma **trilha**. Diante de um caminho a escolher, uma formiga prefere, com maior probabilidade, o de cheiro mais forte.
- A trilha ajuda a formiga a achar o caminho de volta e as outras a encontrar o alimento. O feromônio **evapora**, o que permite esquecer caminhos e aumenta a diversificação.
- **A ponte binária** (Deneubourg et al., 1990): o formigueiro e a comida são ligados por dois caminhos.
  - **Caminhos de mesmo tamanho:** no início não há feromônio, e as formigas escolhem ao acaso. Por flutuações aleatórias, um dos lados acumula mais feromônio, e a colônia converge para ele.
  - **Caminhos de tamanhos diferentes:** a colônia converge para o mais curto. Ele é percorrido em menos tempo, então mais formigas passam por ele, e mais feromônio é depositado.

## 2. Problema da mochila 0-1

Dados itens com pesos `peso_i`, valores `valor_i` e capacidade `C`:

\[
\max \sum_{i=1}^{n} valor_i x_i
\quad\text{sujeito a}\quad
\sum_{i=1}^{n} peso_i x_i \le C,\quad x_i\in\{0,1\}.
\]

## 3. As formigas artificiais e o Ant System (slides 10 a 30)

As formigas artificiais constroem soluções passo a passo. No Ant System para o caixeiro, cada formiga começa numa cidade e, estando na cidade `i`, vai para a cidade `j` com probabilidade

\[
p^k_{ij} = \frac{\tau_{ij}^{\alpha}\,\eta_{ij}^{\beta}}{\sum_{l \in N^k_i} \tau_{il}^{\alpha}\,\eta_{il}^{\beta}}, \qquad j \in N^k_i,
\]

onde:

- `τ_ij` é o feromônio da aresta `(i, j)`;
- `η_ij = 1/d_ij` é a informação heurística (a "visibilidade" da cidade `j` a partir de `i`);
- `α` e `β` pesam o feromônio e a heurística;
- `N^k_i` são as cidades que a formiga `k` ainda não visitou. A formiga **lembra** por onde passou.

A escolha é uma **roleta**, como no algoritmo genético. No exemplo do slide 19 (5 cidades, `τ = α = β = 1`), a formiga na cidade 1 vai para 2, 3, 4 e 5 com chances de 45%, 21%, 23% e 11%. Depois da primeira iteração, as formigas 1 e 2 já encontram a rota ótima (9,8).

Quando todas terminam, o feromônio é atualizado (slides 24 a 26):

\[
\tau_{ij} \leftarrow (1-\rho)\,\tau_{ij} + \sum_{k=1}^{m} \Delta\tau^k_{ij},
\qquad
\Delta\tau^k_{ij} =
\begin{cases} Q/L_k & \text{se } (i,j) \text{ está na rota da formiga } k\\ 0 & \text{caso contrário}\end{cases}
\]

- A **evaporação** (taxa `0 < ρ ≤ 1`) evita que o feromônio cresça sem limite e permite esquecer decisões ruins: **favorece a diversificação**.
- O **depósito** é maior nas rotas mais curtas (`L_k` menor). No slide 27, com `ρ = 0,5` e `Q = 1`, a aresta (3, 5) recebe o depósito das formigas 1, 2 e 5: `τ₃₅ = 0,5·1 + 1/9,8 + 1/9,8 + 1/12,4 = 0,785`.
- **Parada** (slides 28 e 30): um número máximo de iterações sem melhoria. A **estagnação** acontece quando todas as formigas seguem sempre o mesmo percurso, por excesso de feromônio nas arestas de uma rota subótima.

```text
τ ← τ0 em todos os componentes
repita:
    para cada formiga k:
        construa uma solução S_k pela regra de transição (roleta)
        se S_k é melhor que s*: s* ← S_k
    τ ← (1 − ρ) τ + Σ Δτ^k        (evaporação e depósito)
até que s* fique k_max iterações sem melhorar
retorne s*
```

## 4. Outras formas de atualizar o feromônio (slides 31 e 32)

- **Elitist Ant System** (EAS, Dorigo, 1992): a melhor rota desde o início (*best-so-far*, `T_bs`) deposita mais, com peso `e`: `τ ← (1 − ρ)τ + Σ Δτ^k + e·Δτ^bs`. É o elitismo do AG.
- **Rank-based Ant System** (ASrank, Bullnheimer et al., 1999): só as `w − 1` melhores formigas da iteração depositam, a de posição `r` com peso `w − r`, e o best-so-far com peso `w`.

## 5. Intensificação e diversificação: o Ant Colony System (slides 33 a 35)

- **Regra proporcional pseudoaleatória:** com probabilidade `q0`, a formiga vai para o melhor `τ·η^β` (**intensificação**); senão, usa a roleta do AS (diversificação "tendenciosa").
- **Atualização global:** só o best-so-far deposita, e só nos seus componentes: `τ ← (1 − ρ)τ + ρ·Δτ^bs`. O novo feromônio é uma média ponderada entre o antigo e o depósito.
- **Atualização local:** logo depois de usar um componente, a formiga o puxa de volta para o nível mínimo: `τ ← (1 − ξ)τ + ξ·τ0`. Isso reduz a atratividade do que foi muito visitado e aumenta a diversificação.

**Formigas naturais × artificiais** (slides 36 e 37):

- **Em comum:** as duas são agentes que cooperam por meio do feromônio (com evaporação), procuram o menor caminho e se comportam de forma estocástica e local.
- **Diferenças:** as artificiais se movem em passos discretos, têm memória e depositam de acordo com a qualidade da solução, só depois de chegar ao destino.

**Vantagens e desvantagens** (slide 38):

- **Vantagens:** é naturalmente paralelizável, eficiente em problemas de caminhos e se adapta a mudanças no problema.
- **Desvantagens:** a construção é uma sequência de escolhas aleatórias não independentes, pode demorar a convergir e depende muito dos parâmetros.

## 6. Adaptação para a mochila

A formiga constrói a solução item a item. Entre os itens que **ainda cabem** (a vizinhança viável), escolhe o próximo pela regra do slide 17, com `η_j = valor_j / peso_j` (a densidade, a "atratividade" do item), e para quando nenhum cabe. O que muda entre as representações é **onde fica o feromônio**, isto é, quais são os **componentes** da solução:

| Representação | Componente | Peças | Analogia |
|---|---|---|---|
| Binária | o **item** `j` | `binaria.construtiva_formiga`, `binaria.trilha` (os itens dentro) | "a formiga visitou a cidade" |
| Por ordem | a **transição** `(i, j)`: ir do item `i` para o `j`; o primeiro sai de `None` | `ordem.construtiva_formiga`, `ordem.trilha` (as transições entre os itens que o decodificador coloca) | a aresta `(i, j)` do caixeiro |

Na ordem, a sequência escolhida vem primeiro, e os itens que não couberam vêm depois, por densidade; decodificada, a ordem dá exatamente os itens escolhidos.

**O feromônio** é um dicionário componente → τ (`Feromonio`, em `utils/feromonio.py`). Um componente que nenhuma formiga usou não fica guardado e vale o **fundo**, que é o `τ0` evaporado junto com os outros. Assim, o esquema funciona com qualquer tipo de componente, sem listá-los de antemão.

**O depósito.** O caixeiro minimiza, e o depósito `Q/L_k` é maior para rotas curtas. Na mochila, que maximiza, uma formiga com solução `S_k` deposita `Δτ = valor(S_k) / valor da gulosa` em cada componente de `S_k`. Uma formiga tão boa quanto a gulosa deposita ≈ 1, que é o `τ0` padrão: é a mesma ideia do ACS, que usa a heurística do vizinho mais próximo como régua. Multiplicar `Q` e `τ0` pelo mesmo número não muda nenhuma probabilidade, então só a razão entre eles importa, e o parâmetro é só o `feromonio_inicial`.

**Detalhes desta implementação:**

- A atualização local do ACS é aplicada logo depois de cada formiga construir, nos componentes que ela usou. É o mesmo que aplicá-la "após atravessar a aresta", porque uma formiga não usa o mesmo componente duas vezes.
- Na regra pseudoaleatória, a formiga escolhe o maior `τ·η^β`, sem o `α`, como no slide 33.
- Com `feromonio=None`, a construção usa `τ = 1` em tudo: é um sorteio guloso por densidade, que serve de construtiva para os outros esquemas.

## 7. Parâmetros

| Parâmetro | Papel | Padrão | Fonte |
|---|---|---|---|
| `numero_formigas` | formigas por iteração (`m`) | 20 | slide 12 |
| `max_sem_melhora` | iterações sem melhorar o best-so-far antes de parar (`k_max`) | 100 | slides 28 e 30 |
| `alfa`, `beta` | pesos do feromônio e da heurística | 1 e 1 | slide 19 |
| `evaporacao` | `ρ` | 0,5 | slide 27 |
| `feromonio_inicial` | `τ0` | 1 | slide 30 |
| `deposito` | `'todas'` (AS), `'elitista'` (EAS), `'ranking'` (ASrank) ou `'melhor'` (ACS) | `'todas'` | slides 26, 31, 32 e 34 |
| `peso_elite` | `e` do EAS | 5 | slide 31 |
| `w` | posições do ASrank | 6 | slide 32 |
| `q0` | chance da regra pseudoaleatória escolher o melhor | 0 | slide 33 |
| `atualizacao_local` | `ξ`; 0 desliga | 0 | slide 35 |
| `avaliar`, `construtiva`, `trilha` | as peças | binárias | [`utils/`](../../utils/README.md) |
| `busca_local` | aplicada à solução de cada formiga, antes do depósito | `None` | — |
| `debug` | depurador visual | `None` | — |

O **ACS completo** é `deposito="melhor", q0=0.9, atualizacao_local=0.1, evaporacao=0.1`.

## 8. Histórico

`ant_colony_optimization_mochila` devolve `(melhor_solucao, historico)`. Como no GRASP, não há solução inicial, e o histórico começa na iteração 1:

- `valor_candidato`: a **média das formigas** na iteração;
- `valor_atual`: a **melhor formiga da iteração**;
- `melhor_valor`: o best-so-far;
- `avaliacoes`: uma por formiga, mais as da busca local;
- `distintos`: quantas soluções diferentes as formigas construíram. O valor 1 é a **estagnação** dos slides 28 e 29.

No `Depurador`, cada iteração gera a figura **formigas**, com todas as soluções no plano peso × valor, em relação ao best-so-far do começo da iteração, e a figura da iteração.

## 9. O que os experimentos mostram

Instância correlacionada de 50 itens da linha de base do notebook e a comum de mesmo tamanho, 10 sementes, 20 formigas, parada após 100 iterações sem melhora:

| Combinação | Correlacionada | Comum | Avaliações até o melhor (corr.) |
|---|---|---|---|
| AS, α = β = 1 (padrão) | 0,49% (2/10) | 0,00% (10/10) | 766 |
| AS, β = 2 | 0,00% (10/10) | 0,00% (10/10) | 960 |
| Só a heurística (α = 0, β = 2) | 0,81% (0/10) | 0,01% (8/10) | 1.042 |
| EAS, β = 2 | 0,00% (10/10) | 0,00% (10/10) | 292 |
| ASrank, β = 2 | 0,06% (9/10) | 0,04% (5/10) | 152 |
| ACS, β = 2 | 0,00% (10/10) | 0,00% (10/10) | 22 |
| Ordem (transições), α = β = 1 | 0,52% (2/10) | 0,21% (1/10) | 756 |
| Ordem (transições), β = 2 | 0,13% (8/10) | 0,01% (9/10) | 1.158 |
| AS, β = 2, + busca local em cada formiga | 0,00% (10/10) | 0,00% (10/10) | 542.918 |

- **Os parâmetros importam** (slide 38). Com os valores do exemplo do slide 19, a heurística pesa pouco, e o AS não chega ao ótimo da correlacionada. Com `β = 2`, chega nas 10 sementes.
- **O feromônio aprende.** Sem ele (`α = 0`), cada formiga é só uma construção gulosa aleatória, como no GRASP, e o gap fica em 0,81%. Com o feromônio, a colônia concentra a busca nos itens das boas soluções.
- **Elitismo e estagnação.** Na correlacionada, o EAS acha o melhor cerca de 3 vezes mais rápido que o AS. O ASrank é ainda mais rápido, mas estagna: no fim, as 20 formigas constroem a mesma solução (`distintos = 1`), e na comum ele perde o ótimo em metade das sementes. É a estagnação dos slides 28 e 29.
- **O ACS é o mais rápido** (22 avaliações até o melhor). Com `q0 = 0,9`, a formiga quase sempre segue a escolha gulosa, e o ótimo destas instâncias está a poucos desvios dela.
- **Por item × por transição.** O feromônio na transição, como no caixeiro, aprende mais devagar. Na mochila importa **quais** itens entram, não a ordem em que entram, e o feromônio de um item fica repartido entre as `n` transições que chegam a ele.
- **Busca local:** de 650 a 750 vezes mais avaliações no total, sem ganho aqui.

Na instância de referência (20 itens, semente 0), o padrão chega ao ótimo nas 10 sementes.

## 10. Exemplo

```python
import random

from metaheuristics.estudo.ant_colony_optimization import ant_colony_optimization_mochila
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

random.seed(0)
itens = gerar_instancia_aleatoria(20, 20, 100)
capacidade = sum(item.peso for item in itens) // 2
otimo, _ = programacao_dinamica(itens, capacidade)
random.seed(1)
melhor, historico = ant_colony_optimization_mochila(itens, capacidade)
print(f"Ótimo: {otimo} | ACO: {max(historico['melhor_valor'].values())}")
plotar_historico(historico, otimo, eixo_x="iteracao", save=True)
```

Para a representação por ordem, com feromônio nas transições, troque as peças:

```python
ant_colony_optimization_mochila(
    itens,
    capacidade,
    avaliar=ordem.avaliar,
    construtiva=ordem.construtiva_formiga,
    trilha=ordem.trilha,
)
```

E o Ant Colony System:

```python
ant_colony_optimization_mochila(
    itens,
    capacidade,
    beta=2,
    deposito="melhor",
    q0=0.9,
    atualizacao_local=0.1,
    evaporacao=0.1,
)
```

## 11. Executar

Na raiz do repositório:

```bash
pytest tests/estudo/ant_colony_optimization
```

O teste da instância de referência usa a mesma instância de 20 itens e semente 0 dos outros esquemas e exige `gap <= 1%`, um critério do teste, não uma garantia do ACO. Mude `PLOT = False` para `True` para salvar o gráfico. O teste de `utils/feromonio.py` reproduz o exemplo do slide 27.

## 12. Questões para revisão (slide 39)

1. Como funciona o método em linhas gerais? Quais são seus elementos e parâmetros característicos?
2. Para que serve o feromônio τ? Por que precisa ser evaporado?
3. Como as formigas artificiais constroem as soluções? Baseadas em que informações?
4. Para que serve a informação heurística η?
5. Quando e como é feita a atualização do feromônio? Analise o depósito e a evaporação.
6. Como incorporar elitismo na atualização do feromônio?
7. Cite e exemplifique diferentes formas de prover o balanço entre intensificação e diversificação neste método.
8. Quais são as principais semelhanças e diferenças entre as formigas naturais e as artificiais?
9. Na mochila, por que o feromônio por item funciona melhor que o feromônio por transição?

## 13. Referências

- Bahiense, L. *Metaheurísticas em Otimização Combinatória — Tema 12: Colônia de Formigas (ACO)*. Material didático.
- Dorigo, M. (1992). **Optimization, Learning and Natural Algorithms**. Tese de doutorado, Politecnico di Milano.
- Dorigo, M.; Gambardella, L. M. (1997). *Ant colonies for the traveling salesman problem*. Technical Report TR/IRIDIA/1996-3, IRIDIA, Université Libre de Bruxelles.
- Dorigo, M.; Gambardella, L. M. (1997). *Ant Colony System: A Cooperative Learning Approach to the Traveling Salesman Problem*. **IEEE Transactions on Evolutionary Computation**, 1(1), 53–66.
- Dorigo, M.; Di Caro, G. (1999). *The Ant Colony Optimization Meta-Heuristic*. IRIDIA, Université Libre de Bruxelles.
- Dorigo, M.; Socha, K. (2007). *An Introduction to Ant Colony Optimization*. Em T. F. Gonzalez (ed.), **Approximation Algorithms and Metaheuristics**. CRC Press.
- Dorigo, M.; Stützle, T. (2010). *Ant Colony Optimization: Overview and Recent Advances*. **Handbook of Metaheuristics**, cap. 8.
- Deneubourg, J.-L.; Aron, S.; Goss, S.; Pasteels, J. M. (1990). *The self-organizing exploratory pattern of the Argentine ant*. **Journal of Insect Behavior**, 3(2), 159–168.
- Bullnheimer, B.; Hartl, R. F.; Strauss, C. (1999). *A new rank based version of the Ant System: a computational study*. **Central European Journal of Operations Research**, 7(1), 25–38.
- Leguizamón, G.; Michalewicz, Z. (1999). *A new version of Ant System for subset problems*. **Congress on Evolutionary Computation (CEC 99)**, 2, 1459–1464.
