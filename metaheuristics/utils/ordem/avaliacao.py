from metaheuristics.utils.instancia import Item


def decodificar(solucao: list[int], itens: list[Item], capacidade: int) -> list[int]:
    """Turn an order of items into a binary solution by greedy insertion.

    Items are visited in the given order and each one that still fits is added, so
    every order decodes to a feasible solution and many orders decode to the same.

    Parameters
    ----------
    solucao : list of int
        Order: a permutation of the item indices.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    list of int
        Feasible binary solution.
    """
    binaria = [0] * len(itens)
    peso = 0
    for i in solucao:
        if peso + itens[i].peso <= capacidade:
            binaria[i] = 1
            peso += itens[i].peso
    return binaria


def avaliar(solucao: list[int], itens: list[Item], capacidade: int) -> int:
    """Return the value of the solution decoded from an order.

    Parameters
    ----------
    solucao : list of int
        Order: a permutation of the item indices.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    int
        Value of the decoded solution.
    """
    binaria = decodificar(solucao, itens, capacidade)
    return sum(item.valor for item, bit in zip(itens, binaria) if bit)
