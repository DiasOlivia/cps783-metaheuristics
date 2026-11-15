import random

from metaheuristics.utils.instancia import Item


def construtiva_aleatoria(itens: list[Item], capacidade: int) -> list[int]:
    """Return a random permutation of the item indices.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every constructive shares one signature.

    Returns
    -------
    list of int
        Shuffled item indices.
    """
    ordem = list(range(len(itens)))
    random.shuffle(ordem)
    return ordem


def construtiva_gulosa(itens: list[Item], capacidade: int) -> list[int]:
    """Return the item indices by non-increasing value-to-weight ratio.

    Decoding this order gives the greedy-by-density solution.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every constructive shares one signature.

    Returns
    -------
    list of int
        Item indices sorted by density, ties keeping the original order.
    """
    return sorted(range(len(itens)), key=lambda j: -itens[j].valor / itens[j].peso)
