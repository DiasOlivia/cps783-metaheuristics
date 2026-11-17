import random

from metaheuristics.utils.instancia import Item


def _cortes(n: int, cortes: tuple[int, int] | None) -> tuple[int, int]:
    if cortes is None:
        return tuple(sorted(random.sample(range(n + 1), 2)))
    i, j = cortes
    if not 0 <= i < j <= n:
        raise ValueError("Os cortes devem satisfazer 0 <= i < j <= n.")
    return i, j


def _preencher_em_ordem(
    pai: list[int], outro: list[int], i: int, j: int
) -> list[int]:
    """Keep ``pai[i:j]`` in place and fill the rest with ``outro``, in order."""
    trecho = pai[i:j]
    usados = set(trecho)
    resto = [item for item in outro if item not in usados]
    return resto[:i] + trecho + resto[i:]


def _mapear(pai: list[int], outro: list[int], i: int, j: int) -> list[int]:
    """Keep ``pai[i:j]`` in place and fill the rest by partial mapping."""
    filho = list(outro)
    filho[i:j] = pai[i:j]
    mapa = {pai[k]: outro[k] for k in range(i, j)}
    for k in [*range(i), *range(j, len(pai))]:
        item = outro[k]
        # Repetido: segue o mapa até achar um item que não está no trecho copiado
        while item in mapa:
            item = mapa[item]
        filho[k] = item
    return filho


def cruzamento_opx(
    pai1: list[int],
    pai2: list[int],
    itens: list[Item],
    capacidade: int,
    corte: int | None = None,
) -> tuple[list[int], list[int]]:
    """Order-preserving one-point crossover (OPX).

    The child keeps the genes of one parent before the cut, in place, and takes
    the others in the order they appear in the other parent.

    Parameters
    ----------
    pai1, pai2 : list of int
        Orders (permutations of the item indices), left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every crossover shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.
    corte : int, optional
        Number of genes before the cut, between ``1`` and ``n - 1``; drawn when
        omitted.

    Returns
    -------
    tuple of (list of int, list of int)
        The child that keeps the start of ``pai1`` and the one that keeps the
        start of ``pai2``.
    """
    n = len(pai1)
    if corte is None:
        corte = random.randint(1, n - 1)
    if not 0 < corte < n:
        raise ValueError("O corte deve estar entre 1 e n - 1.")
    return (
        _preencher_em_ordem(pai1, pai2, 0, corte),
        _preencher_em_ordem(pai2, pai1, 0, corte),
    )


def cruzamento_lox(
    pai1: list[int],
    pai2: list[int],
    itens: list[Item],
    capacidade: int,
    cortes: tuple[int, int] | None = None,
) -> tuple[list[int], list[int]]:
    """Linear-order crossover (LOX).

    The child keeps the genes of one parent between the two cuts, in place, and
    fills the other positions, from left to right, with the remaining genes in
    the order they appear in the other parent.

    Parameters
    ----------
    pai1, pai2 : list of int
        Orders (permutations of the item indices), left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every crossover shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.
    cortes : tuple of (int, int), optional
        The segment ``[i, j)`` that is kept, with ``0 <= i < j <= n``; drawn when
        omitted.

    Returns
    -------
    tuple of (list of int, list of int)
        The child that keeps the segment of ``pai1`` and the one that keeps the
        segment of ``pai2``.
    """
    i, j = _cortes(len(pai1), cortes)
    return (
        _preencher_em_ordem(pai1, pai2, i, j),
        _preencher_em_ordem(pai2, pai1, i, j),
    )


def cruzamento_pmx(
    pai1: list[int],
    pai2: list[int],
    itens: list[Item],
    capacidade: int,
    cortes: tuple[int, int] | None = None,
) -> tuple[list[int], list[int]]:
    """Partially-mapped crossover (PMX).

    The child keeps the genes of one parent between the two cuts, in place, and
    takes the other positions from the other parent. A gene that would repeat is
    replaced by following the mapping between the two segments until a gene not
    yet in the child is found.

    Parameters
    ----------
    pai1, pai2 : list of int
        Orders (permutations of the item indices), left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every crossover shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.
    cortes : tuple of (int, int), optional
        The segment ``[i, j)`` that is kept, with ``0 <= i < j <= n``; drawn when
        omitted.

    Returns
    -------
    tuple of (list of int, list of int)
        The child that keeps the segment of ``pai1`` and the one that keeps the
        segment of ``pai2``.
    """
    i, j = _cortes(len(pai1), cortes)
    return _mapear(pai1, pai2, i, j), _mapear(pai2, pai1, i, j)
