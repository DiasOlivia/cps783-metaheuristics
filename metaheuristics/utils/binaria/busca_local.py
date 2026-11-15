from collections.abc import Iterator

from metaheuristics.utils.binaria.avaliacao import calcular_valor_peso
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item

Movimento = tuple[str, tuple[int, ...], int, int]


def _movimentos(
    atual: list[int], itens: list[Item], peso: int, valor: int
) -> Iterator[Movimento]:
    """Yield every 1-flip and 1-for-1 swap with its resulting weight and value."""
    for i, item in enumerate(itens):
        sinal = -1 if atual[i] else 1
        rotulo = f"{'−' if atual[i] else '+'}{i + 1}"
        yield rotulo, (i,), peso + sinal * item.peso, valor + sinal * item.valor
    selecionados = [i for i, bit in enumerate(atual) if bit]
    nao_selecionados = [j for j, bit in enumerate(atual) if not bit]
    # A troca permite melhorar mesmo com a mochila cheia
    for i in selecionados:
        for j in nao_selecionados:
            yield (
                f"{i + 1}→{j + 1}",
                (i, j),
                peso - itens[i].peso + itens[j].peso,
                valor - itens[i].valor + itens[j].valor,
            )


def _aplicar(solucao: list[int], indices: tuple[int, ...]) -> list[int]:
    nova = list(solucao)
    for indice in indices:
        nova[indice] ^= 1
    return nova


def _buscar(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    primeira: bool,
    debug: Depurador | None,
) -> tuple[list[int], int]:
    atual = list(solucao)
    valor, peso = calcular_valor_peso(atual, itens, capacidade)
    if peso > capacidade:
        raise ValueError("A busca local exige uma solução inicial viável.")
    avaliacoes = 0
    while True:
        escolhido = None
        melhor_valor = valor
        examinados = []
        for movimento in _movimentos(atual, itens, peso, valor):
            _, _, novo_peso, novo_valor = movimento
            avaliacoes += 1
            if debug is not None:
                examinados.append(movimento)
            if novo_peso <= capacidade and novo_valor > melhor_valor:
                escolhido, melhor_valor = movimento, novo_valor
                if primeira:
                    break
        if debug is not None:
            vizinhas = [
                (r, _aplicar(atual, indices)) for r, indices, _, _ in examinados
            ]
            debug.passo(
                "busca local",
                atual,
                vizinhas,
                escolhido[0] if escolhido else None,
                "" if escolhido else "nenhuma vizinha melhora: ótimo local",
            )
        if escolhido is None:
            return atual, avaliacoes
        atual = _aplicar(atual, escolhido[1])
        valor, peso = calcular_valor_peso(atual, itens, capacidade)


def busca_local_melhor_melhora(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None = None,
) -> tuple[list[int], int]:
    """Best-improvement local search over feasible 1-flip and 1-for-1 swap moves.

    Each pass examines every move and applies the one with the largest strictly
    better value; it stops at a local optimum for this neighborhood.

    Parameters
    ----------
    solucao : list of int
        Feasible starting solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    debug : Depurador, optional
        When given, records each pass as a debug step.

    Returns
    -------
    tuple of (list of int, int)
        Local optimum and number of neighbors evaluated.
    """
    return _buscar(solucao, itens, capacidade, False, debug)


def busca_local_primeira_melhora(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    debug: Depurador | None = None,
) -> tuple[list[int], int]:
    """First-improvement local search over feasible 1-flip and 1-for-1 swap moves.

    Moves are examined in a fixed order (flips by index, then swaps) and the first
    strictly better one is applied right away.

    Parameters
    ----------
    solucao : list of int
        Feasible starting solution, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    debug : Depurador, optional
        When given, records each pass as a debug step.

    Returns
    -------
    tuple of (list of int, int)
        Local optimum and number of neighbors evaluated.
    """
    return _buscar(solucao, itens, capacidade, True, debug)
