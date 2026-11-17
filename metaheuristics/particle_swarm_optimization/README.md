# Otimização por Enxame de Partículas (PSO)

> Material de estudo — **CPS783: Metaheurísticas em Otimização Combinatória (2026/3)**, Tema 10.

A **Otimização por Enxame de Partículas** (*Particle Swarm Optimization*, PSO) foi proposta em 1995 pelo psicólogo social **James Kennedy** e pelo engenheiro elétrico **Russell Eberhart**. Várias soluções candidatas, as **partículas**, coexistem e colaboram, "voando" pelo espaço de busca à procura do melhor lugar para "pousar". Cada partícula ajusta o seu voo pela **própria experiência** (cognição individual) e pela **experiência do grupo** (aprendizado social).

O PSO foi feito para espaços **contínuos**. Esta implementação segue os slides do Tema 10 (Profª Laura Bahiense) e o adapta à mochila 0-1, que é discreta. A adaptação (seção 5) é **desta implementação**.

## 1. Intuição (slides 2 a 12)

- **Wilson (1975):** estudando cardumes, o biólogo Edward O. Wilson concluiu que cada peixe aproveita as descobertas e a experiência dos outros na busca por comida. O compartilhamento social de informação dá uma vantagem evolutiva.
- **Reynolds (1986):** Craig Reynolds simulou bandos de pássaros (os *boids*, de *bird-oids*) para animações, com três leis: evitar colisões com os vizinhos, igualar a velocidade com eles e ficar perto deles.
- **Kennedy e Eberhart (1995):** juntaram um modelo **cognitivo** (a experiência individual) e um **social** (a do grupo).

A imagem do slide 10: os pássaros não sabem onde está a comida, mas sabem quão longe estão dela. A melhor estratégia é seguir o pássaro que está mais perto. Cada partícula se move comparando três coisas: a **posição atual**, a **sua melhor posição** até agora (pbest) e a **melhor posição do enxame** (gbest). O sucesso depende do equilíbrio entre explorar sozinha e aproveitar o que as outras encontraram (slide 12): pouca exploração individual leva à convergência prematura; pouco aprendizado social deixa o enxame sem encontrar uma boa solução.

## 2. Problema da mochila 0-1

Dados itens com pesos `peso_i`, valores `valor_i` e capacidade `C`:

\[
\max \sum_{i=1}^{n} valor_i x_i
\quad\text{sujeito a}\quad
\sum_{i=1}^{n} peso_i x_i \le C,\quad x_i\in\{0,1\}.
\]

## 3. Formulação (slides 13 a 17)

Um enxame de `P` partículas otimiza um espaço de `n` dimensões. A partícula `i` tem posição `xᵢ` e velocidade `vᵢ`, atualizadas em cada dimensão `j` por

\[
v_{ij}^{t+1} = w^t v_{ij}^t + c_1 r_1 \left(pbest_{ij} - x_{ij}^t\right) + c_2 r_2 \left(gbest_j - x_{ij}^t\right) \tag{1}
\]

\[
x_{ij}^{t+1} = x_{ij}^t + v_{ij}^{t+1}. \tag{2}
\]

| Termo | Papel | Kennedy e Eberhart | Artigos mais recentes | Sem ideia |
|---|---|---|---|---|
| `w` | **fator de inércia**: o peso da velocidade anterior | 1 | 0,5 | [0,5; 1,5] |
| `c1` | **autoconfiança**: atração pelo pbest (cognição individual) | 2 | 1,5 | [1,5; 2,5] |
| `c2` | **confiança no bando**: atração pelo gbest (aprendizado social) | 2 | 1,5 | [1,5; 2,5] |
| `r1`, `r2` | números aleatórios em (0, 1): mantêm a diversidade quando `c1` e `c2` são fixos | — | — | — |

- **vmax (slide 15):** a velocidade costuma crescer demais ao longo da busca, então ela é limitada a `[−vmax, vmax]`, em geral com `vmax = 4` ou `5`.
- **Inércia (slide 16):** `w` alto favorece buscas abrangentes (diversificação), e `w` baixo, o refinamento (intensificação).
- **`c1` × `c2` (slide 17):** com `c1 ≫ c2`, o modelo é cognitivo demais, e o enxame aproveita pouco o que as outras partículas acharam; com `c1 ≪ c2`, é social demais, e converge cedo para um ótimo local.

Aqui `r1` e `r2` são sorteados por dimensão, como é comum nas implementações.

## 4. Algoritmo básico (slide 18)

Para maximização (o slide está escrito para minimização):

```text
para cada partícula i:
    xᵢ <- posição inicial;  vᵢ <- velocidade aleatória em [−vmax, vmax]
    pbestᵢ <- xᵢ
gbest <- a melhor das partículas

para t = 1, …, max_iteracoes:
    para cada partícula i:
        atualizar vᵢ pela equação (1), limitada a vmax
        xᵢ <- voo(xᵢ, vᵢ)
        se f(xᵢ) > f(pbestᵢ):  pbestᵢ <- xᵢ
        se f(xᵢ) > f(gbest):   gbest <- xᵢ
retornar gbest
```

