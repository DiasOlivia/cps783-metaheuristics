from metaheuristics.utils.instancia import Item


def calcular_valor_peso(
    solucao: list[int], itens: list[Item], capacidade: int
) -> tuple[int, int]:
    """Compute the value and weight of a binary solution.

    Created for the SA, the ILS and the VNS (evaluation).

    The value is 0 when the weight exceeds the capacity.

    Parameters
    ----------
    solucao : list of int
        Binary vector where 1 means the item at that index is in the knapsack.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    tuple of (int, int)
        Value (0 if overweight) and actual weight of the selected items.
    """
    if len(solucao) != len(itens):
        raise ValueError("Solução e itens devem ter o mesmo tamanho.")
    if any(bit not in (0, 1) for bit in solucao):
        raise ValueError("A solução deve ser binária.")
    valor = sum(item.valor for item, bit in zip(itens, solucao) if bit)
    peso = sum(item.peso for item, bit in zip(itens, solucao) if bit)
    return (valor if peso <= capacidade else 0), peso


def avaliar(solucao: list[int], itens: list[Item], capacidade: int) -> int:
    """Return the value of a binary solution (0 if overweight).

    Created for the SA, the ILS and the VNS (evaluation).

    Parameters
    ----------
    solucao : list of int
        Binary selection vector.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    int
        Solution value.
    """
    return calcular_valor_peso(solucao, itens, capacidade)[0]


def avaliar_penalizada(
    solucao: list[int], itens: list[Item], capacidade: int
) -> int:
    """Return the value minus a penalty proportional to the excess weight.

    Created for the Tabu Search (evaluation).

    ``f(s) = valor - α * max(0, peso - capacidade)``, with ``α`` equal to the sum
    of all values. With integer weights, an overweight solution scores at most 0,
    so a feasible solution is never beaten by an infeasible one.

    Parameters
    ----------
    solucao : list of int
        Binary selection vector, feasible or not.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    int
        Penalized value; equal to the value when the solution fits.
    """
    if len(solucao) != len(itens):
        raise ValueError("Solução e itens devem ter o mesmo tamanho.")
    valor = sum(item.valor for item, bit in zip(itens, solucao) if bit)
    peso = sum(item.peso for item, bit in zip(itens, solucao) if bit)
    alfa = sum(item.valor for item in itens)
    return valor - alfa * max(0, peso - capacidade)
