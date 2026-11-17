# Algoritmos Genéticos (AG)

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 11.

Os **Algoritmos Genéticos** (*Genetic Algorithms*, GA) imitam a evolução das espécies. Uma **população** de soluções evolui por **gerações**: os indivíduos mais aptos têm mais chance de se reproduzir (**seleção**), os pais combinam os seus genes (**cruzamento**), alguns filhos nascem com pequenas alterações (**mutação**), e os melhores passam intactos para a geração seguinte (**elitismo**).

Esta implementação segue os slides do Tema 11 (Profª Laura Bahiense). O tratamento das soluções que não cabem na mochila (seção 9) é **desta implementação**.

## 1. Inspiração (slides 2 a 6)

- **Linnaeus** classificou os organismos e chamou a atenção para a semelhança entre espécies; **Lamarck** propôs a evolução pelo uso e desuso dos órgãos; **Malthus** mostrou que doenças e falta de alimento limitam o crescimento das populações.
- **Darwin (1858)**, a **seleção natural**: indivíduos com características vantajosas para o ambiente têm mais chance de sobreviver e de se reproduzir, e passam essas características aos descendentes.
- **Mendel (1865)**, as leis da hereditariedade: como os caracteres passam de pais para filhos.
- **Genética populacional (1930-1940):** a variabilidade de uma população que se reproduz sexualmente vem da **mutação** e da **recombinação genética**. De 1950 a 1980 vieram as primeiras simulações computacionais de sistemas genéticos.
- **Holland (1975)**, *Adaptation in Natural and Artificial Systems*, com ênfase em aprendizado de máquina; **Goldberg (1989)**, *Genetic Algorithms in Search, Optimization, and Machine Learning*, com ênfase em otimização.

A definição de **John Koza** (slide 6): o AG é um algoritmo de busca probabilístico que transforma, iterativamente, uma população de objetos (em geral cadeias binárias de tamanho fixo), cada um com uma aptidão, numa nova população de filhos, pelo princípio darwiniano da seleção natural e por operações inspiradas na genética, como o cruzamento e a mutação. Em uma frase: **os indivíduos com maior adaptação têm mais chance de se reproduzir.**

## 2. Problema da mochila 0-1

Dados itens com pesos `peso_i`, valores `valor_i` e capacidade `C`:

\[
\max \sum_{i=1}^{n} valor_i x_i
\quad\text{sujeito a}\quad
\sum_{i=1}^{n} peso_i x_i \le C,\quad x_i\in\{0,1\}.
\]

## 3. Vocabulário (slides 7, 10 e 11)

| Algoritmo genético | Problema matemático | Na mochila |
|---|---|---|
| Indivíduo | solução | uma escolha de itens |
| População | conjunto de soluções | `tamanho_populacao` soluções |
| Cromossomo | codificação de uma solução | o vetor de bits ou a ordem |
| Aptidão (*fitness*) | qualidade da solução | o valor (`avaliar`) |
| Gene | cada elemento da solução | um bit, ou um item da ordem |

O cromossomo é formado por **genes**; os valores possíveis de um gene são os **alelos**, e a posição do gene é o **locus**. A codificação pode ser **binária** (cada bit diz se um elemento pertence à solução), **inteira** (permutações, como no caixeiro viajante) ou **real**. As duas representações do repositório são exatamente os dois exemplos do slide 11: o vetor de bits e a permutação.

## 4. Algoritmo básico (slide 9)

```text
P <- população inicial de p indivíduos
repita (uma geração por volta):
    N <- {}
    cruzamentos, com probabilidade Pcruzamento:
        selecione pares de indivíduos em P
        produza filhos pelo cruzamento do par          -> N
    mutações, com probabilidade Pmutação:
        selecione indivíduo(s) de P
        produza filho(s) de forma assexuada             -> N
    atualize P: mantenha os n_elite melhores de P e
                selecione p − n_elite indivíduos de P ∪ N
até o critério de parada
retorne o indivíduo mais adaptado
```

Aqui, cada geração faz `p // 2` tentativas de cruzamento (cada par gera dois filhos) e `p` tentativas de mutação, cada uma com a sua probabilidade. A mutação, como no slide, é **outra forma de gerar filhos** a partir de `P`, e não um passo aplicado aos filhos do cruzamento. A parada é `max_geracoes`.

## 5. População, elitismo e aptidão (slides 12 a 14)