Como no slide, o pbest e o gbest são atualizados logo depois do voo de cada partícula, e as partículas seguintes já usam o gbest novo.

## 5. Adaptação para a mochila

A equação (2) supõe posições contínuas. Na mochila, a velocidade continua sendo a da equação (1), por item, e cada representação define dois encaixes: as **coordenadas** (os números que entram na equação 1) e o **voo** (como a velocidade muda a solução). Nas duas, a posição de cada partícula é uma solução comum, então as construtivas, as buscas locais, o depurador e os gráficos do repositório funcionam sem mudança.

| Representação | Coordenadas | Voo | `vmax = 4` significa |
|---|---|---|---|
| Binária: **PSO binário** (Kennedy e Eberhart, 1997) | os bits (`binaria.coordenadas`) | cada bit vira 1 com probabilidade `sigmoide(v) = 1/(1 + e^{−v})` (`binaria.mover_sigmoide`) | a chance de um bit ser 1 fica entre 1,8% e 98,2%: sempre resta alguma chance de mudar |
| Por ordem: **chaves por posição** | a posição de cada item na ordem, de `n` (o primeiro) a `1` (o último) (`ordem.coordenadas`) | soma `v` às chaves e reordena por elas (`ordem.mover_chaves`) | um item anda até 4 posições por iteração |

No PSO binário a velocidade não é um deslocamento, e sim a **tendência** do bit a ser 1. A nova posição depende só da velocidade, e a velocidade guarda a atração pelo pbest e pelo gbest: se o bit do gbest é 1 e o da partícula é 0, `gbest − x = 1` empurra `v` para cima. O limite `vmax = 4` é coerente com o "4 ou 5" do slide 15: sem ele, a sigmoide saturaria em 0 ou 1, e o bit ficaria congelado.

**Inviabilidade.** O voo binário sorteia bits sem olhar a capacidade, e muitas partículas passam do peso. A avaliação padrão é a `binaria.avaliar_penalizada` da Busca Tabu: uma solução que não cabe vale no máximo 0. Como o enxame começa viável (`construtiva=binaria.construtiva_aleatoria`, a inicialização aleatória do slide 18), o pbest e o gbest são sempre viáveis. Na ordem, toda solução é viável.

## 6. Por que os parâmetros de Kennedy e Eberhart

Os padrões aqui são os de Kennedy e Eberhart (`w = 1`, `c1 = c2 = 2`), e não os dos artigos mais recentes (`0,5; 1,5; 1,5`). Os valores recentes foram calibrados para o PSO contínuo; na mochila, `w = 0,5` encolhe as velocidades, e então as probabilidades da sigmoide ficam perto de 50% (binária) ou os itens quase não se deslocam (ordem). O voo vira quase um sorteio. Com 50 itens, 30 partículas, 200 iterações e 10 sementes:

| Instância | Kennedy e Eberhart (1; 2; 2) | Recentes (0,5; 1,5; 1,5) |
|---|---|---|
| Comum, binária | 0,52% de gap | 11,53% |
| Correlacionada, binária | 0,84% | 2,65% |
| Comum, por ordem (5 sementes) | 4,90% | 8,99% |
| Correlacionada, por ordem (5 sementes) | 0,91% | 1,04% |

Na instância de referência (20 itens, 20 partículas, 100 iterações), os parâmetros de Kennedy e Eberhart chegam ao ótimo nas 10 sementes, e os recentes ficam em 5,63%.

## 7. Extensões

- **Inércia decrescente**, **implementada:** `inercia=(inicial, final)` faz `wᵗ` cair linearmente da primeira à última iteração. É a ideia do slide 16 (diversificar no começo e intensificar no fim), e o `wᵗ` da equação (1) deixa isso explícito. Na mochila, porém, ela piora o resultado pelo mesmo motivo da seção 6: com `(1, 0,4)`, o gap vai a 4,43% na instância comum e 2,30% na correlacionada, porque a inércia baixa no fim torna o voo aleatório.
- **Busca local**, **implementada:** `busca_local` é aplicada à partícula que **melhora o próprio pbest** (um PSO "memético"). Ela não roda em toda partícula porque, no PSO binário, a partícula pode estar inviável, e as buscas locais binárias exigem solução viável; o pbest é sempre viável. Com a `binaria.busca_local_primeira_melhora`, o gap cai para 0,41% na instância comum e 0,45% na correlacionada, com 13 a 21 vezes mais avaliações.
- **`c1` e `c2` adaptativos**, **fora:** o slide 15 sugere atualizá-los por estatísticas da busca, no estilo da ALNS, mas não diz quais.

## 8. Parâmetros

| Parâmetro | Papel | Padrão | Fonte |
|---|---|---|---|
| `tamanho_enxame` | número de partículas `P` | 20 | slide 13 |
| `max_iteracoes` | critério de parada | 100 | slide 18 |
| `inercia` | `w`, fixo ou `(inicial, final)` | 1 | slides 14 e 16 |
| `c1`, `c2` | autoconfiança e confiança no bando | 2 e 2 | slides 14 e 17 |
| `vmax` | limite da velocidade; as iniciais são sorteadas em `[−vmax, vmax]` | 4 | slide 15 |
| `avaliar` | avaliação | `binaria.avaliar_penalizada` | slide 23 do Tema 8 |
| `construtiva`, `coordenadas`, `mover`, `busca_local`, `debug` | as peças | binárias; sem busca local | [`utils/`](../utils/README.md) |

