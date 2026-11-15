from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.ordem.avaliacao import avaliar


def busca_local_primeira_melhora(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None = None,
) -> tuple[list[int], int]:
    """First-improvement local search swapping two positions of the order.

    Swaps are examined in a fixed order, ``(0, 1), (0, 2), ..., (n-2, n-1)``, and
    the first one that strictly improves the decoded value is applied. Each
    neighbor is decoded from scratch, so a pass costs ``O(n^3)``.

    Parameters
    ----------
    solucao : list of int
        Starting order (permutation of the item indices), left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    debug : Depurador, optional
        When given, records each pass as a debug step.

    Returns
    -------
    tuple of (list of int, int)
        Locally optimal order and number of neighbors evaluated.
    """
    atual = list(solucao)
    valor = avaliar(atual, itens, capacidade)
    avaliacoes = 0
    n = len(atual)
    while True:
        escolhida = None
        examinados = []
        for i in range(n - 1):
            for j in range(i + 1, n):
                vizinha = list(atual)
                vizinha[i], vizinha[j] = vizinha[j], vizinha[i]
                avaliacoes += 1
                if debug is not None:
                    examinados.append((f"{i + 1}↔{j + 1}", vizinha))
                novo_valor = avaliar(vizinha, itens, capacidade)
                if novo_valor > valor:
                    escolhida, valor = vizinha, novo_valor
                    break
            if escolhida is not None:
                break
        if debug is not None:
            debug.passo(
                "busca local",
                atual,
                examinados,
                examinados[-1][0] if escolhida is not None else None,
                ""
                if escolhida is not None
                else "nenhuma troca melhora: ótimo local",
            )
        if escolhida is None:
            return atual, avaliacoes
        atual = escolhida
