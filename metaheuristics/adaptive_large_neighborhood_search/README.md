# Adaptive Large Neighbourhood Search (ALNS)

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 7.

A **Adaptive Large Neighbourhood Search (ALNS)**, ou **Busca Adaptativa em Vizinhança Grande**, foi proposta por **Stefan Røpke e David Pisinger (DTU, 2006)**. É uma busca local em que cada passo **remove** uma parte grande da solução e depois a **reinsere**. Vários operadores de remoção e de inserção competem na mesma busca: os que trazem bons resultados ganham chance de ser sorteados de novo. Normalmente roda dentro de um esquema de Simulated Annealing.

Esta implementação segue os slides do Tema 7 (Profª Laura Bahiense) e o artigo *A Unified Heuristic for a Large Class of Vehicle Routing Problems with Backhauls*. Os operadores para a mochila são **escolhas desta implementação**: o artigo trata de roteamento de veículos.

## 1. Intuição

- **Vizinhança grande.** No SA, um movimento troca um bit, uma mudança pequena. A LNS de Shaw (1998) destrói `q` elementos e reconstrói a solução, alcançando soluções distantes num passo só (é a ideia do *ruin and recreate*). Quanto maior `q`, maior a vizinhança.
- **Vários operadores.** Cada operador tem um papel: a remoção aleatória diversifica; a pior remoção e a de Shaw intensificam. Nenhum é o melhor em todas as instâncias nem em todas as fases da busca.
- **Adaptativa.** Em vez de escolher os operadores à mão, a busca mede o sucesso de cada um e ajusta as chances durante a execução. Essa camada de aprendizado é o "A" da ALNS.

O tamanho da destruição decide o equilíbrio (slide 15). Remover pouco intensifica demais, e a busca não sai da bacia de um ótimo local ruim. Remover muito diversifica demais, perde as partes boas da solução e torna o algoritmo quase aleatório.

## 2. Problema da mochila 0-1

Dados itens com pesos `peso_i`, valores `valor_i` e capacidade `C`:

\[
\max \sum_{i=1}^{n} valor_i x_i
\quad\text{sujeito a}\quad
\sum_{i=1}^{n} peso_i x_i \le C,\quad x_i\in\{0,1\}.
\]

## 3. Componentes

| Componente | O que faz | Nesta implementação |
|---|---|---|
| Solução inicial | ponto de partida | `construtiva` (padrão `binaria.construtiva_aleatoria`) |
| Remoção (desconstrução) | tira `q` elementos da solução | `remocoes`: aleatória, pior e Shaw |
| Inserção (reconstrução) | completa a solução parcial | `insercoes`: aleatória e gulosa; na ordem, também arrependimento |
| Seleção | sorteia uma remoção e uma inserção por roleta | proporcional aos pesos `π` |
| Aceitação | decide se o candidato vira a solução corrente | Metropolis com resfriamento a cada iteração; piora só se a solução for nova |
| Pontuação `p` | mede o sucesso de cada operador dentro de um segmento | `pontuacoes = (σ1, σ2, σ3)` |
| Peso `π` | chance de cada operador ser sorteado | atualizado no fim de cada segmento, com o fator de reação `r` |

### 3.1 Operadores de remoção (slide 13)

Na mochila, remover é tirar itens de dentro. Os três operadores existem nas duas representações e escolhem os mesmos itens: na ordem, a solução é decodificada, a remoção binária correspondente escolhe os itens, e eles saem da ordem.

| Operador | Na mochila | Papel |
|---|---|---|
| `remocao_aleatoria` | sorteia `q` itens de dentro | diversifica: qualquer item pode sair |
| `remocao_pior` | tira os `q` itens de dentro com **menor densidade** valor/peso, os que rendem menos pela capacidade que ocupam | realoca o que mais pesa contra a solução |
| `remocao_shaw` | sorteia um item de dentro e tira os `q − 1` **mais parecidos** com ele, pela distância `\|Δpeso\|/max_peso + \|Δvalor\|/max_valor` | itens parecidos são fáceis de trocar entre si, e a inserção pode explorar essa troca |

A pior remoção é determinística: com o mesmo `q`, tira sempre os mesmos itens. Na versão de Ropke e Pisinger para o problema de coleta e entrega, ela é aleatorizada para não repetir; aqui, quem decide quando ela deixa de ajudar é a roleta.

### 3.2 Operadores de inserção (slide 14)

Inserir é completar a solução parcial **sem desfazer o que já está nela**. As inserções enchem a mochila até não caber mais nada.

