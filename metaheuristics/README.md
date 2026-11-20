# Conceitos: Representação e Metaheurísticas

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 3.

Antes de escolher um algoritmo, vale responder duas perguntas: **como escrever uma solução** no computador (a representação) e **o que cada parte do algoritmo faz** (heurística construtiva, busca local e metaheurística). Este README trata das duas, com exemplos dos algoritmos desta pasta.

## 1. Representação de soluções

Em muitos problemas combinatórios, uma solução é um **subconjunto** de um conjunto base `E`, e o conjunto de soluções viáveis é `F ⊆ 2^|E|`. A **representação** indica quais elementos de `E` estão na solução e quais não estão.

Na Mochila 0-1 com `n` itens, `E` são os itens e a solução é um vetor binário `x`, com `x_i = 1` quando o item `i` é escolhido. É a representação padrão do SA, do ILS e do VNS desta pasta: `[1, 1, 1, 1, 0, 0]` leva os itens 1 a 4.

## 2. Duas representações para o Caixeiro Viajante

Num problema sobre grafo, a mesma solução pode ser anotada de duas formas. **Não são duas formas de resolver o problema**: são duas formas de escrever a resposta que o algoritmo vai criar e modificar.

Exemplo com 4 cidades e 6 arestas:

```text
a ───e1─── b
│ ╲      ╱ │
e4  e5  e6  e2
│  ╱    ╲  │
d ───e3─── c
```

`e1 = a–b`, `e2 = b–c`, `e3 = c–d`, `e4 = d–a`, `e5 = a–c` e `e6 = b–d`. Uma solução é uma volta que passa por todas as cidades e retorna à origem, por exemplo `a → b → c → d → a`.

### 2.1 Por arestas: quais arestas a volta usa?

A solução é um vetor binário com uma posição por aresta: `v_e = 1` se a aresta `e` está na volta. A volta `a → b → c → d → a` vira `(1, 1, 1, 1, 0, 0)`.

- **Tamanho `O(n²)`**, porque o grafo completo tem `n(n − 1)/2` arestas.
- **A maioria dos vetores não é uma volta.** `(1, 1, 0, 0, 0, 0)` não visita `d` e não retorna a `a`. `(1, 1, 1, 1, 1, 1)` deixa todas as cidades com grau 3. Dos `2⁶ = 64` vetores possíveis, só 3 são voltas. Por isso o algoritmo precisa verificar que cada vértice tem grau 2 e que não há subciclo, como faz o [guloso do caixeiro viajante](estudo/guloso/caixeiro_viajante/README.md).

### 2.2 Por vértices: em que ordem a volta passa pelas cidades?

A solução é uma permutação das cidades, com a primeira fixa, já que o ponto de partida de um ciclo é arbitrário. A volta `a → b → c → d → a` vira `abcd`.

- **Tamanho `O(n)`.**
- **Toda permutação é uma volta válida** num grafo completo.
- **Simetria:** a mesma volta aparece duas vezes, uma em cada sentido. `abcd` e `adcb` são o mesmo ciclo, então há `(n − 1)!` permutações para `(n − 1)!/2` voltas distintas.

### 2.3 As 3 voltas do exemplo nas duas formas

| Volta | Por arestas | Por vértices |
|---|---|---|
| `a → b → c → d → a` | `(1, 1, 1, 1, 0, 0)` | `abcd` ou `adcb` |
| `a → b → d → c → a` | `(1, 0, 1, 0, 1, 1)` | `abdc` ou `acdb` |
| `a → c → b → d → a` | `(0, 1, 0, 1, 1, 1)` | `acbd` ou `adbc` |

| | Por arestas | Por vértices |
|---|---|---|
| O que anota | quais arestas usar | a ordem dos vértices |
| Tamanho | `O(n²)` | `O(n)` |
| Viabilidade | a maioria dos vetores é inviável: é preciso checar grau e subciclo | toda permutação é viável |
| Redundância | cada volta é um único vetor | cada volta aparece duas vezes |

## 3. A representação muda a vizinhança

O algoritmo cria e modifica essas anotações o tempo todo, então a representação define quais mudanças pequenas (movimentos) fazem sentido.

- **Por arestas:** trocar um único bit nunca leva de uma volta a outra, porque o vetor fica com `n − 1` ou `n + 1` arestas. O menor movimento que preserva a volta é tirar 2 arestas e colocar outras 2: o **2-OPT**.
- **Por vértices:** trocar duas cidades de posição sempre gera outra volta válida (slides 9 e 10), e o 2-OPT equivale a inverter um trecho da sequência. Por causa da simetria, alguns movimentos não mudam a volta. Trocar `b` e `c` em `abdc` gera `acdb`, que é a mesma volta percorrida ao contrário.

## 4. O mesmo dilema em outros problemas

**Árvore Geradora Mínima.** O [Kruskal](estudo/guloso/kruskal/README.md) devolve a árvore por arestas, como a lista das suas `n − 1` arestas. Por vértices, a árvore pode ser um vetor de pais (`pred[v]` é o vértice ao qual `v` se liga, a partir de uma raiz), de tamanho `O(n)`, ou um código de Prüfer: uma sequência de `n − 2` vértices em que, no grafo completo, toda sequência corresponde a uma árvore válida. O vetor `pai` usado dentro do `kruskal` parece um vetor de pais, mas é o union-find: ele só registra quais vértices já estão no mesmo componente.

**Mochila 0-1.** Não há grafo, mas o dilema reaparece:

- **Vetor binário** (o desta pasta): diz quais itens entram. Muitos vetores passam da capacidade. Por isso `binaria.calcular_valor_peso` devolve valor 0 para eles, e o ILS e o VNS reparam a solução depois de perturbá-la.
- **Ordem dos itens + inserção gulosa:** a solução é uma permutação, decodificada colocando cada item que ainda couber. Toda ordem gera uma solução viável, mas há muita redundância: com 20 itens, são `20!` ordens para no máximo `2²⁰` subconjuntos.

A segunda forma já aparece no repositório: `binaria.construtiva_aleatoria` sorteia uma ordem e a decodifica, e a [mochila gulosa](estudo/guloso/mochila/README.md) escolhe a ordem por peso, valor ou densidade.

As duas estão implementadas como peças em [`utils/`](utils/README.md): `utils/binaria/` e `utils/ordem/`. O SA, o ILS, o VNS, a ALNS, a Busca Tabu, o GRASP, o PSO, o AG e o ACO aceitam qualquer uma delas, e o [notebook do laboratório](laboratorio.ipynb) permite compará-las.

| | Representação direta | Representação por ordem |
|---|---|---|
| Exemplos | volta por arestas, árvore por arestas, mochila binária | volta por permutação, árvore por Prüfer, mochila por ordem |
| Viabilidade | muitas soluções inviáveis: é preciso checar ou reparar | sempre (ou quase sempre) viável |
| Redundância | cada solução aparece uma vez | a mesma solução aparece várias vezes |
| Movimento natural | precisa preservar a viabilidade | trocar posições basta |

Escolher a representação é escolher com qual problema lidar: inviabilidade ou redundância.

## 5. Heurística × metaheurística

### 5.1 Instância e solução

A **instância** são os dados de entrada: na mochila, os itens (peso e valor) e a capacidade; no caixeiro viajante, as cidades e os custos. Ela não muda enquanto o algoritmo roda. Nos testes desta pasta, a instância vem de `gerar_instancia_aleatoria`.

A **solução** é o que o algoritmo constrói e modifica, na representação escolhida.

### 5.2 Três camadas

```text
instância ─▶ [heurística construtiva] ─▶ 1ª solução ─▶ [busca local] ─▶ ótimo local
                                                             ▲                 │
                                                             └─[metaheurística]┘
                                     "travou? perturbe, aceite uma piora, troque de vizinhança"
```

| Camada | O que faz | Exemplos nesta pasta |
|---|---|---|
| Heurística construtiva | monta uma solução do zero | os [gulosos](estudo/guloso/README.md), `binaria.construtiva_aleatoria`, a construção gulosa aleatória do GRASP e a construção da formiga do ACO |
| Heurística de melhoria (busca local) | troca a solução corrente por uma vizinha melhor enquanto houver uma | `busca_local_melhor_melhora` e `busca_local_primeira_melhora`, com 1-flip e troca 1-por-1, em [`utils/binaria/`](utils/README.md) |
| Metaheurística | decide o que fazer quando a busca local para num ótimo local | SA, ILS, VNS, ALNS, Busca Tabu, GRASP, PSO, AG e ACO |

Construtiva e melhoria são os dois tipos básicos de heurística (seção 5 do [README do guloso](estudo/guloso/README.md)). A busca local sozinha esbarra num limite: ela termina no primeiro ótimo local encontrado (slide 33).

### 5.3 Definições

- **Heurística:** procedimento feito para um problema específico, que fornece uma boa solução sem garantia de que seja ótima. Pode construir uma solução ou melhorar uma existente.
- **Metaheurística:** estratégia de alto nível e genérica, que guia outras heurísticas para continuar a busca depois que a melhoria trava, escapando de ótimos locais de baixa qualidade (slide 35). Para isso, combina componentes como construções gulosas, aleatorização, busca local, múltiplas vizinhanças, memória, intensificação e diversificação (slide 36).

Portanto, construir uma solução e depois melhorá-la ainda é heurística: construtiva seguida de busca local. O que torna o algoritmo uma metaheurística é a camada de cima. Uma metaheurística especializada para um problema também passa a ser uma heurística.

### 5.4 O ILS tem as três camadas

Em [`iterated_local_search_mochila`](estudo/iterated_local_search/__init__.py):

1. `binaria.construtiva_aleatoria` é a heurística construtiva;
2. `binaria.busca_local_melhor_melhora` é a heurística de melhoria;
3. o laço com `binaria.perturbar`, uma nova busca local e o critério de aceitação é a metaheurística.

Cada uma dessas peças é um parâmetro da função, então dá para trocar uma camada sem mexer nas outras ([`utils/`](utils/README.md)).

### 5.5 Contraexemplo: o SA

O [Simulated Annealing](estudo/simulated_annealing/README.md) desta pasta, por padrão, não tem busca local: o parâmetro `busca_local` vem vazio. Ele anda de vizinho em vizinho e às vezes aceita uma piora, com uma probabilidade que diminui junto com a temperatura. Uma metaheurística não precisa partir de uma solução pronta para melhorá-la: o que a define é a estratégia para não ficar preso em ótimos locais.

## 6. Questões para revisão

1. Por que as representações por arestas e por vértices descrevem a mesma solução, mas levam a algoritmos diferentes?
2. Como fica a volta `a → c → d → b → a` nas duas representações? A qual das 3 voltas do exemplo ela corresponde?
3. Por que trocar um único bit nunca leva de uma volta a outra na representação por arestas?
4. Na representação por vértices, quantas permutações correspondem à mesma volta? Por quê?
5. Na mochila, qual é a vantagem e qual é o custo de representar a solução por uma ordem de itens?
6. Qual é a diferença entre uma heurística de melhoria e uma metaheurística?
7. Quais são as três camadas do ILS e onde cada uma aparece no código?