- **População inicial:** em geral aleatória, com indivíduos o mais distintos possível; conhecimento do problema também pode entrar (aqui, `construtiva`).
- **Tamanho:** pequena demais cobre pouco do espaço de busca e converge cedo para ótimos locais ruins; grande demais evita isso, mas custa muito tempo.
- **Elitismo:** os `n_elite` melhores passam sempre para a geração seguinte, para compartilhar as suas boas características. "É essencial para o bom funcionamento do algoritmo."
- **Aptidão:** quantifica o quão bom é um indivíduo em relação aos outros. Pode ser a própria função objetivo ou um mapeamento dela que não distorça a qualidade relativa. Precisa ser rápida, porque cada geração avalia muitos indivíduos.

## 6. Seleção (slides 15 a 21)

A seleção aparece em dois lugares: na escolha dos **pais** (slide 21) e na **atualização da população**, que escolhe `p − n_elite` indivíduos de `P ∪ N` (slides 15 a 20). Os mesmos métodos servem para os dois, e o esquema recebe um para cada (`selecao_pais` e `selecao_sobreviventes`).

**Pressão seletiva** (slide 15) é o quão "ganancioso" é o método. Ela se mede pelo **tempo de dominância** (*takeover*): quantas gerações a melhor solução inicial leva para tomar a população inteira só pela seleção. Pressão forte perde diversidade rápido; pressão fraca explora mais, mas converge devagar. Para não convergir cedo para ótimos locais ruins, é preciso manter a diversidade.

| Método | Como escolhe | Papel no slide | Peça |
|---|---|---|---|
| **Roleta** | chance proporcional à aptidão; gira a roleta uma vez por escolha, com repetição | "seleção natural", o mais tradicional; pode encher a população de cópias de um bom indivíduo | `selecao_roleta` |
| **Ranking** | chance proporcional à posição no ranking (o pior pesa 1, o melhor pesa `n`) | ajuste da pressão: grandes diferenças de aptidão ficam em perspectiva, e só a ordem importa | `selecao_ranking` |
| **Torneio** | `q` indivíduos sorteados com reposição; vence o mais apto | diversificação ajustável: `q` grande, pressão forte; `q = 2`, torneio binário | `selecao_torneio` (`q=2`) |
| **Classes** | os `b%` melhores, os `w%` piores, e o resto sorteado | balanço entre intensificação e diversificação | `selecao_classes` (`melhores=0.2`, `piores=0.2`) |

O exemplo do slide 17: aptidões 150, 50, 200 e 100 dão à roleta as chances 30%, 10%, 40% e 20%. A roleta usa `max(0, valor)`: com a avaliação penalizada, um indivíduo que não cabe vale no máximo 0 e não ganha fatia. Nas classes, as frações são da quantidade escolhida; na escolha de um par de pais, `20%` de 2 arredonda para 0, e as classes viram sorteio puro (o slide 21 lembra que a seleção aleatória existe, "mas não é muito utilizada"). Para mudar `q` ou as frações, use `functools.partial(selecao_torneio, q=4)`.

## 7. Cruzamento (slides 22 a 32)

Os **operadores genéticos** (cruzamento e mutação) transformam a população: diversificam e, ao mesmo tempo, mantêm a adaptação herdada. O **cruzamento** é o mais importante: aproveita o conhecimento dos pontos já visitados, recombinando as características dos pais. Com `Pcruzamento` alta demais, a população é quase toda trocada e indivíduos bons se perdem; com ela baixa demais, o algoritmo fica lento.

### Representação binária

| Operador | Como funciona | Exemplo do slide | Peça |
|---|---|---|---|
| Um ponto | o começo de um pai até o corte, o fim do outro | slide 25: `110101 × 100100`, corte 2 → `110100` e `100101` | `binaria.cruzamento_um_ponto(corte=)` |
| Multiponto | troca, alternadamente, os trechos entre os cortes | slide 26: `011101 × 100010`, cortes 1, 2, 4 → `001110` e `110001` | `binaria.cruzamento_multiponto(cortes=2)` |
| Máscara (uniforme) | onde a máscara tem 1, os genes dos pais são trocados; onde tem 0, mantidos | slide 28: máscara `10010110` | `binaria.cruzamento_uniforme(mascara=)` |

Os três são máscaras: um corte vira a máscara `0…01…1`, e vários cortes, uma máscara alternada. Sem `corte`, `cortes` ou `mascara`, eles são sorteados (a máscara do uniforme tem cada bit 1 com chance 1/2).

### Representação por permutação

