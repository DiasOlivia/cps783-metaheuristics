from metaheuristics.utils.instancia import Item


def passos_para_guia(
    solucao: list[int], itens: list[Item], capacidade: int, guia: list[int]
) -> list[tuple[str, list[int]]]:
    """List the swaps that put, at one position, the item the guide has there.

    Created for the GRASP (path-relinking).

    Each move fixes at least one position where the order differs from the guide,
    so the number of moves is the number of differing positions.

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices), left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every reconnection shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept so every reconnection shares one
        signature.
    guia : list of int
        Guide order.

    Returns
    -------
    list of (str, list of int)
        A label ``p←j`` (item ``j`` goes to position ``p``) and the new order, by
        position.
    """
    posicao = {item: p for p, item in enumerate(solucao)}
    passos = []
    for i, (item, alvo) in enumerate(zip(solucao, guia)):
        if item != alvo:
            nova = list(solucao)
            j = posicao[alvo]
            nova[i], nova[j] = nova[j], nova[i]
            passos.append((f"{i + 1}←{alvo + 1}", nova))
    return passos
