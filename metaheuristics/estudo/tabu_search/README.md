# Busca Tabu (Tabu Search)

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 8.

A **Busca Tabu (BT)** foi proposta por **Fred Glover** (com ideias também de Pierre Hansen) em 1986 e formalizada por Glover em 1989. É uma busca local que **não para no primeiro ótimo local**: a cada iteração ela vai para o **melhor vizinho**, mesmo que ele piore a solução, e usa uma **memória** para não voltar ao que acabou de visitar. Ela responde às duas perguntas do slide 2: o que fazer quando nenhum vizinho melhora, e como evitar voltar a um ótimo local já visitado.

Esta implementação segue os slides do Tema 8 (Profª Laura Bahiense) e reproduz nos testes o exemplo da mochila da aula.

## 1. Intuição (slides 4 a 12)

Considere uma minimização com sete soluções em fila, `s1` a `s7`, cada uma vizinha das adjacentes:

1. **Descida:** partindo de `s1`, a busca desce até `s3` e para ali, o primeiro ótimo local.
2. **Ir para o melhor vizinho, mesmo que piore:** de `s3` a busca vai para `s4`. Só que o melhor vizinho de `s4` é `s3` de novo: a busca **cicla**.
3. **Lista tabu:** voltar a `s3` fica proibido por algumas iterações. A busca é empurrada para `s5` e, com `s4` também proibida, para `s6`, de onde desce até `s7`, o ótimo global.

A lista tabu é uma **memória de curto prazo**: ela não guarda tudo o que foi visitado, só o suficiente para impedir o retorno imediato.

## 2. Problema e função de avaliação

Mochila 0-1: dados itens com pesos `peso_i`, valores `valor_i` e capacidade `C`,

\[
\max \sum_{i=1}^{n} valor_i x_i
\quad\text{sujeito a}\quad
\sum_{i=1}^{n} peso_i x_i \le C,\quad x_i\in\{0,1\}.
\]

Na aula, a BT avalia as soluções com uma **função penalizada** (slides 22 e 23), no estilo de uma função lagrangiana: a restrição de capacidade entra na função objetivo como penalidade.

\[
f(s) = \sum_j valor_j s_j - \alpha \cdot \max\Big\{0,\ \sum_j peso_j s_j - C\Big\},
\qquad \alpha = \sum_j valor_j.
\]

É a peça `binaria.avaliar_penalizada`. Com esse `α` e pesos inteiros, uma solução que passa da capacidade vale no máximo 0, então nunca supera uma solução viável. Por isso a melhor solução encontrada é sempre viável. A `binaria.avaliar` dá 0 a toda solução inviável; a penalizada dá um valor tanto mais negativo quanto maior o excesso, o que ordena as inviáveis entre si.

## 3. Componentes

| Componente | O que faz | Nesta implementação |
|---|---|---|
| Solução inicial | ponto de partida `s0` | `construtiva` (padrão `binaria.construtiva_aleatoria`) |
| Vizinhança | todas as vizinhas `N(s)`, com o atributo de cada movimento | `vizinhanca` (padrão `binaria.vizinhanca_flip`) |
| Lista tabu | proíbe os movimentos reversos dos últimos `\|T\|` movimentos | vetor de prazo tabu, indexado pelo item |
| Aspiração | libera um movimento tabu em certas condições | por objetivo e por default |
| Parada | quando parar | `BTmax` iterações sem melhorar `s*`, ou o valor alvo |

### 3.1 Vizinhança

Diferente do SA, que sorteia **uma** vizinha, a BT examina a vizinhança **inteira** a cada iteração e escolhe a melhor admissível (slide 16). Por isso ela precisa de uma peça que liste as vizinhas, um encaixe que os outros esquemas não tinham:

`(solucao, itens, capacidade) -> [(rotulo, itens_alterados, vizinha)]`

| Peça | Movimento | Vizinhas | Atributo tabu |
|---|---|---|---|
| `binaria.vizinhanca_flip` | inverte um bit (a do slide) | `n` | o item do bit invertido |
| `binaria.vizinhanca_flip_troca` | inverte um bit ou troca um item de dentro por um de fora (a vizinhança das buscas locais binárias) | `n + dentro × fora` | o item, ou os dois itens trocados |
| `ordem.vizinhanca_troca` | troca duas posições da ordem | `n(n − 1)/2` | os dois itens trocados |

