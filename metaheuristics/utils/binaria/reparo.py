from metaheuristics.utils.binaria.avaliacao import calcular_valor_peso
from metaheuristics.utils.instancia import Item


def reparar(solucao: list[int], itens: list[Item], capacidade: int) -> list[int]:
    """Make a binary solution fit, then fill it greedily (Chu and Beasley, 1998).

    First the selected items are removed by non-decreasing value-to-weight ratio
    until the solution fits. Then the items outside are tried by non-increasing
    ratio, and each one that still fits is added. The result is feasible and no
    item outside fits anymore.

    Parameters
    ----------
    solucao : list of int
        Binary solution, feasible or not, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    list of int
        Feasible binary solution.
    """
    _, peso = calcular_valor_peso(solucao, itens, capacidade)
    nova = list(solucao)

    def densidade(i: int) -> float:
        return itens[i].valor / itens[i].peso

    for i in sorted((i for i, bit in enumerate(nova) if bit), key=densidade):
        if peso <= capacidade:
            break
        nova[i] = 0
        peso -= itens[i].peso
    fora = (i for i, bit in enumerate(nova) if not bit)
    for i in sorted(fora, key=densidade, reverse=True):
        if peso + itens[i].peso <= capacidade:
            nova[i] = 1
            peso += itens[i].peso
    return nova
