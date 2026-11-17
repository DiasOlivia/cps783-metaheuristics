import random

from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item


def _remover(
    etapa: str,
    solucao: list[int],
    removidos: list[int],
    debug: Depurador | None,
) -> list[int]:
    nova = list(solucao)
    for i in removidos:
        nova[i] = 0
    if debug is not None:
        rotulo = f"q={len(removidos)}"
        debug.passo(etapa, solucao, [(rotulo, nova)], rotulo)
    return nova


def _dentro(solucao: list[int], k: int) -> list[int]:
    if k < 1:
        raise ValueError("k deve ser pelo menos 1.")
    return [i for i, bit in enumerate(solucao) if bit]


def remocao_aleatoria(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Take ``k`` random items out of the knapsack.

    Created for the ALNS (destroy operator).

    Parameters
    ----------
    solucao : list of int
        Binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every removal shares one signature.
    k : int
        Number of items to remove; all of them when fewer are in the knapsack.
    debug : Depurador, optional
        When given, records the removal as a debug step.

    Returns
    -------
    list of int
        Partial solution, with room for the insertion.
    """
    dentro = _dentro(solucao, k)
    removidos = random.sample(dentro, min(k, len(dentro)))
    return _remover("remoção aleatória", solucao, removidos, debug)


def remocao_pior(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Take out the ``k`` items with the lowest value-to-weight ratio.

    Created for the ALNS (destroy operator).

    These items give the least value for the capacity they use. Ties keep the
    order of the indices, so the removal is deterministic.

    Parameters
    ----------
    solucao : list of int
        Binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every removal shares one signature.
    k : int
        Number of items to remove; all of them when fewer are in the knapsack.
    debug : Depurador, optional
        When given, records the removal as a debug step.

    Returns
    -------
    list of int
        Partial solution, with room for the insertion.
    """
    dentro = _dentro(solucao, k)
    removidos = sorted(dentro, key=lambda i: itens[i].valor / itens[i].peso)[:k]
    return _remover("remoção pior", solucao, removidos, debug)


def remocao_shaw(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    k: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Take out a random item and the ``k - 1`` items most similar to it.

    Created for the ALNS (destroy operator).

    Two items are similar when their weights and values are close, measured by
    ``|Δpeso| / max_peso + |Δvalor| / max_valor`` over the instance. Similar items
    are easy to exchange, so the insertion can swap them (Shaw removal).

    Parameters
    ----------
    solucao : list of int
        Binary solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every removal shares one signature.
    k : int
        Number of items to remove; all of them when fewer are in the knapsack.
    debug : Depurador, optional
        When given, records the removal as a debug step.

    Returns
    -------
    list of int
        Partial solution, with room for the insertion.
    """
    dentro = _dentro(solucao, k)
    if not dentro:
        return _remover("remoção Shaw", solucao, [], debug)
    semente = random.choice(dentro)
    max_peso = max(item.peso for item in itens)
    max_valor = max(item.valor for item in itens) or 1

    def distancia(j: int) -> float:
        return (
            abs(itens[j].peso - itens[semente].peso) / max_peso
            + abs(itens[j].valor - itens[semente].valor) / max_valor
        )

    parecidos = sorted((j for j in dentro if j != semente), key=distancia)
    return _remover("remoção Shaw", solucao, [semente] + parecidos[: k - 1], debug)