A vizinhança inclui as vizinhas inviáveis, como na tabela do slide: é a função de avaliação que as desfavorece. Na representação por ordem, cada vizinha é decodificada do zero, e uma iteração custa O(n³).

### 3.2 Lista tabu e vetor de prazo (slides 13, 14, 17 e 29)

Guardar soluções inteiras na memória é caro. A BT guarda **movimentos**, ou melhor, os atributos que eles alteram: na representação binária, a posição do bit; na ordem, os itens trocados (slide 13). A lista tabu contém os reversos dos últimos `|T|` movimentos e funciona como uma fila: quando chega um novo, o mais antigo sai.

Na prática (slide 29), a lista vira um **vetor de prazo tabu** `T̃` com uma posição por item: `T̃(i)` é a última iteração em que o item `i` está em quarentena. Na iteração `iter`, um movimento é tabu se algum item que ele altera tem `T̃(i) ≥ iter`, uma verificação O(1) por item. Depois de um movimento, seus itens ganham `T̃(i) = iter + |T|`. Com um item por movimento, isso equivale à fila de tamanho `|T|`.

O tamanho importa (slide 14): uma lista pequena demais não impede a ciclagem; grande demais restringe tanto que a busca fica sem opções.

### 3.3 Critérios de aspiração (slides 15 e 18)

A lista tabu pode proibir também soluções que nunca foram visitadas. Os critérios de aspiração tiram o status tabu de um movimento:

- **Por objetivo:** um movimento tabu é aceito se a vizinha **supera a melhor solução** já encontrada (`f(s') > f(s*)`). Uma solução melhor que todas as vistas certamente não foi visitada.
- **Por default:** se todos os movimentos são tabu e nenhum aspira, faz-se o tabu **mais antigo**, ou seja, o de prazo que acaba primeiro.

Em caso de empate no valor, fica a primeira vizinha na ordem da vizinhança, que no slide é o menor índice.

### 3.4 Parada (slide 19)

- `max_sem_melhora` (`BTmax`): para quando `Iter − MelhorIter > BTmax`, isto é, depois de `BTmax` iterações seguidas sem melhorar `s*`.
- `valor_alvo`: para assim que `f(s*)` atinge um valor conhecido, como o ótimo da programação dinâmica ou um limitante. Evita rodar à toa quando a solução já é boa o bastante.

### 3.5 Lista tabu dinâmica (slide 30)

Se a busca cicla com um certo `|T|`, mudar o tamanho muda a sequência de soluções e reduz a chance de repetir o ciclo. Com `tamanho_tabu=(Tmin, Tmax)`, `|T|` é sorteado em `[Tmin, Tmax]` na primeira iteração e de novo a cada `τ·Tmax` iterações (`tau`). Com um inteiro, a lista é fixa, e a BT fica determinística depois da solução inicial.

## 4. Pseudocódigo

Para maximização (o slide 20 está escrito para minimização):

```text
s  <- construtiva();  s* <- s
Iter <- 0;  MelhorIter <- 0
T̃(i) <- 0 para cada item

enquanto Iter − MelhorIter ≤ BTmax (e f(s*) < valor_alvo):
    Iter <- Iter + 1
    para cada vizinha (m, s') de N(s):            # m = itens alterados
        tabu(s') <- algum i de m tem T̃(i) ≥ Iter
    admissíveis <- vizinhas não tabu ou com f(s') > f(s*)    # aspiração por objetivo
    se há admissíveis:
        s' <- a de maior f entre as admissíveis (a primeira, no empate)
    senão:
        s' <- a de prazo tabu mais antigo                     # aspiração por default
    T̃(i) <- Iter + |T| para cada i de m
    s <- s'                                        # mesmo que piore
    se f(s) > f(s*):  s* <- s;  MelhorIter <- Iter

retornar s*
```

## 5. O exemplo do slide, passo a passo (slides 21 a 28)

Mochila de capacidade 23 com cinco objetos, `|T| = 1`, `BTmax = 1` e `α = 15`:

| Objeto | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Peso | 4 | 5 | 7 | 9 | 6 |
| Benefício | 2 | 2 | 3 | 4 | 4 |

