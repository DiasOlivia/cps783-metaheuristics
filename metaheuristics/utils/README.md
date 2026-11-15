# Peças para montar metaheurísticas na Mochila 0-1

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**.

Esta pasta separa o SA, o ILS e o VNS em **peças trocáveis**. Os três algoritmos viraram esqueletos que recebem as peças como parâmetro, então dá para trocar uma parte de um pelo de outro (a aceitação do SA no ILS, a busca local no SA, a construtiva gulosa no VNS...) sem editar o código do esquema. Todos devolvem o mesmo histórico, usam os mesmos gráficos e aceitam o mesmo depurador visual.

Para experimentar, use o [notebook do laboratório](../laboratorio.ipynb). Os conceitos por trás (representação, heurística × metaheurística) estão no [README de conceitos](../README.md).

## 1. Organização

```text
utils/
├── instancia.py        Item, gerar_instancia_aleatoria, programacao_dinamica
├── aceitacao.py        aceita_melhora, temperaturas, metropolis
├── historico.py        novo_historico, registrar
├── experimento.py      rodar_sementes, resumir, tabela
├── plot.py             plotar_historico, plotar_comparacao
├── debug.py            Depurador
├── binaria/            peças da representação binária
│   ├── avaliacao.py    avaliar, calcular_valor_peso
│   ├── construtiva.py  construtiva_aleatoria, construtiva_gulosa
│   ├── movimento.py    gerar_vizinho
│   ├── perturbacao.py  perturbar
│   └── busca_local.py  busca_local_melhor_melhora, busca_local_primeira_melhora
└── ordem/              peças da representação por ordem
    ├── avaliacao.py    avaliar, decodificar
    ├── construtiva.py  construtiva_aleatoria, construtiva_gulosa
    ├── movimento.py    gerar_vizinho
    ├── perturbacao.py  perturbar
    └── busca_local.py  busca_local_primeira_melhora
```

O que fica na raiz de `utils/` vale para as duas representações. O que fica em `binaria/` e `ordem/` só funciona com soluções daquela representação.

As duas subpastas exportam as peças com os mesmos nomes, então trocar de representação é trocar o prefixo (`binaria.avaliar` → `ordem.avaliar`). Importe os módulos, não as funções, e evite uma variável chamada `ordem`, que esconderia o módulo:

```python
from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
```

## 2. As duas representações

A mesma solução (quais itens estão na mochila) pode ser escrita de dois jeitos. Exemplo com C = 9, pesos `[4, 3, 7, 5, 3, 2, 3]` e valores `[12, 8, 17, 11, 6, 2, 2]` (índices a partir de 0):

| | Binária | Por ordem |
|---|---|---|
| Solução com os itens 0 e 3 (valor 23) | `[1, 0, 0, 1, 0, 0, 0]` | `[0, 3, 1, 2, 4, 5, 6]` |
| Como se lê | um bit por item | a ordem em que se tenta colocar os itens; o decodificador coloca cada um que ainda couber |
| Análoga a | "por arestas" no caixeiro viajante | "por vértices" no caixeiro viajante |
| Viabilidade | pode passar da capacidade: `binaria.calcular_valor_peso` devolve valor 0 e a perturbação repara | sempre viável |
| Redundância | cada solução é um vetor só | `[3, 0, 6, 5, 4, 2, 1]` dá a mesma solução |

**Regra:** numa execução, todas as peças de `binaria/` ou de `ordem/` (avaliar, construtiva, movimento, perturbação, busca local) precisam ser da mesma representação. A aceitação, o histórico, os gráficos e o depurador servem para as duas.

## 3. Catálogo de peças

Peças com o mesmo **encaixe** e a mesma representação são trocáveis entre si.

| Encaixe | Assinatura | Binária | Por ordem |
|---|---|---|---|
| avaliar | `(solucao, itens, capacidade) -> valor` | `binaria.avaliar` | `ordem.avaliar` |
| construtiva | `(itens, capacidade) -> solucao` | `binaria.construtiva_aleatoria`; `binaria.construtiva_gulosa` (densidade valor/peso) | `ordem.construtiva_aleatoria`; `ordem.construtiva_gulosa` (densidade) |
| movimento | `(solucao, itens, capacidade, k, debug=None) -> solucao` | `binaria.gerar_vizinho`: k trocas viáveis de 1 bit | `ordem.gerar_vizinho`: k trocas de duas posições |
| perturbação | o mesmo do movimento | `binaria.perturbar`: k bits distintos + reparo | `ordem.perturbar`: embaralha os itens de k posições |
| busca local | `(solucao, itens, capacidade, debug=None) -> (solucao, avaliacoes)` | `binaria.busca_local_melhor_melhora`; `binaria.busca_local_primeira_melhora` | `ordem.busca_local_primeira_melhora` |
| aceitação | `(delta, iteracao) -> bool` | `aceita_melhora`; `metropolis(temperaturas(T0, Tmin, α), iteracoes_por_temperatura)` | (as mesmas) |

