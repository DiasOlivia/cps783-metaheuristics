"""Ant Colony Optimization (ACO) for the 0-1 knapsack problem."""

import statistics
from collections.abc import Callable

from metaheuristics.utils import binaria
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.feromonio import Feromonio
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item

DEPOSITOS = ("todas", "elitista", "ranking", "melhor")


def ant_colony_optimization_mochila(
    itens: list[Item],
    capacidade: int,
    numero_formigas: int = 20,
    max_sem_melhora: int = 100,
    alfa: float = 1.0,
    beta: float = 1.0,
    evaporacao: float = 0.5,
    feromonio_inicial: float = 1.0,
    deposito: str = "todas",
    peso_elite: float = 5.0,
    w: int = 6,
    q0: float = 0.0,
    atualizacao_local: float = 0.0,
    avaliar: Callable = binaria.avaliar,
    construtiva: Callable = binaria.construtiva_formiga,
    trilha: Callable = binaria.trilha,
    busca_local: Callable | None = None,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Solve the 0-1 knapsack problem with Ant Colony Optimization.

    At each iteration, every ant builds a solution with ``construtiva``, guided
    by the pheromone ``τ`` and by the value-to-weight ratio ``η``. Then the
    pheromone is updated on the components given by ``trilha``: an ant with
    solution ``S`` deposits ``Δτ = valor(S) / valor da gulosa``, so a solution as
    good as the greedy one deposits about ``τ0``. The search stops after
    ``max_sem_melhora`` iterations without improving the best solution.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    numero_formigas : int, default 20
        Ants per iteration.
    max_sem_melhora : int, default 100
        Iterations without improving the best solution before stopping.
    alfa : float, default 1.0
        Weight ``α`` of the pheromone in the transition rule.
    beta : float, default 1.0
        Weight ``β`` of the heuristic information.
    evaporacao : float, default 0.5
        Evaporation rate ``ρ``, in ``(0, 1]``.
    feromonio_inicial : float, default 1.0
        Initial pheromone ``τ0`` of every component.
    deposito : {'todas', 'elitista', 'ranking', 'melhor'}, default 'todas'
        Pheromone update. ``'todas'`` is the Ant System: everything evaporates
        and every ant deposits. ``'elitista'`` (EAS) adds ``peso_elite`` times
        the deposit of the best-so-far solution. ``'ranking'`` (ASrank): only the
        ``w - 1`` best ants of the iteration deposit, the one ranked ``r`` with
        weight ``w - r``, plus ``w`` times the best-so-far. ``'melhor'`` (ACS):
        only the components of the best-so-far change,
        ``τ = (1 - ρ) τ + ρ Δτ_bs``.
    peso_elite : float, default 5.0
        Weight ``e`` of the best-so-far deposit in the EAS.
    w : int, default 6
        Ranks of the ASrank, at least 2.
    q0 : float, default 0.0
        Chance that an ant takes the best item instead of drawing one (ACS).
    atualizacao_local : float, default 0.0
        Rate ``ξ`` of the local update ``τ = (1 - ξ) τ + ξ τ0``, applied to the
        components of each ant right after it builds (ACS); 0 turns it off.
    avaliar : callable, default binaria.avaliar
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_formiga
        One ant, ``(itens, capacidade, feromonio, alfa, beta, q0) -> solucao``.
    trilha : callable, default binaria.trilha
        Components of a solution, ``(solucao, itens, capacidade) -> [chaves]``.
    busca_local : callable, optional
        Applied to each ant before the deposit,
        ``(solucao, itens, capacidade, debug) -> (solucao, avaliacoes)``.
    debug : Depurador, optional
        Draws the ants and the result of each iteration.

    Returns
    -------
    melhor_solucao : list of int
        Best solution found, in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        Per iteration, from 1: ``valor_candidato`` (mean value of the ants),
        ``valor_atual`` (best ant of the iteration), ``melhor_valor``,
        ``avaliacoes`` and ``distintos`` (number of different solutions built).
    """
    if numero_formigas < 1 or max_sem_melhora < 1:
        raise ValueError("numero_formigas e max_sem_melhora devem ser >= 1.")
    if not 0 < evaporacao <= 1 or not 0 <= atualizacao_local < 1:
        raise ValueError("evaporacao em (0, 1] e atualizacao_local em [0, 1).")
    if min(alfa, beta) < 0 or not 0 <= q0 <= 1 or feromonio_inicial <= 0:
        raise ValueError("alfa, beta >= 0, q0 em [0, 1] e feromonio_inicial > 0.")
    if deposito not in DEPOSITOS or w < 2:
        raise ValueError(f"deposito deve ser um de {DEPOSITOS}, e w >= 2.")

    gulosa = binaria.construtiva_gulosa(itens, capacidade)
    referencia = binaria.avaliar(gulosa, itens, capacidade) or 1
    feromonio = Feromonio(feromonio_inicial)
    melhor_solucao, melhor_valor = None, None
    avaliacoes = 0
    historico = novo_historico()

    def depositar(solucao: list[int], valor: float, peso: float = 1.0) -> None:
        for componente in trilha(solucao, itens, capacidade):
            feromonio[componente] += peso * valor / referencia

    def aproximar(solucao: list[int], taxa: float, alvo: float) -> None:
        # Forma comum da atualização global do ACS e da local: τ = (1 - taxa) τ + taxa alvo
        for componente in trilha(solucao, itens, capacidade):
            feromonio[componente] = (1 - taxa) * feromonio[componente] + taxa * alvo

    iteracao = ultima_melhora = 0
    while melhor_valor is None or iteracao - ultima_melhora < max_sem_melhora:
        iteracao += 1
        if debug is not None:
            debug.inicio_iteracao("ACO", iteracao)
        melhor_anterior = melhor_solucao
        formigas = []
        for _ in range(numero_formigas):
            solucao = construtiva(itens, capacidade, feromonio, alfa, beta, q0)
            if atualizacao_local:
                aproximar(solucao, atualizacao_local, feromonio_inicial)
            if busca_local is not None:
                solucao, examinadas = busca_local(
                    solucao, itens, capacidade, debug=debug
                )
                avaliacoes += examinadas
            valor = avaliar(solucao, itens, capacidade)
            avaliacoes += 1
            formigas.append((valor, solucao))
            if melhor_valor is None or valor > melhor_valor:
                melhor_solucao, melhor_valor = list(solucao), valor
                ultima_melhora = iteracao

        if deposito == "melhor":
            aproximar(melhor_solucao, evaporacao, melhor_valor / referencia)
        else:
            feromonio.evaporar(evaporacao)
            if deposito == "ranking":
                ordenadas = sorted(formigas, key=lambda formiga: -formiga[0])
                for r, (valor, solucao) in enumerate(ordenadas[: w - 1], start=1):
                    depositar(solucao, valor, w - r)
                depositar(melhor_solucao, melhor_valor, w)
            else:
                for valor, solucao in formigas:
                    depositar(solucao, valor)
                if deposito == "elitista":
                    depositar(melhor_solucao, melhor_valor, peso_elite)

        valores = [valor for valor, _ in formigas]
        distintos = len({tuple(solucao) for _, solucao in formigas})
        registrar(
            historico,
            iteracao,
            valor_candidato=statistics.mean(valores),
            valor_atual=max(valores),
            melhor_valor=melhor_valor,
            avaliacoes=avaliacoes,
            distintos=distintos,
        )
        if debug is not None:
            lider = valores.index(max(valores))
            origem = melhor_solucao if melhor_anterior is None else melhor_anterior
            debug.passo(
                "formigas",
                origem,
                [(f"f{k + 1}", solucao) for k, (_, solucao) in enumerate(formigas)],
                f"f{lider + 1}",
            )
            debug.fim_iteracao(
                origem,
                formigas[lider][1],
                valores[lider],
                True,
                valores[lider],
                melhor_valor,
                extras={"distintos": distintos},
            )
    return melhor_solucao, historico