Os cruzamentos binários quebram uma permutação: `123|45 × 543|21` gera `12321`, com itens repetidos (slide 29). Os operadores de permutação copiam um trecho de um pai e completam com os genes que faltam, na ordem em que aparecem no outro:

| Operador | Como funciona | Exemplo (pai 1 = `1234567890`, pai 2 = `9378265140`) | Peça |
|---|---|---|---|
| **OPX** (*order-preserving one-point*) | mantém o começo do pai 1 até o corte; o resto vem do pai 2, na ordem | slide 29, corte 5 → `12345 97860` | `ordem.cruzamento_opx(corte=)` |
| **LOX** (*linear-order*) | mantém o trecho do pai 1 entre dois cortes; preenche as outras posições, da esquerda para a direita, com o pai 2 | slide 30, cortes (3, 7) → `938 4567 210` | `ordem.cruzamento_lox(cortes=)` |
| **PMX** (*partially-mapped*) | mantém o trecho do pai 1; as outras posições vêm do pai 2, e um gene repetido segue o mapa entre os trechos até achar um livre | slide 31, cortes (3, 7) → `932 4567 180` | `ordem.cruzamento_pmx(cortes=)` |

No PMX do slide 31, o `7` do pai 2 já está no trecho copiado: o mapa leva `7 → 5 → 2`, e entra o `2`; o `4` vira `8`. Os cortes `(i, j)` delimitam o trecho `[i, j)`, contado a partir de 0. Cada operador devolve dois filhos: o que mantém o trecho do pai 1 e o que mantém o do pai 2 (o slide 32 mostra os dois filhos do PMX).

## 8. Mutação (slides 33 a 36)

A mutação introduz e mantém a diversidade: altera genes ao acaso, para que nenhum ponto do espaço de busca tenha probabilidade nula, e ajuda a escapar de ótimos locais. É aplicada com probabilidade baixa (≤ 5%); com `Pmutação` alta, a busca vira aleatória.

A mutação tem o mesmo encaixe do **movimento** dos outros esquemas, `(solucao, itens, capacidade, k, debug)`, então as peças de movimento já servem, com `k = intensidade_mutacao`:

| Representação | Mutação do slide | Peça |
|---|---|---|
| Binária | um ponto / múltiplos pontos: inverte bits (slide 34) | `binaria.gerar_vizinho` (`k` bits, só acrescenta um item se ele couber); padrão |
| Permutação | **troca**: dois genes trocam de posição (slide 35) | `ordem.gerar_vizinho` |
| Permutação | **inserção**: o segundo gene sorteado vai para logo depois do primeiro (slide 35) | `ordem.mutacao_insercao` |
| Permutação | **inversão**: inverte o trecho entre dois pontos (slide 36) | `ordem.mutacao_inversao` |
| Permutação | **perturbação**: embaralha o trecho entre dois pontos (slide 36) | `ordem.perturbar` (embaralha `k` posições soltas, não um trecho contíguo) |

## 9. Adaptação para a mochila: o reparo

O cruzamento binário não olha a capacidade: na instância correlacionada de 50 itens, **metade dos filhos** do cruzamento uniforme não cabe na mochila. O padrão aqui é o **reparo guloso** de Chu e Beasley (1998), `binaria.reparar`, aplicado a todo indivíduo novo:

1. enquanto não couber, tira o item de **pior** densidade (valor/peso);
2. depois, tenta os itens de fora, do de **melhor** densidade para o de pior, e coloca cada um que ainda cabe.

O passo 2 completa a mochila, então o reparo é também uma melhoria gulosa, e não só uma volta à viabilidade. Com ele, todo indivíduo cabe, e a avaliação padrão é a `binaria.avaliar`. Sem ele (`reparo=None`), use a `binaria.avaliar_penalizada` da Busca Tabu, que dá no máximo 0 a quem não cabe.

Na **ordem**, `reparo=None`: o decodificador já coloca só o que cabe, então todo filho é viável. Ao trocar de representação, troque o prefixo das peças e passe `reparo=None`.

**A elite sai de `P`**, como no slide 9: um filho melhor que todos só fica se for sorteado entre os sobreviventes. O esquema guarda à parte o melhor indivíduo avaliado, então ele não se perde do resultado, mas pode sair da população (no histórico, `valor_atual` fica abaixo de `melhor_valor`). Tirar a elite de `P ∪ N` não deu ganho consistente nas instâncias de 50 itens.

## 10. Parâmetros

