from metaheuristics.utils.binaria.busca_local import _aplicar
from metaheuristics.utils.instancia import Item


def passos_para_guia(
    solucao: list[int], itens: list[Item], capacidade: int, guia: list[int]
) -> list[tuple[str, list[int]]]:
    """List the moves that bring one attribute of the guide into the solution.

    Each move flips one bit where the solution differs from the guide, so the
    number of moves is the Hamming distance (the symmetric difference of the
    selected items). Moves may lead to solutions that do not fit.

    Parameters
    ----------
    solucao : list of int
        Binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every reconnection shares one
        signature.
    guia : list of int
        Binary guide solution.

    Returns
    -------
    list of (str, list of int)
        A label (``+i`` adds, ``−i`` removes item ``i``) and the new solution,
        in index order.
    """
    return [
        (f"{'−' if bit else '+'}{i + 1}", _aplicar(solucao, (i,)))
        for i, (bit, alvo) in enumerate(zip(solucao, guia))
        if bit != alvo
    ]