- As duas buscas locais binárias percorrem os mesmos movimentos (1-flip e troca 1-por-1), na mesma ordem. A de **melhor melhora** examina todos e aplica o melhor; a de **primeira melhora** aplica o primeiro que melhora (slide 28). Elas podem parar em ótimos locais diferentes.
- O movimento e a perturbação têm o mesmo encaixe, então também são trocáveis: dá para passar `binaria.gerar_vizinho` como perturbação do ILS ou `binaria.perturbar` como movimento do SA.
- A `metropolis` guarda a última decisão em `aceitar.ultimo` (temperatura, chance e sorteio), que o depurador mostra.
- **Custo da busca local por ordem:** cada vizinha é decodificada do zero, então uma passada custa O(n³). Medido: 0,04 s com 50 itens e 0,6 s com 100. Com ILS ou VNS de 250 iterações e 100 itens, isso passa de 2 minutos por execução. Prefira até ~50 itens.

## 4. Os esquemas e onde as peças entram

Os três seguem a mesma forma: **construtiva → [busca local] → laço (movimento ou perturbação → [busca local] → aceitação)**. O melhor resultado é guardado à parte do atual.

| | construtiva | movimento / perturbação | busca local | aceitação | regra própria |
|---|---|---|---|---|---|
| SA | `binaria.construtiva_aleatoria` | `movimento=binaria.gerar_vizinho` (k = `intensidade_movimento`) | `None` | `None` = Metropolis com as temperaturas | número de iterações = níveis de temperatura × iterações por nível |
| ILS | `binaria.construtiva_aleatoria` | `perturbacao=binaria.perturbar` (k = `intensidade_perturbacao`) | `binaria.busca_local_melhor_melhora`, também na solução inicial | `aceita_melhora` | — |
| VNS | `binaria.construtiva_aleatoria` | `perturbacao=binaria.perturbar` (k corrente) | `binaria.busca_local_melhor_melhora` | `aceita_melhora` | aceito: k = 1; senão k + 1, voltando a 1 depois de `k_max` |

Os valores da tabela são os padrões: sem passar nenhuma peça, cada algoritmo faz exatamente o que fazia antes, com os mesmos resultados para a mesma semente. Todos recebem também `avaliar` (padrão `binaria.avaliar`) e `debug`.

A assinatura do SA, como exemplo:

```python
def simulated_annealing_mochila(
    itens,
    capacidade,
    temperatura_inicial,
    temperatura_minima,
    fator_resfriamento,
    iteracoes_por_temperatura,
    avaliar=binaria.avaliar,  # como calcular o valor de uma solução
    construtiva=binaria.construtiva_aleatoria,  # como montar a 1ª solução
    movimento=binaria.gerar_vizinho,  # como gerar um candidato
    intensidade_movimento=1,  # o k passado ao movimento
    busca_local=None,  # melhorar o candidato antes de decidir? None = não
    aceitacao=None,  # None = Metropolis com as temperaturas acima
    verbose=False,  # True = imprime as melhorias
    debug=None,  # Depurador: uma figura por etapa
): ...
```

E como trocar cada peça:

```python
simulated_annealing_mochila(..., construtiva=binaria.construtiva_gulosa)
simulated_annealing_mochila(
    ..., movimento=binaria.perturbar, intensidade_movimento=3
)
simulated_annealing_mochila(..., busca_local=binaria.busca_local_primeira_melhora)
simulated_annealing_mochila(..., aceitacao=aceita_melhora)

# outra representação: troque o prefixo de todas as peças
simulated_annealing_mochila(
    ...,
    avaliar=ordem.avaliar,
    construtiva=ordem.construtiva_aleatoria,
    movimento=ordem.gerar_vizinho,
)
```

Na representação por ordem, a solução devolvida é uma ordem. Use `ordem.decodificar` para ver os itens.

## 5. Histórico

Todo esquema devolve `(melhor_solucao, historico)`. O histórico é um dicionário de dicionários indexados pela iteração, e a iteração 0 é a solução inicial.