| Operador | Binária | Ordem |
|---|---|---|
| `insercao_aleatoria` | percorre os itens de fora em ordem aleatória e coloca os que cabem | recoloca cada item que falta numa posição sorteada |
| `insercao_gulosa` | a cada passo, coloca o item de fora que cabe e **mais aumenta o valor**, e recalcula o que ainda cabe | a cada passo, testa cada item que falta em cada posição e aplica o par de maior valor |
| `insercao_arrependimento` | — | a cada passo, coloca primeiro o item que mais perde se não for para a melhor posição: arrependimento = valor na melhor posição − valor na segunda melhor |

A gulosa binária escolhe pelo **ganho na função objetivo**, como no slide, e não pela densidade da [construtiva gulosa](../guloso/mochila/README.md). Exemplo dos testes, com `C = 9` e o item de peso 4 já dentro: pela densidade entrariam os itens de 3/8 e 2/2 (valor final 22); pelo ganho, entra o de 5/11, que enche a mochila (valor final 23).

#### Por que o arrependimento só existe na ordem

O arrependimento compara a **melhor posição** de um elemento com a **segunda melhor**. No exemplo da aula, um problema de roteamento de veículos, cada rota é uma sequência de clientes: o cliente removido pode entrar em várias posições e várias rotas, e vale inserir primeiro o que perde mais se ficar para depois. Essa é uma representação **por ordem**.

Na representação binária, um item de fora só tem um jeito de entrar: virar 1. Não existe segunda posição, então não há arrependimento a medir. Na representação por ordem há posições, e o operador existe. Mas muitas posições decodificam para o mesmo valor (redundância da ordem), então o arrependimento costuma ser 0. Nesse caso, o desempate é pelo maior valor, e o operador age como a gulosa. Exemplo dos testes: na ordem `[2]` com `C = 5`, o item 0 vale 10 antes do 2 e 3 depois (arrependimento 7), enquanto o item 1 vale 12 nas duas posições (arrependimento 0). A gulosa coloca primeiro o 1; o arrependimento, primeiro o 0.

### 3.3 Seleção por roleta (slides 17 e 18)

Cada operador é uma fatia da roleta, de tamanho proporcional ao seu peso:

\[
prob(i) = \frac{\pi_i}{\sum_{k=1}^{N} \pi_k}.
\]

Remoções e inserções têm roletas separadas. Com pesos 2, 2 e 3 nas remoções, as chances são 28,57%, 28,57% e 42,86%. Todos os pesos começam em 1, ou seja, no primeiro segmento as chances são iguais.

### 3.4 Pontuações (slide 19)

No início de cada segmento as pontuações `p` são zeradas. Em cada iteração, a remoção e a inserção usadas recebem a **mesma** pontuação, porque não dá para saber qual das duas foi responsável pelo resultado (slide 20):

| Situação | Pontuação |
|---|---|
| o candidato é o novo melhor global | `σ1` |
| o candidato é novo e melhor que a solução corrente | `σ2` |
| o candidato é novo, não é melhor e foi aceito pelo SA | `σ3` |
| outros casos | 0 |

O slide pede `σ1 > σ2 > σ3`, e o padrão aqui é `(33, 13, 9)`. O artigo da ALNS para o problema de coleta e entrega com janelas de tempo (Ropke e Pisinger, 2006, *Transportation Science*) usa `(33, 9, 13)`, com `σ3 > σ2`: premia mais quem aceita uma piora nova, ou seja, quem diversifica. Para testar, passe `pontuacoes=(33, 9, 13)`.

### 3.5 Pesos (slide 20)

No fim de cada segmento, o peso de cada operador `i` vira

\[
\pi_{i,j+1} = (1 - r)\,\pi_{i,j} + r\,\frac{p_i}{\theta_i},
\]

em que `p_i` é a pontuação do operador no segmento `j` e `θ_i` é quantas vezes ele foi usado. O **fator de reação** `r` controla a memória:

- `r = 0`: os pesos nunca mudam;
- `r = 1`: os pesos passam a ser só a pontuação média do último segmento.

Um operador que não foi usado no segmento (`θ_i = 0`) mantém o peso.

### 3.6 Segmentos × iterações

A busca é dividida em **segmentos** (o laço externo), cada um com `tamanho_segmento` **iterações** (o laço interno). A **pontuação** é atualizada a cada iteração e mede o desempenho dentro do segmento. O **peso** é atualizado a cada segmento e acumula o desempenho ao longo de toda a busca.

### 3.7 Aceitação