| Parâmetro | Papel | Padrão | Fonte |
|---|---|---|---|
| `tamanho_populacao` | `p` | 50 | slide 12 |
| `max_geracoes` | critério de parada | 100 | slide 9 |
| `prob_cruzamento` | chance de cada uma das `p // 2` tentativas de cruzamento | 0,8 | slide 23 |
| `prob_mutacao` | chance de cada uma das `p` tentativas de mutação | 0,05 | "≤ 5%", slides 34 a 36 |
| `intensidade_mutacao` | o `k` da mutação | 1 | slide 34 |
| `tamanho_elite` | `n_elite` | 2 | slide 13 |
| `selecao_pais`, `selecao_sobreviventes` | métodos de seleção | `selecao_roleta` | slides 15 a 21 |
| `avaliar`, `construtiva`, `cruzamento`, `mutacao`, `reparo` | as peças | binárias: `avaliar`, `construtiva_aleatoria`, `cruzamento_uniforme`, `gerar_vizinho`, `reparar` | [`utils/`](../utils/README.md) |
| `busca_local` | aplicada a cada indivíduo novo, depois do reparo (AG "memético") | `None` | — |
| `debug` | depurador visual | `None` | — |

## 11. Histórico

`genetic_algorithm_mochila` devolve `(melhor_solucao, historico)`, no formato comum a todos os esquemas, com a geração 0 sendo a população inicial:

- `valor_candidato`: a **média da população** na geração;
- `valor_atual`: o **melhor indivíduo da população**; com elitismo, nunca diminui;
- `melhor_valor`: o melhor indivíduo avaliado até a geração, inclusive filhos que não sobreviveram;
- `avaliacoes`: uma por indivíduo novo, mais as da busca local (o reparo não conta);
- `distintos`: quantos indivíduos diferentes há na população, que o `plotar_historico` mostra no painel de baixo. É a **diversidade** dos slides 12 e 15: quando cai para 1, a população convergiu.

No `Depurador`, cada geração gera a figura **população**, com todos os indivíduos no plano peso × valor em relação ao melhor do começo da geração, e a da geração. Nas gerações desenhadas, cada mutação também gera a sua figura.

## 12. O que os experimentos mostram

Instância correlacionada de 50 itens da linha de base do notebook e a comum de mesmo tamanho, 10 sementes, com os padrões (população 50, 100 gerações, cerca de 4.300 avaliações):

| Combinação | Correlacionada | Comum | Distintos no fim (corr.) |
|---|---|---|---|
| Padrão (uniforme, roleta, reparo) | 0,00% (10/10) | 0,00% (10/10) | 4,4 |
| Sem reparo, avaliação penalizada | 2,17% (0/10) | 4,44% (0/10) | 6,7 |
| Sem cruzamento (Pc = 0, Pm = 0,8) | 0,00% (10/10) | 0,77% (0/10) | 4,9 |
| Torneio nas duas seleções | 0,00% (10/10) | 0,02% (6/10) | 1,6 |
| Torneio nos pais, classes nos sobreviventes | 0,00% (10/10) | 0,03% (5/10) | 9,8 |
| Ordem: LOX | 0,71% (2/10) | 2,27% (0/10) | 31,4 |
| Ordem: PMX | 1,07% (0/10) | 3,60% (0/10) | 16,2 |
| Ordem: OPX | 1,78% (0/10) | 7,30% (0/10) | 26,0 |
| Ordem: LOX sem elite | 1,52% (0/10) | 6,25% (0/10) | 33,8 |
| Padrão + busca local em cada filho | 0,00% (10/10) | 0,00% (10/10) | 5,0 |

- **O tratamento da inviabilidade pesa mais que os operadores.** Sem reparo, metade dos filhos é descartada pela seleção, e o AG fica entre 2% e 4,5%. Com o reparo, os três cruzamentos binários chegam ao ótimo; na correlacionada, até a mutação sozinha chega, porque o passo 2 do reparo enche a mochila.
- **O cruzamento faz diferença na comum:** sem ele, o gap vai a 0,77%, e o melhor demora mais a aparecer (834 avaliações até o melhor na correlacionada, contra 263).
- **Pressão seletiva (slide 15):** o torneio colapsa a população em 1 ou 2 indivíduos distintos e chega ao ótimo em menos sementes na comum; a roleta mantém mais diversidade porque, na mochila, os valores da população são parecidos e as fatias quase iguais; as classes, com os piores sempre presentes, são as que mais diversificam.
- **Ordem:** todo filho é viável, mas a mesma solução tem muitas ordens, e a população continua cheia de indivíduos "distintos" que decodificam parecido. O LOX, que copia um trecho e preserva a ordem relativa do resto, é o melhor dos três. Na ordem, **sem elite** o gap dobra na correlacionada e quase triplica na comum, como avisa o slide 13.
- **Busca local em cada filho:** de 600 a 700 vezes mais avaliações (2,6 a 3 milhões), sem ganho aqui, porque o padrão já chega ao ótimo.

