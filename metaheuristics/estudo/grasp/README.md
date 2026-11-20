# GRASP + Path-Relinking

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 9.

O **GRASP** (*Greedy Randomized Adaptive Search Procedure*) foi proposto por **Thomas Feo e Mauricio Resende** em 1989, para o problema de cobertura de conjuntos. É uma **busca local multi-start**: cada iteração constrói uma solução de um jeito guloso e aleatório e a melhora com uma busca local, e a melhor solução encontrada é devolvida. O **Path-Relinking (PR)**, proposto por Glover (1996) para a Busca Tabu, acrescenta uma memória: guarda soluções elite e explora os caminhos entre elas.

Esta implementação segue os slides do Tema 9 (Profª Laura Bahiense). As escolhas para a mochila (função gulosa, movimentos do PR) são **desta implementação**.

## 1. Intuição (slides 3 a 5)

Duas formas de começar uma busca local:

| Construção | Qualidade | Variabilidade |
|---|---|---|
| Aleatória | baixa | alta |
| Gulosa | boa | baixa ou nenhuma |

O GRASP combina as duas: a cada passo, sorteia o próximo elemento entre os **melhores** candidatos. As soluções saem boas e diferentes entre si, e cada uma leva a busca local a um ótimo local possivelmente diferente. Como a construção não é necessariamente ótima, a busca local termina o trabalho; e a eficiência dela depende da vizinhança, da estratégia de busca, de uma avaliação rápida e da qualidade da solução construída (slide 5).

## 2. Problema da mochila 0-1

Dados itens com pesos `peso_i`, valores `valor_i` e capacidade `C`:

\[
\max \sum_{i=1}^{n} valor_i x_i
\quad\text{sujeito a}\quad
\sum_{i=1}^{n} peso_i x_i \le C,\quad x_i\in\{0,1\}.
\]

## 3. Fase de construção (slides 6 a 16)

A cada passo:

1. os **candidatos** são os itens fora da mochila que ainda cabem (slide 12);
2. cada candidato recebe o valor da **função gulosa**, aqui a densidade `valor/peso`;
3. a **Lista Restrita de Candidatos (RCL)** fica com os melhores;
4. um item da RCL é **sorteado** e entra na mochila;
5. os candidatos são recalculados: alguns deixam de caber.

### 3.1 Tamanho da RCL (slide 10)

- **Por cardinalidade:** os `p` melhores candidatos.
- **Por qualidade** (a desta implementação): com `c_max` e `c_min` as densidades máxima e mínima entre os candidatos, a RCL tem os itens com

\[
c(e) \ge c_{\max} - \alpha\,(c_{\max} - c_{\min}).
\]

O slide escreve a regra para minimização (`c(e) ≤ c_min + α(c_max − c_min)`); aqui ela está invertida, porque a mochila maximiza. Com **α = 0**, só entram os de densidade máxima: é a construção **gulosa** (a mesma solução da `construtiva_gulosa`). Com **α = 1**, entram todos os que cabem: é uma construção **aleatória**.

### 3.2 Aspectos probabilístico e adaptativo (slides 12 a 16)

O sorteio dentro da RCL é o aspecto **probabilístico**. O recálculo dos candidatos depois de cada escolha é o aspecto **adaptativo**: a função gulosa leva em conta o que já foi construído. No exemplo de cobertura de conjuntos da aula, o custo incremental de um subconjunto é o custo dividido pelo número de elementos **ainda não cobertos** que ele cobre. Primeiro `S1` vale 10/3 ≈ 3,33 e é escolhido; depois `S2` passa de 15/2 a 15/1 = 15 e `S3` de 20/3 a 20/2 = 10, porque parte do que eles cobriam já está coberto. Na mochila, a densidade de cada item não muda, mas o conjunto de candidatos muda: um item que cabia deixa de caber.

### 3.3 Peças

| Peça | Representação | O que devolve |
|---|---|---|
| `binaria.construtiva_gulosa_aleatoria(itens, capacidade, alfa=0.3, vies="aleatoria")` | binária | a solução construída |
| `ordem.construtiva_gulosa_aleatoria(...)` | por ordem | os itens na ordem em que foram escolhidos, seguidos dos outros; decodifica para a mesma solução da binária |

