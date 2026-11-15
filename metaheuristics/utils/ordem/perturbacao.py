import random

from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item


def perturbar(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Shuffle the items found at ``k`` random distinct positions of the order.

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every perturbation shares one signature.
    k : int
        Number of positions involved, ``1 <= k <= len(itens)``.
    debug : Depurador, optional
        When given, records the perturbation as a debug step.

    Returns
    -------
    list of int
        New order.
    """
    if not 1 <= k <= len(itens):
        raise ValueError("k deve estar entre 1 e o número de itens.")
    nova = list(solucao)
    posicoes = random.sample(range(len(nova)), k)
    conteudo = [nova[p] for p in posicoes]
    random.shuffle(conteudo)
    for p, item in zip(posicoes, conteudo):
        nova[p] = item
    if debug is not None:
        debug.passo("perturbação", solucao, [(f"k={k}", nova)], f"k={k}")
    return nova
