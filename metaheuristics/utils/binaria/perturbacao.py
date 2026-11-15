import random

from metaheuristics.utils.binaria.avaliacao import calcular_valor_peso
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item


def perturbar(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Flip ``k`` distinct random bits, then repair the capacity if needed.

    The result is at Hamming distance ``k`` before the repair. If it is
    overweight, randomly chosen selected items are removed until it fits, which
    can change the final distance. The repair is a design choice for the knapsack.

    Parameters
    ----------
    solucao : list of int
        Feasible binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    k : int
        Number of distinct bits to flip, ``1 <= k <= len(itens)``.
    debug : Depurador, optional
        When given, records the perturbation as a debug step.

    Returns
    -------
    list of int
        Feasible perturbed solution.
    """
    if not 1 <= k <= len(itens):
        raise ValueError("k deve estar entre 1 e o número de itens.")
    _, peso = calcular_valor_peso(solucao, itens, capacidade)
    if peso > capacidade:
        raise ValueError("A perturbação exige uma solução viável.")
    nova = list(solucao)
    for i in random.sample(range(len(itens)), k):
        nova[i] ^= 1
    _, peso = calcular_valor_peso(nova, itens, capacidade)
    selecionados = [i for i, bit in enumerate(nova) if bit]
    random.shuffle(selecionados)
    for i in selecionados:
        if peso <= capacidade:
            break
        nova[i] = 0
        peso -= itens[i].peso
    if debug is not None:
        debug.passo("perturbação", solucao, [(f"k={k}", nova)], f"k={k}")
    return nova
