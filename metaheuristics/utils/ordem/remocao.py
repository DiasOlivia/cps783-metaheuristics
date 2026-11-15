from collections.abc import Callable

from metaheuristics.utils.binaria import remocao as remocao_binaria
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.ordem.avaliacao import decodificar


def _remover(
    etapa: str,
    remover: Callable,
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None,
) -> list[int]:
    """Drop from the order the items that the binary removal takes out."""
    selecao = decodificar(solucao, itens, capacidade)
    parcial = remover(selecao, itens, capacidade, k)
    removidos = {i for i, (a, b) in enumerate(zip(selecao, parcial)) if a != b}
    nova = [i for i in solucao if i not in removidos]
    if debug is not None:
        rotulo = f"q={len(removidos)}"
        debug.passo(etapa, solucao, [(rotulo, nova)], rotulo)
    return nova


def remocao_aleatoria(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Drop from the order ``k`` random items of the decoded knapsack.

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices, possibly partial), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    k : int
        Number of items to remove; all of them when fewer are in the knapsack.
    debug : Depurador, optional
        When given, records the removal as a debug step.

    Returns
    -------
    list of int
        Partial order, without the removed items.
    """
    return _remover(
        "remoção aleatória",
        remocao_binaria.remocao_aleatoria,
        solucao,
        itens,
        capacidade,
        k,
        debug,
    )


def remocao_pior(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Drop from the order the ``k`` decoded items with the lowest density.

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices, possibly partial), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    k : int
        Number of items to remove; all of them when fewer are in the knapsack.
    debug : Depurador, optional
        When given, records the removal as a debug step.

    Returns
    -------
    list of int
        Partial order, without the removed items.
    """
    return _remover(
        "remoção pior",
        remocao_binaria.remocao_pior,
        solucao,
        itens,
        capacidade,
        k,
        debug,
    )


def remocao_shaw(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Drop from the order a random decoded item and the ``k - 1`` most similar.

    Similarity follows ``binaria.remocao_shaw``: close weights and values.

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices, possibly partial), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    k : int
        Number of items to remove; all of them when fewer are in the knapsack.
    debug : Depurador, optional
        When given, records the removal as a debug step.

    Returns
    -------
    list of int
        Partial order, without the removed items.
    """
    return _remover(
        "remoção Shaw",
        remocao_binaria.remocao_shaw,
        solucao,
        itens,
        capacidade,
        k,
        debug,
    )
