from metaheuristics.utils.instancia import Item

Vizinha = tuple[str, tuple[int, ...], list[int]]


def vizinhanca_troca(
    solucao: list[int], itens: list[Item], capacidade: int
) -> list[Vizinha]:
    """List every order obtained by swapping two positions.

    Created for the Tabu Search (neighborhood).

    The swaps follow the order ``(0, 1), (0, 2), ..., (n-2, n-1)``, the same of
    ``ordem.busca_local_primeira_melhora``. The items swapped, not the positions,
    are the attributes that become tabu.

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices), left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every neighborhood shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept so every neighborhood shares one signature.

    Returns
    -------
    list of (str, tuple of int, list of int)
        A label with the swapped positions (``i↔j``), the two items swapped and
        the new order.
    """
    vizinhas = []
    n = len(solucao)
    for i in range(n - 1):
        for j in range(i + 1, n):
            vizinha = list(solucao)
            vizinha[i], vizinha[j] = vizinha[j], vizinha[i]
            vizinhas.append((f"{i + 1}↔{j + 1}", (solucao[i], solucao[j]), vizinha))
    return vizinhas
