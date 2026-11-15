import random
from collections.abc import Callable

from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.ordem.avaliacao import avaliar


def _faltantes(solucao: list[int], itens: list[Item]) -> list[int]:
    presentes = set(solucao)
    return [j for j in range(len(itens)) if j not in presentes]


def _registrar(
    etapa: str, solucao: list[int], nova: list[int], debug: Depurador | None
) -> None:
    if debug is not None:
        rotulo = f"+{len(nova) - len(solucao)} itens"
        debug.passo(etapa, solucao, [(rotulo, nova)], rotulo)


def _inserir(
    etapa: str,
    criterio: Callable[[list[int]], tuple[int, ...]],
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None,
) -> list[int]:
    """Insert, one at a time, the missing item with the largest ``criterio``.

    ``criterio`` receives the decoded value of the item at each position of the
    current order; the chosen item goes to its best position (the first one, on
    ties). The values are recomputed after each insertion.
    """
    nova = list(solucao)
    faltantes = _faltantes(solucao, itens)
    while faltantes:
        escolha = None
        for j in faltantes:
            valores = [
                avaliar(nova[:p] + [j] + nova[p:], itens, capacidade)
                for p in range(len(nova) + 1)
            ]
            chave = criterio(valores)
            if escolha is None or chave > escolha[0]:
                escolha = (chave, j, valores.index(max(valores)))
        _, j, posicao = escolha
        nova.insert(posicao, j)
        faltantes.remove(j)
    _registrar(etapa, solucao, nova, debug)
    return nova


def insercao_aleatoria(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Put each missing item back at a random position of the order.

    Parameters
    ----------
    solucao : list of int
        Partial order (item indices without repetition), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity; unused, kept so every insertion shares one signature.
    debug : Depurador, optional
        When given, records the insertion as a debug step.

    Returns
    -------
    list of int
        Complete order (permutation of the item indices).
    """
    nova = list(solucao)
    faltantes = _faltantes(solucao, itens)
    random.shuffle(faltantes)
    for j in faltantes:
        nova.insert(random.randint(0, len(nova)), j)
    _registrar("inserção aleatória", solucao, nova, debug)
    return nova


def insercao_gulosa(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Repeatedly insert the missing item at the position with the best value.

    Every missing item is tried at every position, and the pair with the highest
    decoded value is applied; the values are recomputed after each insertion.
    With ``m`` missing items and ``n`` items, this decodes ``O(m² n)`` orders of
    size ``n``, so it is slow for large instances.

    Parameters
    ----------
    solucao : list of int
        Partial order (item indices without repetition), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    debug : Depurador, optional
        When given, records the insertion as a debug step.

    Returns
    -------
    list of int
        Complete order (permutation of the item indices).
    """
    return _inserir(
        "inserção gulosa",
        lambda valores: (max(valores),),
        solucao,
        itens,
        capacidade,
        debug,
    )


def _arrependimento(valores: list[int]) -> tuple[int, int]:
    ordenados = sorted(valores, reverse=True)
    segunda = ordenados[1] if len(ordenados) > 1 else ordenados[0]
    return ordenados[0] - segunda, ordenados[0]


def insercao_arrependimento(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None = None,
) -> list[int]:
    """Repeatedly insert the missing item that would lose the most if postponed.

    The regret of an item is the decoded value at its best position minus the
    value at its second best position. The item with the largest regret (ties:
    the largest best value) goes to its best position, and the regrets are
    recomputed. Many positions decode to the same value, so the regret is often 0.
    The cost is the same as ``insercao_gulosa``.

    Parameters
    ----------
    solucao : list of int
        Partial order (item indices without repetition), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    debug : Depurador, optional
        When given, records the insertion as a debug step.

    Returns
    -------
    list of int
        Complete order (permutation of the item indices).
    """
    return _inserir(
        "inserção por arrependimento",
        _arrependimento,
        solucao,
        itens,
        capacidade,
        debug,
    )
