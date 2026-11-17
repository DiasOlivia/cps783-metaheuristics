# PRD — Origem de cada peça na docstring

## Contexto

As peças trocáveis de `metaheuristics/utils/` foram criadas uma metaheurística por vez: SA, ILS e VNS (separadas no refactor `a198b85`), ALNS, Busca Tabu, GRASP, PSO, AG e ACO. Olhando uma função, não dá para saber para qual esquema ela nasceu. Por exemplo, `avaliar_penalizada` veio da Busca Tabu, e `gerar_vizinho`, do SA. O PRD anterior, do ACO, está no histórico do git.

## Objetivo

Registrar, na docstring de cada peça, a metaheurística para a qual ela foi criada.

## Decisões

| Tema | Decisão |
|---|---|
| Onde | uma linha logo após o resumo da docstring, como parágrafo próprio |
| Idioma | inglês, como o resto das docstrings |
| Conteúdo | só a metaheurística de origem e o papel da peça nela, por exemplo `Created for the ALNS (destroy operator).` Onde a peça é padrão hoje fica no catálogo do `utils/README.md` |
| Origem | levantada pelo git: cada esquema trouxe as suas peças no próprio commit. As de SA, ILS e VNS vêm do código anterior ao refactor. A busca de primeira melhora e as peças de ordem nasceram no refactor, como alternativas para os três |
| Fora | funções privadas (`_...`), a infraestrutura comum (`historico`, `experimento`, `plot`, `debug`, `instancia`) e os gulosos da primeira aula |

## Peças e origem

| Origem | Peças |
|---|---|
| SA | `temperaturas`, `metropolis`, `binaria.gerar_vizinho`, `ordem.gerar_vizinho` |
| SA, ILS e VNS | `binaria.calcular_valor_peso`, `binaria.avaliar`, `binaria.construtiva_aleatoria`, `binaria.construtiva_gulosa`; na ordem: `decodificar`, `avaliar`, `construtiva_aleatoria`, `construtiva_gulosa` |
| ILS e VNS | `aceita_melhora`, `binaria.perturbar`, `binaria.busca_local_melhor_melhora`, `binaria.busca_local_primeira_melhora`, `ordem.perturbar`, `ordem.busca_local_primeira_melhora` |
| ALNS | as remoções e inserções das duas representações |
| Busca Tabu | `binaria.avaliar_penalizada` e as vizinhanças das duas representações |
| GRASP | `reconectar`, `atualizar_elite`, `construtiva_gulosa_aleatoria` e `passos_para_guia` das duas representações |
| PSO | `coordenadas`, `mover_sigmoide` e `mover_chaves` |
| AG | as seleções, os cruzamentos, `binaria.reparar`, `ordem.mutacao_insercao` e `ordem.mutacao_inversao` |
| ACO | `Feromonio`, `construtiva_formiga` e `trilha` das duas representações |

## Critérios de aceite

- Cada uma das 61 peças públicas tem exatamente uma linha "Created for", e nenhuma outra função tem.
- O resto das docstrings não muda.
- `ruff` e `pytest` passam.
