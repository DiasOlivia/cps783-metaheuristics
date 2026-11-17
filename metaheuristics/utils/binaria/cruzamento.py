import random
from collections.abc import Sequence

from metaheuristics.utils.instancia import Item


def _aplicar_mascara(
    pai1: list[int], pai2: list[int], mascara: Sequence[int]
) -> tuple[list[int], list[int]]:
    """Swap the genes of the two parents where the mask is 1."""
    filho1 = [b if troca else a for a, b, troca in zip(pai1, pai2, mascara)]
    filho2 = [a if troca else b for a, b, troca in zip(pai1, pai2, mascara)]
    return filho1, filho2


def cruzamento_multiponto(
    pai1: list[int],
    pai2: list[int],
    itens: list[Item],
    capacidade: int,
    cortes: int | Sequence[int] = 2,
) -> tuple[list[int], list[int]]:
    """Exchange, alternately, the segments between the cut points.

    Created for the Genetic Algorithm (crossover).

    A cut at ``c`` falls after the first ``c`` genes. The first segment stays,
    the second is exchanged between the parents, the third stays, and so on. The
    children may not fit in the knapsack.

    Parameters
    ----------
    pai1, pai2 : list of int
        Binary parents, left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every crossover shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.
    cortes : int or sequence of int, default 2
        Number of cut points, drawn among ``1, ..., n - 1``, or the cut points
        themselves.

    Returns
    -------
    tuple of (list of int, list of int)
        The two children.
    """
    n = len(pai1)
    if isinstance(cortes, int):
        if not 1 <= cortes < n:
            raise ValueError("O número de cortes deve estar entre 1 e n - 1.")
        cortes = random.sample(range(1, n), cortes)
    if any(not 0 < corte < n for corte in cortes):
        raise ValueError("Cada corte deve estar entre 1 e n - 1.")
    # Um gene é trocado quando há um número ímpar de cortes antes dele
    mascara = [sum(corte <= i for corte in cortes) % 2 for i in range(n)]
    return _aplicar_mascara(pai1, pai2, mascara)


def cruzamento_um_ponto(
    pai1: list[int],
    pai2: list[int],
    itens: list[Item],
    capacidade: int,
    corte: int | None = None,
) -> tuple[list[int], list[int]]:
    """Join the genes before a cut point of one parent to those after it of the other.

    Created for the Genetic Algorithm (crossover).

    Parameters
    ----------
    pai1, pai2 : list of int
        Binary parents, left unchanged.
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
        ``pai1[:corte] + pai2[corte:]`` and ``pai2[:corte] + pai1[corte:]``.
    """
    return cruzamento_multiponto(
        pai1, pai2, itens, capacidade, 1 if corte is None else [corte]
    )


def cruzamento_uniforme(
    pai1: list[int],
    pai2: list[int],
    itens: list[Item],
    capacidade: int,
    mascara: Sequence[int] | None = None,
) -> tuple[list[int], list[int]]:
    """Exchange the genes of the parents where a binary mask is 1.

    Created for the Genetic Algorithm (crossover).

    Without a mask, each bit of the mask is drawn with probability 1/2, so each
    child takes each gene from either parent with the same chance.

    Parameters
    ----------
    pai1, pai2 : list of int
        Binary parents, left unchanged.
    itens : list of Item
        Items of the instance; unused, kept so every crossover shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.
    mascara : sequence of int, optional
        One bit per gene: 1 exchanges the genes at that position, 0 keeps them.

    Returns
    -------
    tuple of (list of int, list of int)
        The two children.
    """
    if mascara is None:
        mascara = [random.randint(0, 1) for _ in pai1]
    if len(mascara) != len(pai1):
        raise ValueError("A máscara deve ter um bit por gene.")
    return _aplicar_mascara(pai1, pai2, mascara)
