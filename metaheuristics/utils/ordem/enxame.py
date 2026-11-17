from metaheuristics.utils.instancia import Item


def coordenadas(
    solucao: list[int], itens: list[Item], capacidade: int
) -> list[float]:
    """Return the position of an order particle: one key per item.

    Created for the PSO (particle position).

    The key of an item is its place in the order, counted from the end: ``n`` for
    the first item and ``1`` for the last, so a higher key means earlier.

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices).
    itens : list of Item
        Items of the instance; unused, kept so every coordinate map shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.

    Returns
    -------
    list of float
        Key of each item, indexed by item.
    """
    n = len(solucao)
    chaves = [0.0] * n
    for posicao, item in enumerate(solucao):
        chaves[item] = float(n - posicao)
    return chaves


def mover_chaves(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    velocidade: list[float],
) -> list[int]:
    """Fly an order particle: add the velocity to the keys and sort by them.

    Created for the PSO (flight).

    A velocity of ``+3`` moves an item about three places towards the front
    (random keys). Ties keep the current order.

    Parameters
    ----------
    solucao : list of int
        Current order, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    velocidade : list of float
        Velocity of each item, indexed by item.

    Returns
    -------
    list of int
        New order.
    """
    chaves = coordenadas(solucao, itens, capacidade)
    novas = [chave + v for chave, v in zip(chaves, velocidade)]
    return sorted(solucao, key=lambda item: -novas[item])