| Iter | Solução corrente | f | Movimento escolhido | Tabu | s* | Iter − MelhorIter |
|---|---|---|---|---|---|---|
| 0 | 01010 | 6 | — | ∅ | 6 | 0 |
| 1 | 01011 | 10 | inverte o 5: o melhor vizinho | {5} | 10 | 0 |
| 2 | 00011 | 8 | inverte o 2: é piora, mas é o melhor vizinho não tabu (o bit 5 é tabu) | {2} | 10 | 1 |
| 3 | 00111 | 11 | inverte o 3 | {3} | 11 | 0 |
| 4 | 00101 | 7 | inverte o 4: o melhor vizinho, 00011 (8), é tabu e não aspira (8 < 11); 00101 e 00110 empatam em 7, e fica o primeiro | {4} | 11 | 1 |
| 5 | 10101 | 9 | inverte o 1: 00111 (11) é tabu e não aspira, porque 11 não supera 11 | {1} | 11 | 2 → para |

A busca devolve `s* = (00111)`, de valor 11, o ótimo. O teste `test_tabu_search_mochila__exemplo_do_slide` reproduz essa tabela, e o notebook mostra cada iteração com o depurador.

**Nota sobre o slide 27:** na iteração 4, os vizinhos (10111) e (01111) aparecem com pesos 24 e 25 e valores −2 e −17. Os pesos certos são 26 e 27, com valores 13 − 3·15 = −32 e 13 − 4·15 = −47 (o mesmo −47 que o slide 25 mostra para (01111)). Como as duas soluções são inviáveis, a escolha não muda.

## 6. Parâmetros

| Parâmetro | Papel | Padrão | Fonte |
|---|---|---|---|
| `tamanho_tabu` | `\|T\|` fixo, ou `(Tmin, Tmax)` para a lista dinâmica | 5 | slides 17 e 30 |
| `max_sem_melhora` | `BTmax`: iterações sem melhorar `s*` antes de parar | 50 | slide 19 |
| `tau` | a lista dinâmica sorteia `\|T\|` a cada `τ·Tmax` iterações | 1 | slide 30 |
| `valor_alvo` | para ao atingir este valor | `None` (desligado) | slide 19 |
| `avaliar` | função de avaliação | `binaria.avaliar_penalizada` | slide 23 |
| `construtiva`, `vizinhanca`, `debug` | as peças | binárias, 1-flip | [`utils/`](../../utils/README.md) |

## 7. O que os experimentos mostram

No notebook do laboratório (50 itens, 10 sementes, lista dinâmica `(5, 25)` e `BTmax = 100`):

- **Instância comum** (valores sorteados): a BT chega a 0,65% do ótimo em média, melhor que o SA (2,19%) com um número parecido de avaliações.
- **Instância correlacionada** (`valor = peso + 2`): a BT fica em cerca de 6%, a pior da linha de base. A mochila começa exatamente cheia, e o melhor vizinho é sempre tirar o item mais leve, que perde menos valor. Para melhorar, seria preciso tirar um item **pesado** e colocar vários leves, mas esse movimento nunca é o melhor vizinho. Com `|T| = 5` e a semente 0, a partir da iteração 8 a busca repete a mesma sequência de 16 soluções; listas maiores e dinâmicas mudam pouco o resultado.

Esse é o limite de uma BT só com memória de curto prazo: a escolha do melhor vizinho é míope. É o que motivam as estratégias de diversificação, oscilação estratégica e path-relinking dos slides 32 a 36.

## 8. Peças trocáveis

Todos os componentes são parâmetros, e a avaliação penalizada também encaixa nos outros esquemas. Exemplos:

```python
# vizinhança das buscas locais: 1-flip + troca 1-por-1
tabu_search_mochila(itens, capacidade, vizinhanca=binaria.vizinhanca_flip_troca)

# representação por ordem
tabu_search_mochila(
    itens,
    capacidade,
    avaliar=ordem.avaliar,
    construtiva=ordem.construtiva_aleatoria,
    vizinhanca=ordem.vizinhanca_troca,
)

# para ao atingir o ótimo
tabu_search_mochila(itens, capacidade, valor_alvo=valor_otimo)
```

## 9. Histórico