Com a assinatura `(itens, capacidade)`, as duas encaixam também como construtiva dos outros esquemas (com α = 0,3).

## 4. Construção melhorada (slides 17 a 21)

O GRASP original não usa nada do que aprendeu nas iterações anteriores. Os slides apresentam três formas de aprender:

- **GRASP reativo** (Prais e Ribeiro, 2000), **implementado:** α é sorteado a cada iteração de um conjunto `{α₁, …, αₘ}`, com probabilidades que começam iguais e são recalculadas periodicamente a partir da qualidade média das soluções obtidas com cada α. No slide, para minimização, `pᵢ ∝ z*/z̄ᵢ`; aqui, para maximização, `pᵢ ∝ z̄ᵢ/z*`. Os α que dão soluções melhores ganham chance, como os operadores da ALNS. Basta passar uma tupla: `alfa=(0.1, 0.3, 0.5, 0.7, 0.9)`.
- **Bias choice**, **implementado:** em vez de sortear a RCL com probabilidades iguais, favorecer os mais bem classificados. Com `r` a posição na RCL (1 = melhor), o peso é `1` (aleatória), `1/log(r + 1)` (logarítmica), `e^{-r}` (exponencial) ou `r^{-2}` (polinomial de ordem 2); também aceita uma função de `r`. No GRASP, com `functools.partial(binaria.construtiva_gulosa_aleatoria, vies="exponencial")`.
- **Perturbação de custos** (Canuto, Resende e Ribeiro, 2001), **fora:** perturba os custos a cada iteração, com estratégias diversificadora, intensificadora e uniforme. O slide 19 a indica quando a construção é pouco sensível à randomização ou não há algoritmo guloso, o que não é o caso da mochila.

## 5. Fase de busca local (slides 22 e 23)

- **Primeira melhora × melhor melhora:** a primeira melhora costuma ser mais rápida, e a melhor melhora tende a convergir cedo para um ótimo local ruim. O padrão aqui é `binaria.busca_local_primeira_melhora`; qualquer busca local do repositório encaixa.
- **Hashing**, **implementado** (`hashing=True`): se a solução construída já apareceu antes, o ótimo local guardado é reaproveitado, em vez de rodar a busca local de novo. As buscas locais do repositório são determinísticas, então o resultado não muda, só as avaliações. Na instância de referência (20 itens, semente 1), as 50 iterações custam 513 avaliações com hashing e 6.306 sem.
- **Filtering**, **fora:** só aplicar a busca local a construções promissoras.

## 6. Soluções elite e Path-Relinking (slides 24 a 38)

### 6.1 Pool elite (slide 36)

Uma **memória de longo prazo**: as boas soluções guardam variáveis "fortemente determinadas" e "consistentes" (slide 24). O pool `P` (`tamanho_elite`) recebe a solução de cada iteração assim:

- enquanto não está cheio, entra qualquer solução nova;
- depois, entra se **superar a melhor** do pool, ou se **superar a pior e for suficientemente diferente** de todas: `Δ(x, y) ≥ diferenca_minima`, com `Δ` a diferença simétrica, o número de posições em que `x` e `y` diferem (`Δ((1,0,1,1,0), (1,1,0,1,0)) = 2`, slide 36);
- a solução que entra substitui a pior.

### 6.2 Path-Relinking (slides 25 a 33)

Depois da busca local, a solução da iteração (**inicial**) é ligada a uma solução elite sorteada (**guia**). A cada passo, **todos os movimentos que trazem um atributo da guia** são avaliados, e o melhor é aplicado. O caminho termina quando chega à guia, e a melhor solução intermediária substitui a da iteração se for melhor.

| Peça | Movimento | Passos até a guia |
|---|---|---|
| `binaria.passos_para_guia` | inverte um bit em que a solução difere da guia | a distância de Hamming |
| `ordem.passos_para_guia` | troca duas posições para colocar na posição `p` o item que a guia tem ali | o número de posições diferentes |

Os passos podem passar por soluções que não cabem: a avaliação as desfavorece. A lógica do caminho e do pool fica em `utils/reconexao.py` (`reconectar` e `atualizar_elite`), independente da representação e do esquema.

### 6.3 Variantes (slides 37 e 38)

