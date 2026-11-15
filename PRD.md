# PRD — GRASP + Path-Relinking no laboratório de metaheurísticas (Mochila 0-1)

## Contexto

A aula do Tema 9 apresenta o **GRASP** (*Greedy Randomized Adaptive Search Procedure*), de Feo e Resende (1989). É uma busca local multi-start: cada partida vem de uma **construção gulosa aleatória**, em que o próximo elemento é sorteado de uma Lista Restrita de Candidatos (RCL) controlada por α. A aula também apresenta o **Path-Relinking (PR)**, uma intensificação que guarda soluções elite e percorre o caminho entre a solução da iteração e uma solução elite.

O repositório já separa SA, ILS, VNS, ALNS e Busca Tabu em peças trocáveis (`metaheuristics/utils/`), com histórico, gráficos e depurador comuns. Esta entrega coloca o GRASP + PR no mesmo padrão. O PRD anterior, da Busca Tabu, está no histórico do git, e as decisões dele continuam valendo, registradas em [`utils/README.md`](metaheuristics/utils/README.md) e no [README da Busca Tabu](metaheuristics/tabu_search/README.md).

## Objetivo

Implementar o GRASP + PR como mais um esqueleto que recebe peças, com uma construtiva gulosa aleatória e um encaixe de reconexão nas duas representações, e deixar o pool elite e o PR prontos para outros esquemas.

## Decisões

| Tema | Decisão |
|---|---|
| Esquema | `grasp_mochila` em `metaheuristics/grasp/`. GRASP + PR (slide 35) **ligado por padrão**; com `reconexao=None`, vira o GRASP puro (slide 4) |
| Parada | `max_iteracoes` iterações (slide 35); o README cita a variante "sem melhoria" do slide 4 |
| Construção | `construtiva_gulosa_aleatoria(itens, capacidade, alfa=0.3, vies="aleatoria")`. Candidatos são os itens que ainda cabem (slide 12, aspecto adaptativo); a função gulosa é a densidade valor/peso. A RCL é por qualidade, `c(e) ≥ c_max − α·(c_max − c_min)` (slide 10, para maximização): α = 0 é a gulosa, α = 1 é aleatória entre os que cabem. Com a assinatura `(itens, capacidade)`, a peça também encaixa nos outros esquemas |
| GRASP reativo | `alfa` aceita um número (fixo) ou uma tupla (reativo, slide 18): α é sorteado com probabilidades que começam iguais e, a cada `periodo_reativo` iterações, viram `q_i = z̄_i / z*` normalizado (a razão do slide invertida, porque aqui é maximização). Um α ainda não usado fica com `q = 1` |
| Bias choice | argumento `vies` da construtiva (slide 21): `"aleatoria"`, `"logaritmica"`, `"exponencial"`, `"polinomial"` (ordem 2) ou uma função de rank. No GRASP, entra com `functools.partial` |
| Hashing | `hashing=True` (slide 23): se a solução construída já apareceu, reaproveita o ótimo local guardado em vez de rodar a busca local de novo. As buscas locais são determinísticas, então o resultado é o mesmo e só economiza avaliações |
| Busca local | padrão `binaria.busca_local_primeira_melhora` (slide 22: a primeira melhora é em geral mais rápida, e a melhor melhora converge cedo) |
| Pool elite | `tamanho_elite` (slide 36): a solução entra enquanto o pool não está cheio, se for nova. Depois, entra se superar a melhor do pool, ou se superar a pior **e** tiver Δ ≥ `diferenca_minima` de todas. Ela substitui a pior. Δ é a diferença simétrica, o número de passos até a outra solução |
| PR | a guia é sorteada no pool; a cada passo, avalia todos os movimentos que trazem um atributo da guia e aplica o melhor (slides 26–33); devolve a melhor solução intermediária do caminho, que substitui a da iteração se for melhor |
| Variantes do PR | `direcao="backward"` (parte da melhor das duas; padrão, "Melhor!" no slide 37), `"forward"` (parte da pior), `"backward_forward"` (as duas pontas andam alternadamente até se encontrarem, slide 38); `periodo_reconexao=k` aplica o PR a cada k iterações |
| Histórico | o formato comum, com `valor_candidato` = solução **construída** e `valor_atual` = depois da busca local e do PR (a distância entre as duas linhas mostra o trabalho da busca local), mais o extra `alfa`. Começa na iteração 1: o GRASP não tem uma solução inicial à parte |
| Representações | binária (padrão) e por ordem, como nos outros esquemas |
| Reaproveitamento | avaliações, buscas locais, histórico, gráficos, experimento e depurador. A construtiva por ordem usa a sequência de escolhas da binária, e a lógica do PR e do pool fica em `utils/reconexao.py`, independente da representação |

### Nomes das peças

| Encaixe | Binária | Ordem |
|---|---|---|
| construtiva (com `alfa` e `vies`) | `binaria.construtiva_gulosa_aleatoria` | `ordem.construtiva_gulosa_aleatoria` |
| reconexão `(solucao, itens, capacidade, guia) -> [(rotulo, vizinha)]` | `binaria.passos_para_guia` | `ordem.passos_para_guia` |

Funções independentes da representação, em `utils/reconexao.py`: `reconectar` e `atualizar_elite`.

## Escopo

- Esqueleto do GRASP + PR com README de teoria (slides do Tema 9), pseudocódigo, parâmetros, histórico e questões de revisão.
- Peças novas nas duas representações, exportadas pelos `__init__.py`, e `utils/reconexao.py`.
- Testes de cada peça nova, do PR, do pool elite e do esquema.
- READMEs (raiz, conceitos e `utils/`) e notebook do laboratório atualizados, com GRASP + PR e GRASP puro na linha de base.

## Fora do escopo

- Perturbação de custos (slides 19–20): indicada quando a construção é pouco sensível à randomização ou não há guloso, o que não é o caso da mochila.
- Filtering (slide 23), GRASP + VNS (slide 42) e relinking bidirecional (slide 38).

## Critérios de aceite

- O GRASP aceita qualquer avaliação, construtiva, busca local e reconexão compatíveis passadas por parâmetro, sem editar o esquema.
- Com `reconexao=None`, roda o GRASP puro; com o padrão, o GRASP + PR.
- O hashing não muda o resultado de uma execução, só reduz as avaliações.
- O histórico segue o formato comum, e `plotar_historico` funciona sem mudanças.
- `pytest` passa a partir da raiz, e os testes que já existiam não foram alterados.
- O notebook roda do começo ao fim sem erro.

## Próximos passos

- **GRASP:** perturbação de custos, filtering e GRASP + VNS.
- **Path-Relinking na Busca Tabu:** `reconectar` e `atualizar_elite` já são independentes do esquema.
- **Algoritmo genético:** esqueleto populacional, com peças novas por representação (cruzamento, mutação, seleção).
