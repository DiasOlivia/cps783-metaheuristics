import random

from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item


def gerar_vizinho(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int = 1,
    debug: Depurador | None = None,
) -> list[int]:
    """Swap two random positions of a copy of the order, ``k`` times.

    Created for the SA in the order representation (move).

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every move shares one signature.
    k : int, default 1
        Number of swaps.
    debug : Depurador, optional
        When given, records the move as a debug step.

    Returns
    -------
    list of int
        New order.
    """
    nova = list(solucao)
    if len(nova) >= 2:
        for _ in range(k):
            i, j = random.sample(range(len(nova)), 2)
            nova[i], nova[j] = nova[j], nova[i]
    if debug is not None:
        debug.passo("movimento", solucao, [("vizinho", nova)], "vizinho")
    return nova
