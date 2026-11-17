import random

from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item


def mutacao_insercao(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int = 1,
    debug: Depurador | None = None,
) -> list[int]:
    """Draw two items and move the second right after the first, ``k`` times.

    Created for the Genetic Algorithm (mutation).

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices), left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every move shares one signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.
    k : int, default 1
        Number of insertions.
    debug : Depurador, optional
        When given, records the mutation as a debug step.

    Returns
    -------
    list of int
        New order.
    """
    nova = list(solucao)
    if len(nova) >= 2:
        for _ in range(k):
            a, b = random.sample(range(len(nova)), 2)
            primeiro = nova[a]
            segundo = nova.pop(b)
            nova.insert(nova.index(primeiro) + 1, segundo)
    if debug is not None:
        debug.passo("mutação", solucao, [("mutante", nova)], "mutante")
    return nova


def mutacao_inversao(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int = 1,
    debug: Depurador | None = None,
) -> list[int]:
    """Reverse the segment between two random points of the order, ``k`` times.

    Created for the Genetic Algorithm (mutation).

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices), left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every move shares one signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.
    k : int, default 1
        Number of inversions.
    debug : Depurador, optional
        When given, records the mutation as a debug step.

    Returns
    -------
    list of int
        New order.
    """
    nova = list(solucao)
    if len(nova) >= 2:
        for _ in range(k):
            i, j = sorted(random.sample(range(len(nova) + 1), 2))
            nova[i:j] = nova[i:j][::-1]
    if debug is not None:
        debug.passo("mutação", solucao, [("mutante", nova)], "mutante")
    return nova
