import random

from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item


def _registrar(
    etapa: str, solucao: list[int], nova: list[int], debug: Depurador | None
) -> None:
    if debug is not None:
        rotulo = f"+{sum(nova) - sum(solucao)} itens"
        debug.passo(etapa, solucao, [(rotulo, nova)], rotulo)


def insercao_aleatoria(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Visit the items outside the knapsack in random order and add each that fits.

    Parameters
    ----------
    solucao : list of int
        Feasible binary solution, possibly partial; left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    debug : Depurador, optional
        When given, records the insertion as a debug step.

    Returns
    -------
    list of int
        Feasible solution where no item outside fits anymore.
    """
    nova = list(solucao)
    peso = sum(item.peso for item, bit in zip(itens, nova) if bit)
    fora = [j for j, bit in enumerate(nova) if not bit]
    random.shuffle(fora)
    for j in fora:
        if peso + itens[j].peso <= capacidade:
            nova[j] = 1
            peso += itens[j].peso
    _registrar("inserção aleatória", solucao, nova, debug)
    return nova


def insercao_gulosa(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Repeatedly add the item outside that fits and increases the value the most.

    After each insertion the remaining capacity shrinks, so the items that still
    fit are recomputed. Ties keep the lowest index.

    Parameters
    ----------
    solucao : list of int
        Feasible binary solution, possibly partial; left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    debug : Depurador, optional
        When given, records the insertion as a debug step.

    Returns
    -------
    list of int
        Feasible solution where no item outside fits anymore.
    """
    nova = list(solucao)
    peso = sum(item.peso for item, bit in zip(itens, nova) if bit)
    while True:
        cabem = [
            j
            for j, bit in enumerate(nova)
            if not bit and peso + itens[j].peso <= capacidade
        ]
        if not cabem:
            break
        j = max(cabem, key=lambda c: itens[c].valor)
        nova[j] = 1
        peso += itens[j].peso
    _registrar("inserção gulosa", solucao, nova, debug)
    return nova
