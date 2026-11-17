# PRD — PSO (Enxame de Partículas) no laboratório de metaheurísticas (Mochila 0-1)

## Contexto

A aula do Tema 10 apresenta a **Otimização por Enxame de Partículas (PSO)**, de Kennedy e Eberhart (1995). Um enxame de partículas "voa" pelo espaço de busca, e cada partícula ajusta a sua velocidade pela própria melhor posição (cognição individual) e pela melhor posição do enxame (aprendizado social).

O PSO dos slides é **contínuo** (`x ← x + v`), e a mochila é discreta. O repositório já separa SA, ILS, VNS, ALNS, Busca Tabu e GRASP em peças trocáveis (`metaheuristics/utils/`), com histórico, gráficos e depurador comuns. Esta entrega adapta o PSO às duas representações e o coloca no mesmo padrão. O PRD anterior, do GRASP, está no histórico do git, e as decisões dele continuam valendo, registradas em [`utils/README.md`](metaheuristics/utils/README.md) e no [README do GRASP](metaheuristics/grasp/README.md).

## Objetivo

Implementar o PSO como mais um esqueleto que recebe peças, com a velocidade da equação (1) dos slides e um voo próprio de cada representação, sem mudar o que já existe.

## Decisões

| Tema | Decisão |
|---|---|
| Esquema | `particle_swarm_optimization_mochila` em `metaheuristics/particle_swarm_optimization/`, seguindo o nome em inglês dos outros |
| Velocidade | a equação (1) do slide 13, por item: `v ← w·v + c1·r1·(pbest − x) + c2·r2·(gbest − x)`, com `r1, r2 ~ U(0, 1)` sorteados por dimensão e `v` limitada a `[−vmax, vmax]` (slide 15). As velocidades iniciais são sorteadas em `[−vmax, vmax]` (slide 18) |
| Binária | **PSO binário** (Kennedy e Eberhart, 1997): a posição é o vetor de bits, e o voo sorteia cada bit como 1 com probabilidade `sigmoide(v)`. Com `vmax = 4`, essa chance fica entre 1,8% e 98,2%, o que explica o "vmax = 4 ou 5" do slide 15 |
| Ordem | **chaves por posição**: a coordenada de cada item é a posição dele na ordem (`n` para o primeiro, `1` para o último); o voo soma `v` às chaves e reordena por elas. `vmax = 4` é andar até 4 posições por iteração |
| Posição = solução | nas duas representações, a posição de cada partícula é uma solução comum, então construtivas, avaliação, buscas locais, `Depurador` e gráficos funcionam sem mudança |
| Inviabilidade | avaliação padrão `binaria.avaliar_penalizada` (Busca Tabu): uma partícula que não cabe vale no máximo 0. O enxame começa viável (`construtiva=binaria.construtiva_aleatoria`, a "inicialização aleatória" do slide 18), então pbest e gbest são sempre viáveis |
| Parâmetros | os padrões de **Kennedy e Eberhart** (o "*" do slide 14): `inercia=1`, `c1=2`, `c2=2`, `vmax=4`. Os "artigos mais recentes" (0,5; 1,5; 1,5) foram calibrados para o PSO contínuo: na mochila, w = 0,5 encolhe as velocidades e deixa o voo quase aleatório (11,5% de gap contra 0,5% na instância comum de 50 itens). O README mostra a comparação e as faixas `[0,5; 1,5]` e `[1,5; 2,5]` |
| Inércia decrescente | `inercia` aceita um número (fixo) ou um par `(inicial, final)`: `wᵗ` cai linearmente ao longo das iterações (slides 13 e 16: começa diversificando e termina intensificando) |
| Busca local | opcional (`busca_local=None`), aplicada à partícula que **melhora o próprio pbest** (PSO "memético"): o pbest é sempre viável, e as buscas locais binárias exigem solução viável |
| Atualização | como no slide 18: partícula a partícula, o pbest e o gbest são atualizados assim que ela voa |
| Parada | `max_iteracoes` |
| Histórico | por iteração, a partir da 0 (o enxame inicial): `valor_candidato` = **média do enxame**, `valor_atual` = **melhor partícula da iteração**, `melhor_valor` = gbest, `avaliacoes` (uma por partícula, mais a busca local) e o extra `inercia` |
| Depurador | sem mudança: cada iteração gera um passo "enxame", com todas as partículas no plano peso × valor, e a figura da iteração |
| Reaproveitamento | avaliação penalizada, construtivas, buscas locais, histórico, gráficos, experimento e depurador |

### Nomes das peças

| Encaixe | Binária | Ordem |
|---|---|---|
| coordenadas `(solucao, itens, capacidade) -> [float]` | `binaria.coordenadas`: os bits | `ordem.coordenadas`: a posição de cada item na ordem |
| voo `(solucao, itens, capacidade, velocidade) -> solucao` | `binaria.mover_sigmoide`: cada bit é 1 com probabilidade `sigmoide(v)` | `ordem.mover_chaves`: reordena pelas chaves `coordenadas + v` |

## Escopo

- Esqueleto do PSO com README de teoria (slides do Tema 10), a adaptação para a mochila, parâmetros, histórico e questões de revisão.
- Peças `enxame.py` em `utils/binaria/` e `utils/ordem/`, exportadas pelos `__init__.py`.
- Testes de cada peça nova e do esquema.
- READMEs (raiz, conceitos e `utils/`) e notebook do laboratório atualizados.

## Fora do escopo

- c1 e c2 adaptativos (slide 15): o slide não diz quais estatísticas usar, então a regra seria nossa.
- Topologias de vizinhança (lbest) e outras variantes que não estão nos slides.

## Critérios de aceite

- O PSO aceita qualquer avaliação, construtiva, coordenadas, voo e busca local compatíveis passados por parâmetro, sem editar o esquema.
- A velocidade nunca passa de `vmax`.
- O histórico segue o formato comum, e `plotar_historico` funciona sem mudanças.
- `pytest` passa a partir da raiz, e os testes que já existiam não foram alterados.
- O notebook roda do começo ao fim sem erro.

## Próximos passos

- **PSO:** c1 e c2 adaptativos e topologias de vizinhança.
- **Path-Relinking na Busca Tabu:** `reconectar` e `atualizar_elite` já são independentes do esquema.
- **Algoritmo genético:** esqueleto populacional, com peças novas por representação (cruzamento, mutação, seleção).