| `direcao` | Parte de | Nos slides |
|---|---|---|
| `"backward"` (padrão) | a **melhor** das duas | "Melhor!": a vizinhança da melhor solução é explorada por completo |
| `"forward"` | a **pior** das duas | — |
| `"backward_forward"` | as duas, alternadamente, cada uma em direção à posição atual da outra, até se encontrarem | "melhor!" |

Com `periodo_reconexao=k`, o PR roda a cada `k` iterações (**relinking periódico**), para economizar tempo. O **bidirecional** (percorrer os dois caminhos inteiros) ficou de fora: segundo o slide 38, dobra o tempo e dá ganhos marginais.

Nos testes, um "pico" no meio do caminho mostra que a direção importa: de (0000) a (1111), a forward passa por (1100) e o encontra, e a backward desce por outro lado e não.

## 7. Pseudocódigo

Para maximização, com o PR ligado (slide 35):

```text
P <- ∅                                          # pool elite
para it = 1, …, max_iteracoes:
    α <- sorteado (se reativo) ou fixo
    s <- construção gulosa aleatória(α)          # valor_candidato
    s <- busca local(s)                          # ou o ótimo guardado (hashing)
    se P ≠ ∅ e it é múltiplo de periodo_reconexao:
        g <- sorteio em P
        s' <- melhor intermediária do caminho entre s e g (direcao)
        se f(s') > f(s):  s <- s'
    oferecer s ao pool P
    se f(s) > f(s*):  s* <- s                    # valor_atual = f(s)
    se reativo e it é múltiplo de periodo_reativo: recalcular as probabilidades de α
retornar s*
```

Com `reconexao=None`, as linhas do PR e do pool somem, e o que sobra é o GRASP básico do slide 4. O slide 4 para depois de `MAX_ITER` iterações **sem melhoria**; aqui, como no slide 35, são `max_iteracoes` iterações no total.

## 8. Parâmetros

| Parâmetro | Papel | Padrão | Fonte |
|---|---|---|---|
| `max_iteracoes` | iterações do GRASP | 50 | slide 35 |
| `alfa` | α da RCL; uma tupla torna o GRASP reativo | 0,3 | slides 10 e 18 |
| `periodo_reativo` | iterações entre recálculos das probabilidades de α | 10 | slide 18 |
| `hashing` | reaproveitar o ótimo local de uma construção repetida | `True` | slide 23 |
| `tamanho_elite` | capacidade do pool | 5 | slide 36 |
| `diferenca_minima` | Δ mínimo para entrar no pool sem superar a melhor | 2 | slide 36 |
| `direcao` | início do PR | `"backward"` | slides 37 e 38 |
| `periodo_reconexao` | o PR roda a cada `k` iterações | 1 | slide 37 |
| `avaliar`, `construtiva`, `busca_local`, `reconexao`, `debug` | as peças; `reconexao=None` é o GRASP puro | binárias; primeira melhora | [`utils/`](../../utils/README.md) |

## 9. O que os experimentos mostram

No notebook do laboratório (50 itens, 10 sementes):

- **Com os padrões**, GRASP + PR e GRASP puro chegam ao ótimo nas 10 sementes da instância correlacionada, com cerca de 700 avaliações até o melhor. A construção por densidade já começa perto do ótimo, e a busca local com trocas termina o trabalho. Na instância de referência (20 itens), a própria gulosa (α = 0) já é ótima.
- **O efeito do PR aparece com α alto**, quando as construções são mais aleatórias. Com α = 0,9 na instância correlacionada, as duas versões chegam ao ótimo, mas o GRASP + PR precisa de 1.946 avaliações até o melhor, contra 2.999 do GRASP puro. É o análogo, em avaliações, das curvas de "tempo até o alvo" dos slides 39 a 41.
- Na instância comum, com α = 0,6, o GRASP + PR chega ao ótimo em 8 de 10 sementes (gap médio 0,02%), e o puro, em 7 (0,05%).

Os ganhos são pequenos porque a mochila é fácil para o GRASP: com frequência, todas as iterações chegam ao mesmo ótimo local, e então o pool tem uma solução só e o PR não tem caminho a percorrer.

## 10. Histórico

`grasp_mochila` devolve `(melhor_solucao, historico)`, no formato comum a todos os esquemas, com as iterações a partir de 1 (o GRASP não tem uma solução inicial à parte):

