import random

from metaheuristics.guloso.mochila import mochila_gulosa
from metaheuristics.utils.instancia import Item


def construtiva_aleatoria(itens: list[Item], capacidade: int) -> list[int]:
    """Build a random feasible solution: shuffle the items and insert what fits.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    list of int
        Feasible binary solution.
    """
    solucao = [0] * len(itens)
    indices = list(range(len(itens)))
    # Cada execução começa de um ponto diferente, sem depender da ordem da lista
    random.shuffle(indices)
    peso_atual = 0
    for i in indices:
        if peso_atual + itens[i].peso <= capacidade:
            solucao[i] = 1
            peso_atual += itens[i].peso
    return solucao


def construtiva_gulosa(itens: list[Item], capacidade: int) -> list[int]:
    """Build the greedy solution by non-increasing value-to-weight ratio.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    list of int
        Feasible binary solution.
    """
    return mochila_gulosa(
        [item.peso for item in itens],
        [item.valor for item in itens],
        capacidade,
        "densidade",
    )