A aceitação é a do SA, com uma diferença do slide 16: uma piora (ou empate) só é aceita se a solução **ainda não tiver sido encontrada**. Assim a busca não gasta iterações voltando a soluções já vistas. Um candidato que melhora é sempre aceito. A temperatura cai depois de **cada** iteração, como no artigo, então a agenda `temperaturas(T0, Tf, α)` define o número de iterações.

"Já encontrada" quer dizer gerada antes como candidata, comparando a solução inteira. Na representação por ordem, duas ordens diferentes que decodificam para os mesmos itens contam como soluções diferentes: a redundância da ordem também aparece aqui.

## 4. Pseudocódigo

Para maximização (o slide está escrito para minimização):

```text
s  <- construtiva()
s* <- s
π  <- 1 para cada operador; p <- 0; θ <- 0
encontradas <- {s}

para cada temperatura T da agenda (T <- α·T a cada iteração):
    R <- roleta(remoções, π);  I <- roleta(inserções, π)
    q <- sorteio em [1, round(grau_remocao · n)]
    s' <- I(R(s, q))
    Δ  <- f(s') - f(s)
    nova <- s' não está em encontradas;  encontradas <- encontradas ∪ {s'}

    se Δ > 0:                                   # melhora: sempre aceita
        s <- s'
        se f(s) > f(s*):  s* <- s;  σ <- σ1
        senão se nova:    σ <- σ2
    senão se nova e aleatório(0, 1) < exp(Δ / T):  # piora ou empate, se nova
        s <- s';  σ <- σ3

    p[R] += σ;  p[I] += σ;  θ[R] += 1;  θ[I] += 1
    a cada tamanho_segmento iterações:
        π_i <- (1 - r)·π_i + r·p_i/θ_i   (só para θ_i > 0)
        p <- 0;  θ <- 0

retornar s*
```

## 5. Parâmetros

| Parâmetro | Papel | Padrão | Fonte |
|---|---|---|---|
| `temperatura_inicial`, `temperatura_minima`, `fator_resfriamento` | agenda do SA; uma iteração por temperatura | obrigatórios | slides 12 e 16 |
| `remocoes` | lista de operadores de remoção | aleatória, pior e Shaw (binária) | slide 13 |
| `insercoes` | lista de operadores de inserção | aleatória e gulosa (binária) | slide 14 |
| `grau_remocao` | `q` é sorteado em `[1, round(grau_remocao · n)]` | 0,2 | slide 15; com cerca de metade dos itens dentro, equivale aos "até 40%" do artigo |
| `tamanho_segmento` | iterações por segmento | 100 | artigo da ALNS para o PDPTW |
| `fator_reacao` | `r` da atualização dos pesos | 0,1 | artigo da ALNS para o PDPTW |
| `pontuacoes` | `(σ1, σ2, σ3)` | (33, 13, 9) | ordem do slide 19; o artigo usa (33, 9, 13) |
| `avaliar`, `construtiva`, `busca_local`, `aceitacao`, `debug` | as mesmas peças dos outros esquemas | binárias; sem busca local; Metropolis | [`utils/`](../utils/README.md) |

O número de iterações é o tamanho da agenda: com `T0 = 100`, `Tf = 1` e `α = 0,99`, são 459 iterações. No artigo, `T0` é calculado a partir da primeira solução (parâmetro `w`), o que fica fora desta implementação. Escolha `T0` na escala das diferenças de valor da instância.

## 6. Peças trocáveis

Todos os componentes são parâmetros, com as peças de [`utils/`](../utils/README.md) como padrão. A remoção tem o **mesmo encaixe da perturbação e do movimento**, `(solucao, itens, capacidade, k, debug)`, então eles também entram na lista de remoções:

```python
adaptive_large_neighborhood_search_mochila(
    itens,
    capacidade,
    100,
    1,
    0.99,
    remocoes=(binaria.remocao_shaw, binaria.perturbar),
)
```

Para trocar de representação, troque o prefixo de todas as peças:

```python
adaptive_large_neighborhood_search_mochila(
    itens,
    capacidade,
    100,
    1,
    0.99,
    remocoes=(ordem.remocao_aleatoria, ordem.remocao_pior, ordem.remocao_shaw),
    insercoes=(
        ordem.insercao_aleatoria,
        ordem.insercao_gulosa,
        ordem.insercao_arrependimento,
    ),
    avaliar=ordem.avaliar,
    construtiva=ordem.construtiva_aleatoria,
)
```

**Custo da inserção por ordem:** a gulosa e o arrependimento decodificam cada item que falta em cada posição, `O(q² n²)` por iteração. Medido no pior `q`: 0,3 ms com 20 itens, 7 ms com 50 e 100 ms com 100. Com milhares de iterações, prefira até cerca de 50 itens.

