# PRD — Laboratório de metaheurísticas para a Mochila 0-1

## Contexto

O exercício pede para resolver um problema "brincando" com as metaheurísticas: trocar e misturar partes de cada uma e comparar os resultados. O problema escolhido é a **Mochila 0-1**, o mesmo do SA, do ILS e do VNS que já existiam.

Antes desta entrega, não dava para misturar os algoritmos:

- as funções básicas (`Item`, `gerar_instancia_aleatoria`, `calcular_valor_peso`, `programacao_dinamica`, `gerar_solucao_inicial`) existiam em 3 cópias;
- cada algoritmo devolvia um histórico diferente e tinha um gráfico próprio;
- "iteração" não significava a mesma coisa nos três;
- os testes do ILS e do VNS falhavam quando rodados da raiz.

## Objetivo

Separar os algoritmos em **peças pequenas e trocáveis**, organizadas pelas camadas do [README de conceitos](metaheuristics/README.md) (construtiva, movimento/perturbação, busca local, aceitação), em duas representações. SA, ILS e VNS passam a ser esqueletos que recebem essas peças. Todos usam o mesmo histórico, os mesmos gráficos e um depurador que torna visível cada etapa da busca. Um notebook explica as peças e roda a linha de base; **as misturas ficam com quem faz o exercício**.

## Decisões

| Tema | Decisão |
|---|---|
| Problema | Mochila 0-1 |
| Módulos atuais (SA, ILS, VNS) | refatorados para usar as peças; os resultados com as peças padrão e a mesma semente não mudam |
| Organização | `metaheuristics/utils/`, um arquivo por tipo de peça |
| Representações | binária (análoga à "por arestas") e por ordem com decodificador guloso (análoga à "por vértices"), cada uma numa subpasta; o comum fica na raiz de `utils/` |
| Peças novas | construtiva gulosa (densidade) e busca local por primeira melhora; na representação por ordem, todas as peças |
| Histórico | formato único (`valor_candidato`, `valor_atual`, `melhor_valor`, `avaliacoes` + extras como `temperatura` e `k`); as chaves antigas e os `plot.py` de cada algoritmo saem |
| Eixo de comparação | avaliações acumuladas, porque iterações de esquemas diferentes custam esforços diferentes |
| Prints do SA | ficam atrás de `verbose=False` |
| Instâncias | nova opção correlacionada (`valor = peso + max(1, max_peso // 10)`); sem ela, os sorteios são idênticos aos de antes |
| Gráficos | `show` (mostrar) e `save` (gravar em `plots/`) |
| Debug | `Depurador(show, save, a_cada, limite)`, passado como `debug` ao esquema, que o repassa às peças. Figura com 3 painéis, validada em protótipo: faixa da solução atual, plano peso × valor (trilha e vizinhas) e mini-histórico na mesma escala |
| Interface | notebook `metaheuristics/laboratorio.ipynb`, sem combinações prontas, com uma seção "Suas misturas" |
| Nomes das peças | o mesmo nome nas duas representações, com o módulo como prefixo (`binaria.avaliar`, `ordem.avaliar`), para que trocar de representação seja trocar o prefixo; `binaria/__init__.py` e `ordem/__init__.py` exportam as peças. Todas as peças e esquemas recebem `(solucao, itens, capacidade, ...)`. Tabela abaixo |

### Nomes das peças

| Encaixe | Binária | Ordem |
|---|---|---|
| avaliar | `avaliar_solucao` → `binaria.avaliar` | `avaliar_ordem` → `ordem.avaliar` |
| construtiva | `gerar_solucao_inicial` → `binaria.construtiva_aleatoria` | `ordem_aleatoria` → `ordem.construtiva_aleatoria` |
| construtiva | `solucao_gulosa` → `binaria.construtiva_gulosa` | `ordem_gulosa` → `ordem.construtiva_gulosa` |
| movimento | `gerar_vizinho` → `binaria.gerar_vizinho` | `trocar_posicoes` → `ordem.gerar_vizinho` |
| perturbação | `perturbar_solucao` → `binaria.perturbar` | `perturbar_ordem` → `ordem.perturbar` |
| busca local | `busca_local` → `binaria.busca_local_melhor_melhora` | — |
| busca local | `busca_local_primeira_melhora` → `binaria.busca_local_primeira_melhora` | `busca_local_ordem` → `ordem.busca_local_primeira_melhora` |
| auxiliar | `calcular_valor_peso` → `binaria.calcular_valor_peso` | `decodificar_ordem` → `ordem.decodificar` |

`aceitacao.py` não muda. Nas peças de ordem, o parâmetro `ordem` vira `solucao`; nas binárias e nos esquemas, `capacidade_mochila` vira `capacidade`.

## Escopo entregue

- `metaheuristics/utils/`: instância, aceitação, histórico, experimento (sementes, resumo e tabela), gráficos, depurador, e as peças de `binaria/` e `ordem/`. O catálogo está em [`utils/README.md`](metaheuristics/utils/README.md).
- SA, ILS e VNS com parâmetros de peças (`avaliar`, `construtiva`, `movimento`/`perturbacao`, `busca_local`, `aceitacao`, `debug`).
- Testes para cada peça em `tests/utils/` e testes dos esquemas nas duas representações. Imports corrigidos, e `pytest` roda tudo a partir da raiz.
- Notebook do laboratório e READMEs atualizados. `ipykernel` adicionado às dependências.

## Fora do escopo

- Caixeiro Viajante e outras representações além de binária e ordem.
- O notebook antigo `SA_Mochila_0_1.ipynb`, que tem as funções copiadas dentro dele.
- A pasta `guloso/`.

## Critérios de aceite

- Qualquer esquema aceita qualquer peça compatível passada por parâmetro, sem editar o código do esquema.
- SA, ILS e VNS, com as peças padrão, reproduzem os resultados anteriores. Verificado em 18 execuções (3 sementes × 2 tamanhos × 3 esquemas), com e sem o depurador.
- Todos os esquemas devolvem o histórico comum, e o mesmo gráfico funciona para qualquer um.
- `pytest` passa a partir da raiz.
- O notebook roda do começo ao fim sem erro.
- Não existe mais nenhuma cópia das funções básicas da mochila.

## Próximos passos

- **Busca Tabu:** esqueleto próprio; precisa de memória (lista tabu) e de uma vizinhança que se possa listar.
- **Algoritmo genético:** esqueleto populacional; peças novas por representação (cruzamento, mutação, seleção). O histórico já aceita extras, como a média da população.
- **GRASP:** construtiva gulosa aleatorizada (lista restrita de candidatos) seguida da busca local que já existe.