- `valor_candidato`: a solução **construída**;
- `valor_atual`: a solução depois da busca local e do PR; a distância entre as duas linhas no gráfico mostra o trabalho da busca local;
- `melhor_valor`: o valor de `s*`;
- `avaliacoes`: a construída e a final contam 1 cada, mais as vizinhas da busca local e os passos do PR (com as duas pontas);
- `alfa`: o α da iteração, que o `plotar_historico` mostra no painel de baixo.

No `Depurador`, cada iteração gera as figuras de cada passada da busca local e de cada passo do PR (com a direção no título), e a da iteração, com as notas "hashing: busca local reaproveitada" e "PR melhorou: a → b" quando for o caso.

## 11. Exemplo

```python
import random

from metaheuristics.estudo.grasp import grasp_mochila
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

random.seed(0)
itens = gerar_instancia_aleatoria(20, 20, 100)
capacidade = sum(item.peso for item in itens) // 2
otimo, _ = programacao_dinamica(itens, capacidade)
random.seed(1)
melhor, historico = grasp_mochila(itens, capacidade)
print(f"Ótimo: {otimo} | GRASP + PR: {historico['melhor_valor'][50]}")
plotar_historico(historico, otimo, eixo_x="iteracao", save=True)
```

## 12. Executar

Na raiz do repositório:

```bash
pytest tests/estudo/grasp
```

O teste da instância de referência usa a mesma instância de 20 itens e semente 0 dos outros esquemas e exige `gap <= 5%`, um critério do teste, não uma garantia do GRASP. Mude `PLOT = False` para `True` para salvar o gráfico.

## 13. Fora desta implementação

- **Perturbação de custos** (slides 19 e 20) e **filtering** (slide 23).
- **GRASP com VNS** (slide 42): a busca local vira um VNS com VND. No repositório, a busca local é uma peça de passada única, então isso exigiria uma peça nova.
- **Relinking bidirecional** (slide 38).

## 14. Questões para revisão

1. Como funciona o GRASP em linhas gerais? Quais são seus elementos e parâmetros?
2. Qual é a função da fase de construção? E da busca local?
3. Como o algoritmo introduz aleatoriedade na construção gulosa?
4. Para que serve e como funciona a Lista Restrita de Candidatos? O que acontece com α = 0 e α = 1?
5. Por que a construção é "adaptativa"?
6. Como funciona o GRASP reativo? Quando vale a pena perturbar os custos originais?
7. Qual é a motivação para guardar soluções elite? O que é e como funciona o path-relinking?
8. É melhor aplicar o path-relinking a cada iteração ou só no fim, como pós-otimização? Quais são os prós e os contras?

## 15. Referências

- Bahiense, L. *Metaheurísticas em Otimização Combinatória — Tema 9: GRASP + PR*. Material didático.
- Feo, T. A.; Resende, M. G. C. (1989). *A probabilistic heuristic for a computationally difficult set covering problem*. **Operations Research Letters**, 8, 67–71.
- Festa, P.; Resende, M. G. C. (2001). *GRASP: An Annotated Bibliography*. AT&T Labs Research Technical Report.
- Resende, M. G. C.; Ribeiro, C. C. (2002). *Greedy Randomized Adaptive Search Procedures*. In: Glover, F.; Kochenberger, G. (eds.), **State of the Art Handbook in Metaheuristics**. Kluwer.
- Resende, M. G. C. (2007). *An introduction to GRASP*. XXXIX Simpósio Brasileiro de Pesquisa Operacional.
- Prais, M.; Ribeiro, C. C. (2000). *Reactive GRASP: An application to a matrix decomposition problem in TDMA traffic assignment*. **INFORMS Journal on Computing**, 12, 164–176.
- Feo, T. A.; Resende, M. G. C.; Smith, S. H. (1994). *A greedy randomized adaptive search procedure for maximum independent set*. **Operations Research**, 42, 860–878.
- Canuto, S. A.; Resende, M. G. C.; Ribeiro, C. C. (2001). *Local search with perturbations for the prize-collecting Steiner tree problem in graphs*. **Networks**, 38(1), 50–58.
- Glover, F. (1996). *Tabu search and adaptive memory programming — advances, applications and challenges*. In: **Interfaces in Computer Science and Operations Research**. Kluwer.