Na instância de referência (20 itens, semente 0), o padrão chega ao ótimo nas 10 sementes.

## 13. Exemplo

```python
import random

from metaheuristics.genetic_algorithm import genetic_algorithm_mochila
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

random.seed(0)
itens = gerar_instancia_aleatoria(20, 20, 100)
capacidade = sum(item.peso for item in itens) // 2
otimo, _ = programacao_dinamica(itens, capacidade)
random.seed(1)
melhor, historico = genetic_algorithm_mochila(itens, capacidade)
print(f"Ótimo: {otimo} | AG: {historico['melhor_valor'][100]}")
plotar_historico(historico, otimo, eixo_x="iteracao", save=True)
```

Para a representação por ordem, troque as peças e desligue o reparo:

```python
genetic_algorithm_mochila(
    itens,
    capacidade,
    avaliar=ordem.avaliar,
    construtiva=ordem.construtiva_aleatoria,
    cruzamento=ordem.cruzamento_lox,
    mutacao=ordem.mutacao_inversao,
    reparo=None,
)
```

E os exemplos dos slides, com os cortes fixos:

```python
binaria.cruzamento_um_ponto([1, 1, 0, 1, 0, 1], [1, 0, 0, 1, 0, 0], [], 0, corte=2)
# ([1, 1, 0, 1, 0, 0], [1, 0, 0, 1, 0, 1])
pai1, pai2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [9, 3, 7, 8, 2, 6, 5, 1, 4, 0]
ordem.cruzamento_pmx(pai1, pai2, [], 0, cortes=(3, 7))[0]
# [9, 3, 2, 4, 5, 6, 7, 1, 8, 0]
```

## 14. Executar

Na raiz do repositório:

```bash
pytest tests/genetic_algorithm
```

O teste da instância de referência usa a mesma instância de 20 itens e semente 0 dos outros esquemas e exige `gap <= 1%`, um critério do teste, não uma garantia do AG. Mude `PLOT = False` para `True` para salvar o gráfico. Os testes das peças (`tests/utils/`) reproduzem os exemplos dos slides 17, 25, 26, 28, 29, 30, 31 e 32.

## 15. Questões para revisão (slide 37)

1. Como funciona o método em linhas gerais? Quais são seus elementos e parâmetros característicos?
2. O que ocorre quando a população é pequena? E quando é grande?
3. Quais características da população são mantidas ao longo do algoritmo?
4. Para que serve a função de aptidão?
5. Para que servem os métodos de seleção? Cite e explique dois métodos e as principais diferenças de objetivo entre eles.
6. Em que se baseiam os operadores genéticos? Quais são suas funções no AG?
7. Para que serve o cruzamento? Como funciona? Exemplifique dois tipos.
8. Para que serve a probabilidade de cruzamento? O que ocorre quando é alta? E quando é baixa?
9. Para que serve a mutação? Como funciona? Exemplifique.
10. Para que serve a probabilidade de mutação? O que ocorre quando é alta?
11. Por que o cruzamento binário precisa de reparo na mochila, e por que a representação por ordem não precisa?

## 16. Referências

- Bahiense, L. *Metaheurísticas em Otimização Combinatória — Tema 11: Algoritmos Genéticos (GA)*. Material didático.
- Holland, J. H. (1992). **Adaptation in Natural and Artificial Systems**. 2ª ed. Cambridge, MA: MIT Press (1ª ed. 1975).
- Goldberg, D. E. (1989). **Genetic Algorithms in Search, Optimization, and Machine Learning**. Reading, MA: Addison-Wesley.
- Davis, L. D. (1991). **Handbook of Genetic Algorithms**. New York: Van Nostrand Reinhold.
- Mitchell, M. (1995). *Genetic Algorithms: An Overview*. **Complexity**, 1(1), 31–39.
- Chu, P. C.; Beasley, J. E. (1998). *A genetic algorithm for the multidimensional knapsack problem*. **Journal of Heuristics**, 4, 63–86.