## 7. Histórico

`adaptive_large_neighborhood_search_mochila` devolve `(melhor_solucao, historico)`, no formato comum a todos os esquemas, indexado de 0 ao número de iterações:

- `valor_candidato`, `valor_atual`, `melhor_valor` e `avaliacoes`, como nos outros esquemas (cada candidato conta 1 avaliação, mais as da busca local, se houver);
- `temperatura`: a temperatura da iteração (a partir da iteração 1);
- `peso <operador>`: o peso de cada operador ao fim da iteração, com o nome da função (por exemplo, `peso remocao_shaw`); na iteração 0, os pesos iniciais.

O `plotar_historico` desenha os pesos no painel de baixo, uma linha por operador, com a temperatura no eixo da direita. No `Depurador`, cada iteração gera as figuras da remoção e da inserção sorteadas; uma piora rejeitada por já ter sido encontrada aparece com a nota "já encontrada".

## 8. Exemplo

```python
import random

from metaheuristics.adaptive_large_neighborhood_search import (
    adaptive_large_neighborhood_search_mochila,
)
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

random.seed(0)
itens = gerar_instancia_aleatoria(20, 20, 100)
capacidade = sum(item.peso for item in itens) // 2
otimo, _ = programacao_dinamica(itens, capacidade)
melhor, historico = adaptive_large_neighborhood_search_mochila(
    itens, capacidade, 100, 1, 0.99
)
melhor_valor = historico["melhor_valor"][max(historico["melhor_valor"])]
print(f"Ótimo: {otimo} | ALNS: {melhor_valor}")
plotar_historico(historico, otimo, eixo_x="iteracao", save=True)
```

## 9. Executar

Na raiz do repositório:

```bash
pytest tests/adaptive_large_neighborhood_search
```

O teste principal usa a mesma instância de 20 itens e semente 0 do SA, do ILS e do VNS, e exige `gap <= 5%`. Esse limite é um critério do teste, não uma garantia da ALNS. Mude `PLOT = False` para `True` para salvar o gráfico.

## 10. Vantagens e limitações

**Vantagens:** os operadores não precisam ser escolhidos à mão; vizinhanças grandes alcançam soluções distantes; as remoções e inserções costumam ser simples, mesmo em problemas com muitas restrições; a mesma estrutura serve para vários problemas, como mostra o artigo com seis variantes de roteamento.

**Limitações:** há muitos parâmetros (agenda, `σ`, `r`, segmento, grau de remoção); o artigo mostra que a camada de aprendizado nem sempre supera a escolha uniforme; e a qualidade continua dependendo dos operadores disponíveis. A roleta só escolhe entre eles.

## 11. Questões para revisão

1. Como funciona a ALNS em linhas gerais?
2. Para que servem os operadores de remoção e de inserção?
3. Como o grau de remoção equilibra intensificação e diversificação?
4. Como é feita a escolha dos operadores?
5. Qual é a diferença entre segmentos e iterações?
6. Qual é a diferença entre os pesos e as pontuações?
7. Como as pontuações são calculadas em cada iteração? E os pesos, em cada segmento?
8. Por que a inserção por arrependimento não existe na representação binária da mochila?

## 12. Referências

- Bahiense, L. *Metaheurísticas em Otimização Combinatória — Tema 7: Adaptive Large Neighbourhood Search (ALNS)*. Material didático.
- Ropke, S.; Pisinger, D. (2006). *A Unified Heuristic for a Large Class of Vehicle Routing Problems with Backhauls*. **European Journal of Operational Research**, 171, 750–775. DOI: [10.1016/j.ejor.2004.09.004](https://doi.org/10.1016/j.ejor.2004.09.004).
- Ropke, S.; Pisinger, D. (2006). *An Adaptive Large Neighborhood Search Heuristic for the Pickup and Delivery Problem with Time Windows*. **Transportation Science**, 40(4), 455–472. DOI: [10.1287/trsc.1050.0135](https://doi.org/10.1287/trsc.1050.0135).
- Ropke, S.; Pisinger, D. (2007). *A General Heuristic for Vehicle Routing Problems*. **Computers & Operations Research**, 34, 2403–2435. DOI: [10.1016/j.cor.2005.09.012](https://doi.org/10.1016/j.cor.2005.09.012).
- Shaw, P. (1998). *Using Constraint Programming and Local Search Methods to Solve Vehicle Routing Problems*. CP-98.
