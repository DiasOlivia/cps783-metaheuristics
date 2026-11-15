"""Iterated Local Search (ILS) for the 0-1 knapsack problem."""

from collections.abc import Callable

from metaheuristics.utils import binaria
from metaheuristics.utils.aceitacao import aceita_melhora
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item


def iterated_local_search_mochila(
    itens: list[Item],
    capacidade: int,
    max_iteracoes: int,
    intensidade_perturbacao: int = 3,
    avaliar: Callable = binaria.avaliar,
    construtiva: Callable = binaria.construtiva_aleatoria,
    busca_local: Callable | None = binaria.busca_local_melhor_melhora,
    perturbacao: Callable = binaria.perturbar,
    aceitacao: Callable = aceita_melhora,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Optimize the 0-1 knapsack problem by Iterated Local Search (ILS).

    Starting from a constructed solution improved by local search, each cycle
    perturbs the current local optimum, improves it again by local search and
    decides with ``aceitacao`` whether it becomes the current solution. The best
    solution is tracked separately. The default pieces are the binary ones.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    max_iteracoes : int
        Number of ILS cycles (non-negative).
    intensidade_perturbacao : int, default 3
        The ``k`` passed to the perturbation.
    avaliar : callable, default binaria.avaliar
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_aleatoria
        Initial solution, ``(itens, capacidade) -> solucao``.
    busca_local : callable or None, default binaria.busca_local_melhor_melhora
        ``(solucao, itens, capacidade, debug) -> (solucao, avaliacoes)``; None
        skips the local search.
    perturbacao : callable, default binaria.perturbar
        ``(solucao, itens, capacidade, k, debug) -> solucao``.
    aceitacao : callable, default aceita_melhora
        Acceptance rule ``(delta, iteracao) -> bool``.
    debug : Depurador, optional
        Draws one figure per step.

    Returns
    -------
    melhor_solucao : list of int
        Best solution found, in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        ``valor_candidato``, ``valor_atual``, ``melhor_valor`` and ``avaliacoes``
        per cycle; iteration 0 is the initial local optimum.
    """
    if capacidade < 0 or max_iteracoes < 0:
        raise ValueError("Capacidade e iterações não podem ser negativas.")
    if any(item.peso <= 0 or item.valor < 0 for item in itens):
        raise ValueError("Itens devem ter peso positivo e valor não negativo.")
    if not itens and max_iteracoes > 0:
        raise ValueError("É necessário ao menos um item para perturbar.")
    if itens and not 1 <= intensidade_perturbacao <= len(itens):
        raise ValueError("Intensidade inválida para a quantidade de itens.")

    if debug is not None:
        debug.inicio_iteracao("ILS", 0, ultima=max_iteracoes == 0)
    inicial = construtiva(itens, capacidade)
    avaliacoes = 0
    atual = inicial
    if busca_local is not None:
        atual, avaliacoes = busca_local(inicial, itens, capacidade, debug=debug)
    valor_atual = avaliar(atual, itens, capacidade)
    avaliacoes += 1
    melhor_solucao, melhor_valor = list(atual), valor_atual
    historico = novo_historico()
    registrar(
        historico,
        0,
        valor_candidato=valor_atual,
        valor_atual=valor_atual,
        melhor_valor=melhor_valor,
        avaliacoes=avaliacoes,
    )
    if debug is not None:
        debug.fim_iteracao(
            inicial, atual, valor_atual, True, valor_atual, melhor_valor
        )

    for iteracao in range(1, max_iteracoes + 1):
        if debug is not None:
            debug.inicio_iteracao("ILS", iteracao, ultima=iteracao == max_iteracoes)
        candidato = perturbacao(
            atual, itens, capacidade, intensidade_perturbacao, debug=debug
        )
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
        if valor_atual > melhor_valor:
            melhor_solucao, melhor_valor = list(atual), valor_atual
        registrar(
            historico,
            iteracao,
            valor_candidato=valor_candidato,
            valor_atual=valor_atual,
            melhor_valor=melhor_valor,
            avaliacoes=avaliacoes,
        )
        if debug is not None:
            debug.fim_iteracao(
                anterior,
                candidato,
                valor_candidato,
                aceito,
                valor_atual,
                melhor_valor,
                info=getattr(aceitacao, "ultimo", None),
            )
    return melhor_solucao, historico