| Chave | Conteúdo |
|---|---|
| `valor_candidato` | valor da solução gerada na iteração |
| `valor_atual` | valor da solução corrente depois da aceitação |
| `melhor_valor` | melhor valor encontrado até a iteração |
| `avaliacoes` | soluções avaliadas, acumuladas: cada candidato conta 1, e a busca local soma as vizinhas que examinou |
| `temperatura` (SA), `k` (VNS) | extras de cada esquema |

**Compare esquemas pelas avaliações, não pelas iterações.** Uma iteração do SA avalia 1 vizinho; uma do ILS ou do VNS roda uma busca local inteira, que pode avaliar centenas.

## 6. Instâncias

`gerar_instancia_aleatoria(num_itens, max_peso, max_valor, correlacionada=False)`:

- **comum:** peso e valor sorteados separadamente. Existem itens claramente bons e claramente ruins, e quase todo método acerta;
- **correlacionada:** `valor = peso + max(1, max_peso // 10)` (a instância "fortemente correlacionada" de Pisinger). Todos os itens rendem parecido por unidade de peso, o difícil é encaixar os pesos, e as combinações se diferenciam.

Sem a opção, os sorteios são os mesmos de antes: a mesma semente gera os mesmos itens.

## 7. Gráficos e experimentos

| Função | O que faz |
|---|---|
| `plotar_historico(historico, valor_otimo, eixo_x, show, save)` | candidato, atual, melhor e ótimo de uma execução, com um painel extra para `temperatura` ou `k` |
| `plotar_comparacao({rótulo: histórico}, valor_otimo, eixo_x, show, save)` | o melhor valor de várias combinações, sobrepostos |
| `rodar_sementes(esquema, itens, capacidade, sementes, **parametros)` | roda um esquema uma vez por semente e mede o tempo |
| `resumir(execucoes, valor_otimo)` | gap médio, melhor e pior, ótimos atingidos, avaliações até o melhor e tempo |
| `tabela({rótulo: resumo})` | os resumos em uma tabela de texto |

`show=True` mostra a figura (no notebook, abaixo da célula); `save=True` grava em `plots/utils/`.

## 8. Depurador visual

```python
debug = Depurador(
    itens, capacidade, valor_otimo=otimo, show=True, a_cada=100, limite=20
)
simulated_annealing_mochila(..., debug=debug)
```

Cada figura tem três painéis:

1. **Solução atual:** uma faixa com os itens dentro da mochila até a capacidade C, e as listas `dentro` e `fora` com `item (peso/valor)`.
2. **Plano peso × valor:** cada solução vira um ponto. Aparecem a trilha das soluções atuais (azul), as vizinhas vistas na etapa (verde se melhoram, amarelo se empatam, vermelho se pioram, × se não cabem), a escolhida (estrela) e o melhor até agora (losango roxo). Nas iterações da representação binária, aparecem também as vizinhas "±item".
3. **Mini-histórico:** valor atual, melhor e candidatos por iteração, na mesma escala de valor do painel 2, com a temperatura ou o k no eixo da direita.

- `show` diz se a figura aparece na tela; `save` diz se ela vira arquivo, em `plots/debug/<data-hora>/`. É preciso ligar pelo menos um dos dois.
- `a_cada=N` desenha a cada N iterações, mais a primeira e a última. Nessas iterações, a busca local e a perturbação também geram suas figuras (uma por passada).
- `limite` é o número máximo de figuras. **Cuidado com o volume:** o SA padrão tem 6.600 iterações; com `a_cada=1` seriam milhares de figuras.
- Na representação por ordem, passe `decodificar=ordem.decodificar`.
- O depurador não sorteia números: o resultado com e sem debug é idêntico.

## 9. Como montar uma mistura

1. Escolha o esquema: `simulated_annealing_mochila`, `iterated_local_search_mochila` ou `variable_neighborhood_search_mochila`.
2. Troque as peças passando-as como parâmetro, todas da mesma representação.
3. Rode em várias sementes com `rodar_sementes`, resuma com `resumir` e compare com a linha de base em `tabela` e `plotar_comparacao`.

A última seção do [notebook](../laboratorio.ipynb) traz esse molde pronto para preencher.

## 10. Próximas metaheurísticas

A estrutura foi pensada para receber Busca Tabu, algoritmo genético e GRASP:

- cada uma ganha sua pasta de esqueleto, como `simulated_annealing/`;
- as peças novas entram na subpasta da representação: GRASP precisa de uma construtiva gulosa aleatorizada; o genético, de cruzamento, mutação e seleção; a Busca Tabu, de memória e de uma vizinhança que se possa listar;
- o histórico aceita chaves extras (por exemplo, a média da população no genético).
