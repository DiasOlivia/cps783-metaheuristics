import random
from collections.abc import Callable
from collections.abc import Hashable

from metaheuristics.utils.feromonio import Feromonio
from metaheuristics.utils.instancia import Item


def _sequencia_formiga(
    itens: list[Item],
    capacidade: int,
    feromonio: Feromonio | None,
    alfa: float,
    beta: float,
    q0: float,
    componente: Callable[[int | None, int], Hashable],
) -> list[int]:
    """Return the items chosen, in order, by one ant.

    At each step the candidates are the items that still fit, and the ant goes
    from the last chosen item (``None`` at the start) to the next one through the
    component ``componente(anterior, j)``.
    """
    escolhidos = []
    usados = set()
    peso = 0
    anterior = None
    while True:
        candidatos = [
            j
            for j, item in enumerate(itens)
            if j not in usados and peso + item.peso <= capacidade
        ]
        if not candidatos:
            return escolhidos
        tau = [
            1.0 if feromonio is None else feromonio[componente(anterior, j)]
            for j in candidatos
        ]
        eta = [itens[j].valor / itens[j].peso for j in candidatos]
        if q0 and random.random() < q0:
            # Regra pseudoaleatória (slide 33): o maior τ·η^β, sem sorteio
            notas = [t * e**beta for t, e in zip(tau, eta)]
            escolhido = candidatos[notas.index(max(notas))]
        else:
            pesos = [t**alfa * e**beta for t, e in zip(tau, eta)]
            escolhido = random.choices(
                candidatos, weights=pesos if any(pesos) else None
            )[0]
        escolhidos.append(escolhido)
        usados.add(escolhido)
        peso += itens[escolhido].peso
        anterior = escolhido


def construtiva_formiga(
    itens: list[Item],
    capacidade: int,
    feromonio: Feromonio | None = None,
    alfa: float = 1.0,
    beta: float = 1.0,
    q0: float = 0.0,
) -> list[int]:
    """Build a solution the way an ant does, with pheromone per item.

    Created for the ACO (ant construction).

    While some item fits, the ant draws the next one among those that fit with
    probability ``τ_j^α η_j^β / Σ τ_l^α η_l^β``, where ``τ_j`` is the pheromone
    of item ``j`` and ``η_j`` its value-to-weight ratio (the heuristic
    information). With probability ``q0`` it takes the item with the largest
    ``τ_j η_j^β`` instead (the pseudorandom proportional rule of the ACS).

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    feromonio : Feromonio, optional
        Pheromone of each item; without it, ``τ = 1`` for every item, and the
        construction is a randomized greedy by value-to-weight ratio.
    alfa : float, default 1.0
        Weight ``α`` of the pheromone.
    beta : float, default 1.0
        Weight ``β`` of the heuristic information.
    q0 : float, default 0.0
        Chance of choosing the best item instead of drawing one.

    Returns
    -------
    list of int
        Feasible binary solution where no item outside fits anymore.
    """
    solucao = [0] * len(itens)
    for j in _sequencia_formiga(
        itens, capacidade, feromonio, alfa, beta, q0, lambda anterior, j: j
    ):
        solucao[j] = 1
    return solucao


def trilha(solucao: list[int], itens: list[Item], capacidade: int) -> list[int]:
    """Return the components of a binary solution: the items in the knapsack.

    Created for the ACO (pheromone deposit).

    Parameters
    ----------
    solucao : list of int
        Binary solution.
    itens : list of Item
        Items of the instance; unused, kept so every trail shares one signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.

    Returns
    -------
    list of int
        Indices of the selected items, where the ant deposits pheromone.
    """
    return [j for j, bit in enumerate(solucao) if bit]