## 9. Histórico

`particle_swarm_optimization_mochila` devolve `(gbest, historico)`, no formato comum a todos os esquemas, com a iteração 0 sendo o enxame inicial:

- `valor_candidato`: a **média do enxame** na iteração;
- `valor_atual`: a **melhor partícula da iteração**;
- `melhor_valor`: o valor do gbest;
- `avaliacoes`: uma por partícula e por iteração, mais as da busca local;
- `inercia`: o `wᵗ` da iteração (a partir da 1), que o `plotar_historico` mostra no painel de baixo.

No `Depurador`, cada iteração gera a figura **enxame**, com todas as partículas no plano peso × valor em relação ao gbest do começo da iteração (as que não cabem aparecem com ×), e a da iteração.

## 10. O que os experimentos mostram

Na linha de base do notebook (instância correlacionada de 50 itens, 30 partículas, 200 iterações, 10 sementes), o PSO fica em 0,84% de gap médio, chega ao ótimo em 2 sementes e usa cerca de 6 mil avaliações, um esforço parecido com o do SA (3,37%). Fica atrás da ALNS e do GRASP, que chegam ao ótimo nas 10 sementes. O PSO binário não tem nenhuma noção de vizinhança: a partícula não "anda" para uma solução parecida, ela sorteia uma nova, guiada pelas probabilidades. A busca local no pbest compensa isso em parte.

## 11. Exemplo

```python
import random

from metaheuristics.particle_swarm_optimization import (
    particle_swarm_optimization_mochila,
)
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

random.seed(0)
itens = gerar_instancia_aleatoria(20, 20, 100)
capacidade = sum(item.peso for item in itens) // 2
otimo, _ = programacao_dinamica(itens, capacidade)
random.seed(1)
gbest, historico = particle_swarm_optimization_mochila(itens, capacidade)
print(f"Ótimo: {otimo} | PSO: {historico['melhor_valor'][100]}")
plotar_historico(historico, otimo, eixo_x="iteracao", save=True)
```

Para a representação por ordem, troque as peças:

```python
particle_swarm_optimization_mochila(
    itens,
    capacidade,
    avaliar=ordem.avaliar,
    construtiva=ordem.construtiva_aleatoria,
    coordenadas=ordem.coordenadas,
    mover=ordem.mover_chaves,
)
```

## 12. Executar

Na raiz do repositório:

```bash
pytest tests/particle_swarm_optimization
```

O teste da instância de referência usa a mesma instância de 20 itens e semente 0 dos outros esquemas e exige `gap <= 5%`, um critério do teste, não uma garantia do PSO. Mude `PLOT = False` para `True` para salvar o gráfico.

## 13. Questões para revisão

1. Como funciona o PSO em linhas gerais? Quais são seus elementos e parâmetros?
2. Qual é a função da cognição individual? E do aprendizado social?
3. O que acontece quando a cognição individual é baixa? E quando o aprendizado social é baixo?
4. Quais são as fórmulas de atualização da posição e da velocidade, e qual é o papel de cada termo da velocidade?
5. Qual é a importância do fator de inércia? O que acontece quando ele é baixo? E quando é alto?
6. Por que o PSO precisa de adaptação para a mochila? Como a sigmoide transforma velocidade em decisão?
7. Por que os parâmetros recentes funcionam mal no PSO binário?

## 14. Referências

- Bahiense, L. *Metaheurísticas em Otimização Combinatória — Tema 10: Enxame de Partículas (PSO)*. Material didático.
- Kennedy, J.; Eberhart, R. (1995). *Particle Swarm Optimization*. **IEEE International Conference on Neural Networks**, Perth, IV, 1942–1948.
- Kennedy, J.; Eberhart, R. C. (1997). *A discrete binary version of the particle swarm algorithm*. **IEEE International Conference on Systems, Man, and Cybernetics**, 5, 4104–4108.
- Kennedy, J. (1997). *The Particle Swarm: Social Adaptation of Knowledge*. **International Conference on Evolutionary Computation**, 303–308.
- Eberhart, R. C.; Shi, Y. (1998). *Comparison between genetic algorithms and particle swarm optimization*. **Evolutionary Programming VII**. Springer.
- Shi, Y.; Eberhart, R. C. (1998). *Parameter selection in particle swarm optimization*. **Evolutionary Programming VII**, 591–600. Springer.
- Eberhart, R. C.; Shi, Y. (2001). *Particle swarm optimization: developments, applications and resources*. **Congress on Evolutionary Computation**, Seoul.
- Reynolds, C. W. (1987). *Flocks, herds and schools: A distributed behavioral model*. **Computer Graphics (SIGGRAPH '87)**, 21(4), 25–34.
- Wilson, E. O. (1975). **Sociobiology: The New Synthesis**. Harvard University Press.
