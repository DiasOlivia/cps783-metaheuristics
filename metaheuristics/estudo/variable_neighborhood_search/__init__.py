"""Basic Variable Neighborhood Search (VNS) for the 0-1 knapsack problem."""

from collections.abc import Callable

from metaheuristics.utils import binaria
from metaheuristics.utils.aceitacao import aceita_melhora
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item


def variable_neighborhood_search_mochila(
    itens: list[Item],
    capacidade: int,
    max_iteracoes: int = 250,
    k_max: int = 4,
    avaliar: Callable = binaria.avaliar,
    construtiva: Callable = binaria.construtiva_aleatoria,
    busca_local: Callable | None = binaria.busca_local_melhor_melhora,
    perturbacao: Callable = binaria.perturbar,
    aceitacao: Callable = aceita_melhora,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Solve the 0-1 knapsack problem using Basic VNS (BVNS).

    Each trial shakes the current solution in neighborhood ``N_k`` (the
    perturbation with strength ``k``), improves it by local search and decides
    with ``aceitacao``. An accepted candidate resets ``k`` to 1; otherwise ``k``
    grows, restarting at 1 after ``k_max``. The initial solution does not go
    through local search. ``max_iteracoes`` counts trials, not full cycles.

    Parameters
    ----------
    itens : list of Item
        Items of the instance (positive integer weights, non-negative values).
    capacidade : int
        Knapsack capacity (non-negative integer).
    max_iteracoes : int, default 250
        Number of shaking/local-search trials; zero is allowed.
    k_max : int, default 4
        Maximum shaking strength, between 1 and the number of items.
    avaliar : callable, default binaria.avaliar
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_aleatoria
        Initial solution, ``(itens, capacidade) -> solucao``.
    busca_local : callable or None, default binaria.busca_local_melhor_melhora
        ``(solucao, itens, capacidade, debug) -> (solucao, avaliacoes)``; None
        skips the local search.
    perturbacao : callable, default binaria.perturbar
        Shaking, ``(solucao, itens, capacidade, k, debug) -> solucao``.
    aceitacao : callable, default aceita_melhora
        Acceptance rule ``(delta, iteracao) -> bool``.
    debug : Depurador, optional
        Draws one figure per step.

    Returns
    -------
    melhor_solucao : list of int
        Best solution found, in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        ``valor_candidato``, ``valor_atual``, ``melhor_valor``, ``avaliacoes`` and
        ``k`` per trial; iteration 0 is the initial solution, with ``k=0``.
    """
    if not isinstance(capacidade, int) or capacidade < 0:
        raise ValueError("A capacidade deve ser um inteiro não negativo.")
    if not isinstance(max_iteracoes, int) or max_iteracoes < 0:
        raise ValueError("max_iteracoes deve ser inteiro não negativo.")
    if not isinstance(k_max, int) or k_max < 1 or (itens and k_max > len(itens)):
        raise ValueError("k_max deve estar entre 1 e o número de itens.")
    if any(
        not isinstance(item.peso, int)
        or item.peso <= 0
        or not isinstance(item.valor, int)
        or item.valor < 0
        for item in itens
    ):
        raise ValueError(
            "Pesos devem ser positivos e valores não negativos, ambos inteiros."
        )

    if debug is not None:
        debug.inicio_iteracao("VNS", 0, ultima=max_iteracoes == 0)
    atual = construtiva(itens, capacidade)
    valor_atual = avaliar(atual, itens, capacidade)
    avaliacoes = 1
    melhor_solucao, melhor_valor = list(atual), valor_atual
    historico = novo_historico()
    registrar(
        historico,
        0,
        valor_candidato=valor_atual,
        valor_atual=valor_atual,
        melhor_valor=melhor_valor,
        avaliacoes=avaliacoes,
        k=0,
    )
    if debug is not None:
        debug.fim_iteracao(
            atual,
            atual,
            valor_atual,
            True,
            valor_atual,
            melhor_valor,
            extras={"k": 0},
        )

    k = 1
    for iteracao in range(1, max_iteracoes + 1):
        if debug is not None:
            debug.inicio_iteracao("VNS", iteracao, ultima=iteracao == max_iteracoes)
        if not itens:
            candidato, valor_candidato, k_usado = [], 0, 0
        else:
            k_usado = k
            candidato = perturbacao(atual, itens, capacidade, k, debug=debug)
            if busca_local is not None:
                candidato, examinadas = busca_local(
                    candidato, itens, capacidade, debug=debug
                )
                avaliacoes += examinadas
            valor_candidato = avaliar(candidato, itens, capacidade)
            avaliacoes += 1
        anterior = atual
        aceito = aceitacao(valor_candidato - valor_atual, iteracao)
        if aceito:
            atual, valor_atual = candidato, valor_candidato
            k = 1
        elif itens:
            k = k + 1 if k < k_max else 1
        if valor_atual > melhor_valor:
            melhor_solucao, melhor_valor = list(atual), valor_atual
        registrar(
            historico,
            iteracao,
            valor_candidato=valor_candidato,
            valor_atual=valor_atual,
            melhor_valor=melhor_valor,
            avaliacoes=avaliacoes,
            k=k_usado,
        )
        if debug is not None:
            debug.fim_iteracao(
                anterior,
                candidato,
                valor_candidato,
                aceito,
                valor_atual,
                melhor_valor,
                extras={"k": k_usado},
                info=getattr(aceitacao, "ultimo", None),
            )
    return melhor_solucao, historico
