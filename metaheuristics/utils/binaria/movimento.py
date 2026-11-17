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
    """Apply ``k`` successive feasible one-bit flips to a copy of the solution.

    Created for the SA (move).

    Each flip draws a random position: a selected item is removed, and an
    unselected item is added only if it fits; otherwise another position is drawn.
    The same position may be drawn in two flips, so the final distance can be
    smaller than ``k``.

    Parameters
    ----------
    solucao : list of int
        Feasible binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    k : int, default 1
        Number of flips.
    debug : Depurador, optional
        When given, records the move as a debug step.

    Returns
    -------
    list of int
        Feasible neighbor.
    """
    vizinho = list(solucao)
    peso = sum(item.peso for item, bit in zip(itens, vizinho) if bit)
    for _ in range(k):
        if not any(vizinho) and all(item.peso > capacidade for item in itens):
            raise ValueError("Nenhum item cabe na mochila: não há vizinho viável.")
        while True:
            idx = random.randint(0, len(itens) - 1)
            if vizinho[idx]:
                vizinho[idx] = 0
                peso -= itens[idx].peso
                break
            if peso + itens[idx].peso <= capacidade:
                vizinho[idx] = 1
                peso += itens[idx].peso
                break
    if debug is not None:
        debug.passo("movimento", solucao, [("vizinho", vizinho)], "vizinho")
    return vizinho
