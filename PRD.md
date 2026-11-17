# PRD — Algoritmo Genético no laboratório de metaheurísticas (Mochila 0-1)

## Contexto

A aula do Tema 11 apresenta os **Algoritmos Genéticos** (Holland, 1975; Goldberg, 1989). Uma população de indivíduos evolui por gerações: os mais aptos têm mais chance de se reproduzir (seleção), os pais trocam genes (cruzamento), alguns indivíduos sofrem pequenas alterações (mutação), e os melhores passam intactos para a geração seguinte (elitismo).

O repositório já separa SA, ILS, VNS, ALNS, Busca Tabu, GRASP e PSO em peças trocáveis (`metaheuristics/utils/`), com histórico, gráficos e depurador comuns. Esta entrega coloca o AG no mesmo padrão. O PRD anterior, do PSO, está no histórico do git, e as decisões dele continuam valendo, registradas em [`utils/README.md`](metaheuristics/utils/README.md) e no [README do PSO](metaheuristics/particle_swarm_optimization/README.md).

## Objetivo

Implementar o AG do slide 9 como mais um esqueleto que recebe peças, com os métodos de seleção e os operadores de cruzamento e mutação dos slides nas duas representações, sem mudar o que já existe.

## Medições que embasaram as decisões

Protótipo na instância correlacionada de 50 itens (a da linha de base do notebook), 10 sementes, população 50, 100 gerações (≈ 4.300 avaliações):

| Configuração | Gap médio | Ótimos |
|---|---|---|
| Binária, uniforme, só avaliação penalizada | ~2,1% | 0/10 |
| Binária, uniforme, reparo guloso, roleta | 0,00% | 10/10 (comum: 0,02%, 7/10) |
| Binária com reparo, sem cruzamento | 2,23% | 0/10 |
| Ordem, LOX, roleta | 0,91% | 0/10 (comum: 2,84%) |

Metade dos filhos do cruzamento binário passa da capacidade. Com torneio nas duas seleções, a população colapsa em 1 ou 2 indivíduos distintos; com roleta, ficam de 3 a 7.

## Decisões

| Tema | Decisão |
|---|---|
| Esquema | `genetic_algorithm_mochila` em `metaheuristics/genetic_algorithm/`, seguindo o nome em inglês dos outros |
| Geração (slide 9) | **Cruzamento:** `tamanho_populacao // 2` tentativas; cada uma, com probabilidade `prob_cruzamento`, seleciona um par na população e gera dois filhos. **Mutação:** `tamanho_populacao` tentativas; cada uma, com probabilidade `prob_mutacao`, seleciona um indivíduo e gera um filho assexuado. **Atualização:** mantém os `tamanho_elite` melhores e seleciona os outros na população somada aos filhos, com repetição (slide 17) |
| Seleção | encaixe novo `(valores, quantidade) -> [índices]`, na raiz de `utils/`, porque não depende da representação: roleta, ranking, torneio e classes. Padrão: **roleta** nos pais e nos sobreviventes. A roleta usa `max(0, valor)`; com tudo zerado, o sorteio é uniforme |
| Inviabilidade | **reparo guloso, ligado**: `binaria.reparar` (Chu e Beasley, 1998) tira os itens de pior densidade até caber e completa pelos de melhor densidade. Roda em todo indivíduo novo. Na ordem, `reparo=None`, porque o decodificador já garante viabilidade. Avaliação padrão `binaria.avaliar`; sem reparo, use `binaria.avaliar_penalizada` |
| Cruzamento | binária: um ponto, multiponto e uniforme (padrão); ordem: OPX, LOX (sugerido) e PMX. Os pontos de corte e a máscara são opcionais (sorteados quando omitidos) e reproduzem os exemplos dos slides 25 a 32 |
| Mutação | reaproveita o encaixe do movimento: `binaria.gerar_vizinho` (padrão: k flips viáveis, o "um ponto" e "múltiplos pontos" do slide 34), `ordem.gerar_vizinho` (troca) e `ordem.perturbar` (perturbação). Novas na ordem: `ordem.mutacao_insercao` e `ordem.mutacao_inversao` (slides 35 e 36) |
| Parâmetros | `tamanho_populacao=50`, `max_geracoes=100`, `prob_cruzamento=0.8`, `prob_mutacao=0.05` (o "≤ 5%" dos slides 34 a 36), `intensidade_mutacao=1`, `tamanho_elite=2` |
| Busca local | opcional (`busca_local=None`), em cada indivíduo novo, depois do reparo (AG memético) |
| Parada | `max_geracoes` |
| Histórico | por geração, a partir da 0 (a população inicial), no formato do PSO: `valor_candidato` = média da população, `valor_atual` = melhor da população, `melhor_valor` = melhor de todos, `avaliacoes` (uma por indivíduo novo, mais a busca local; o reparo não conta) e o extra `distintos` (indivíduos diferentes na população), que mostra a perda de diversidade |
| Depurador | sem mudança: cada geração gera um passo "população", com todos os indivíduos no plano peso × valor, e a figura da geração |
| Reaproveitamento | movimentos como mutação, avaliações, construtivas, buscas locais, histórico, gráficos, experimento e depurador |

### Nomes das peças

| Encaixe | Raiz de `utils/` | Binária | Ordem |
|---|---|---|---|
| seleção `(valores, quantidade) -> [índices]` | `selecao_roleta`, `selecao_ranking`, `selecao_torneio` (`q=2`), `selecao_classes` (`melhores=0.2`, `piores=0.2`) | — | — |
| cruzamento `(pai1, pai2, itens, capacidade) -> (filho1, filho2)` | — | `cruzamento_um_ponto`, `cruzamento_multiponto`, `cruzamento_uniforme` | `cruzamento_opx`, `cruzamento_lox`, `cruzamento_pmx` |
| reparo `(solucao, itens, capacidade) -> solucao` | — | `reparar` | — |
| mutação (encaixe do movimento) | — | `gerar_vizinho` (já existia) | `mutacao_insercao`, `mutacao_inversao`; `gerar_vizinho` e `perturbar` (já existiam) |

## Escopo

- Esqueleto do AG com README de teoria (slides do Tema 11), a adaptação para a mochila, parâmetros, histórico e questões de revisão.
- Peças de seleção, cruzamento, reparo e mutação, exportadas pelos `__init__.py`.
- Testes de cada peça nova (com os exemplos dos slides) e do esquema.
- READMEs (raiz, conceitos e `utils/`) e notebook do laboratório atualizados.

## Fora do escopo

- Variantes que não estão nos slides: eliminação de duplicados, ranking não linear, probabilidades de cruzamento e mutação adaptativas.

## Critérios de aceite

- O AG aceita qualquer avaliação, construtiva, cruzamento, mutação, reparo, seleção e busca local compatíveis passados por parâmetro, sem editar o esquema.
- Com elitismo, o melhor da população nunca piora de uma geração para a outra, e o melhor indivíduo avaliado é guardado à parte (a elite sai da população atual, como no slide 9, então um filho melhor que todos pode não sobreviver).
- O histórico segue o formato comum, e `plotar_historico` funciona sem mudanças.
- `pytest` passa a partir da raiz, e os testes que já existiam não foram alterados.
- O notebook roda do começo ao fim sem erro.

## Próximos passos

- **AG:** eliminação de duplicados e probabilidades adaptativas.
- **PSO:** c1 e c2 adaptativos e topologias de vizinhança.
- **Path-Relinking na Busca Tabu:** `reconectar` e `atualizar_elite` já são independentes do esquema.