`tabu_search_mochila` devolve `(melhor_solucao, historico)`, no formato comum a todos os esquemas:

- `valor_candidato` e `valor_atual`: o valor da vizinha escolhida, iguais porque a BT sempre se move. Com a avaliação penalizada, podem ser negativos quando a busca passa por uma solução inviável;
- `melhor_valor`: o valor de `s*`;
- `avaliacoes`: cada vizinha examinada conta 1, então cada iteração com a 1-flip soma `n`;
- `tamanho_tabu`: o `|T|` da iteração (a partir da iteração 1), que o `plotar_historico` mostra no painel de baixo.

No `Depurador`, cada iteração gera a figura da vizinhança inteira, com as vizinhas tabu rotuladas com "(tabu)", e a da iteração, com a nota "aspiração" ou "todas tabu: a de prazo mais antigo" quando uma das aspirações decidiu a escolha. Como a última iteração não é conhecida de antemão, ela só é desenhada se cair em `a_cada`.

## 10. Exemplo

```python
import random

from metaheuristics.estudo.tabu_search import tabu_search_mochila
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

random.seed(0)
itens = gerar_instancia_aleatoria(20, 20, 100)
capacidade = sum(item.peso for item in itens) // 2
otimo, _ = programacao_dinamica(itens, capacidade)
melhor, historico = tabu_search_mochila(itens, capacidade)
melhor_valor = historico["melhor_valor"][max(historico["melhor_valor"])]
print(f"Ótimo: {otimo} | BT: {melhor_valor}")
plotar_historico(historico, otimo, eixo_x="iteracao", save=True)
```

## 11. Executar

Na raiz do repositório:

```bash
pytest tests/estudo/tabu_search
```

O teste da instância de referência usa a mesma instância de 20 itens e semente 0 dos outros esquemas e exige `gap <= 5%`, um critério do teste, não uma garantia da BT. Mude `PLOT = False` para `True` para salvar o gráfico.

## 12. Fora desta implementação

Os slides 31 a 36 trazem estratégias que vão além da memória de curto prazo:

- **Regiões planas** (slide 31): aumentar `|T|` enquanto o valor não muda e voltar ao tamanho original quando ele muda.
- **Intensificação** (slide 32): fixar os atributos das melhores soluções e explorar o resto.
- **Diversificação** (slide 33): com uma memória de longo prazo (por exemplo, a frequência de cada item nas soluções visitadas), levar a busca a regiões pouco exploradas.
- **Oscilação estratégica** (slide 34): variar `α`, ora aumentando, ora diminuindo, para alternar entre soluções viáveis e inviáveis.
- **Path-relinking** (slides 36 a 43): ligar soluções elite por caminhos na vizinhança; é o tema da próxima aula.

## 13. Questões para revisão

1. Como funciona a Busca Tabu em linhas gerais?
2. Quais são seus elementos e parâmetros característicos?
3. Do que é composta e para que serve a lista tabu? Como ela funciona?
4. Por que a lista guarda movimentos, e não soluções?
5. Para que servem os critérios de aspiração?
6. O que fazer para enfrentar as regiões planas do espaço de busca?
7. Como funciona e para que serve a oscilação estratégica?
8. Quais são os tipos de memória usados na Busca Tabu e para que serve cada um?

## 14. Referências

- Bahiense, L. *Metaheurísticas em Otimização Combinatória — Tema 8: Tabu Search (TS)*. Material didático.
- Glover, F. (1986). *Future Paths for Integer Programming and Links to Artificial Intelligence*. **Computers & Operations Research**, 13(5), 533–549.
- Glover, F. (1989). *Tabu Search — Part I*. **ORSA Journal on Computing**, 1(3), 190–206.
- Glover, F. (1990). *Tabu Search — Part II*. **ORSA Journal on Computing**, 2(1), 4–32.
- Glover, F. (1990). *Tabu Search: A Tutorial*. **Interfaces**, 20(4), 74–94.
- Hertz, A.; de Werra, D. (1990). *The Tabu Search Metaheuristic: How We Used It*. **Annals of Mathematics and Artificial Intelligence**, 1, 111–121.
- Gendreau, M.; Potvin, J.-Y. (2005). *Tabu Search*. In: Burke, E. K.; Kendall, G. (eds.), **Search Methodologies**. Springer.
