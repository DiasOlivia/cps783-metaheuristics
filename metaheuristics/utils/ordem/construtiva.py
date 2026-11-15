import random

from metaheuristics.utils.binaria.construtiva import Vies
from metaheuristics.utils.binaria.construtiva import _sequencia_gulosa_aleatoria
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


def construtiva_gulosa_aleatoria(
    itens: list[Item], capacidade: int, alfa: float = 0.3, vies: Vies = "aleatoria"
) -> list[int]:
    """Build an order by the greedy randomized construction of GRASP.

    The items chosen by ``binaria.construtiva_gulosa_aleatoria`` come first, in
    the order they were chosen, followed by the others by non-increasing density.
    With the same random state, both decode to the same solution.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    alfa : float, default 0.3
        RCL quality parameter, in ``[0, 1]``.
    vies : str or callable, default 'aleatoria'
        Bias of the draw in the RCL, as in ``binaria.construtiva_gulosa_aleatoria``.

    Returns
    -------
    list of int
        Permutation of the item indices.
    """
    escolhidos = _sequencia_gulosa_aleatoria(itens, capacidade, alfa, vies)
    resto = set(range(len(itens))) - set(escolhidos)
    return escolhidos + sorted(
        resto, key=lambda j: (-itens[j].valor / itens[j].peso, j)
    )
