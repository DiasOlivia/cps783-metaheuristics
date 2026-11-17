from metaheuristics.utils.binaria.busca_local import _aplicar
from metaheuristics.utils.binaria.busca_local import _movimentos
from metaheuristics.utils.instancia import Item

Vizinha = tuple[str, tuple[int, ...], list[int]]


def vizinhanca_flip(
    solucao: list[int], itens: list[Item], capacidade: int
) -> list[Vizinha]:
    """List every neighbor obtained by flipping one bit, feasible or not.

    Created for the Tabu Search (neighborhood).

    Parameters
    ----------
    solucao : list of int
        Binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every neighborhood shares one signature.

    Returns
    -------
    list of (str, tuple of int, list of int)
        One entry per item, in index order: a label (``+i`` adds, ``−i`` removes
        item ``i``), the flipped item and the neighbor.
    """
    return [
        (f"{'−' if bit else '+'}{i + 1}", (i,), _aplicar(solucao, (i,)))
        for i, bit in enumerate(solucao)
    ]


def vizinhanca_flip_troca(
    solucao: list[int], itens: list[Item], capacidade: int
) -> list[Vizinha]:
    """List the one-bit flips and the 1-for-1 swaps, feasible or not.

    Created for the Tabu Search (neighborhood).

    These are the moves of the binary local searches, in the same order: first
    the flips by index, then each selected item swapped for each unselected one.

    Parameters
    ----------
    solucao : list of int
        Binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every neighborhood shares one signature.

    Returns
    -------
    list of (str, tuple of int, list of int)
        A label (``+i``, ``−i`` or ``i→j``), the items changed and the neighbor.
    """
    # O peso e o valor que _movimentos calcula para cada vizinha não são usados aqui
    return [
        (rotulo, indices, _aplicar(solucao, indices))
        for rotulo, indices, _, _ in _movimentos(solucao, itens, 0, 0)
    ]
