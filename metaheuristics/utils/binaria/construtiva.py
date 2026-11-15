import math
import random
from collections.abc import Callable

from metaheuristics.guloso.mochila import mochila_gulosa
from metaheuristics.utils.instancia import Item

Vies = str | Callable[[int], float]

# Peso de cada posição r (1 = melhor) da RCL no sorteio (bias choice)
VIESES: dict[str, Callable[[int], float]] = {
    "aleatoria": lambda r: 1.0,
    "logaritmica": lambda r: 1 / math.log(r + 1),
    "exponencial": lambda r: math.exp(-r),
    "polinomial": lambda r: r**-2,
}


def construtiva_aleatoria(itens: list[Item], capacidade: int) -> list[int]:
    """Build a random feasible solution: shuffle the items and insert what fits.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    list of int
        Feasible binary solution.
    """
    solucao = [0] * len(itens)
    indices = list(range(len(itens)))
    # Cada execução começa de um ponto diferente, sem depender da ordem da lista
    random.shuffle(indices)
    peso_atual = 0
    for i in indices:
        if peso_atual + itens[i].peso <= capacidade:
            solucao[i] = 1
            peso_atual += itens[i].peso
    return solucao


def construtiva_gulosa(itens: list[Item], capacidade: int) -> list[int]:
    """Build the greedy solution by non-increasing value-to-weight ratio.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    list of int
        Feasible binary solution.
    """
    return mochila_gulosa(
        [item.peso for item in itens],
        [item.valor for item in itens],
        capacidade,
        "densidade",
    )


def _sequencia_gulosa_aleatoria(
    itens: list[Item], capacidade: int, alfa: float, vies: Vies
) -> list[int]:
    """Return the items chosen, in order, by the greedy randomized construction."""
    if not 0 <= alfa <= 1:
        raise ValueError("alfa deve estar entre 0 e 1.")
    if isinstance(vies, str):
        if vies not in VIESES:
            raise ValueError(f"vies deve ser uma função ou um de {sorted(VIESES)}.")
        vies = VIESES[vies]
    escolhidos = []
    fora = set(range(len(itens)))
    peso = 0
    while True:
        candidatos = [j for j in fora if peso + itens[j].peso <= capacidade]
        if not candidatos:
            return escolhidos
        densidade = {j: itens[j].valor / itens[j].peso for j in candidatos}
        maxima, minima = max(densidade.values()), min(densidade.values())
        limite = maxima - alfa * (maxima - minima)
        rcl = sorted(
            (j for j in candidatos if densidade[j] >= limite),
            key=lambda j: (-densidade[j], j),
        )
        pesos = [vies(r) for r in range(1, len(rcl) + 1)]
        escolhido = random.choices(rcl, weights=pesos)[0]
        escolhidos.append(escolhido)
        fora.remove(escolhido)
        peso += itens[escolhido].peso


def construtiva_gulosa_aleatoria(
    itens: list[Item], capacidade: int, alfa: float = 0.3, vies: Vies = "aleatoria"
) -> list[int]:
    """Build a solution by the greedy randomized construction of GRASP.

    At each step the candidates are the items that still fit, ranked by
    value-to-weight ratio. The restricted candidate list (RCL) keeps those with
    ratio ``>= c_max - alfa * (c_max - c_min)``, and one of them is drawn,
    uniformly or with a bias by rank. ``alfa = 0`` is the pure greedy and
    ``alfa = 1`` a random choice among the items that fit.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    alfa : float, default 0.3
        RCL quality parameter, in ``[0, 1]``.
    vies : str or callable, default 'aleatoria'
        Weight of the RCL position ``r`` (1 is the best) in the draw: one of
        ``'aleatoria'`` (1), ``'logaritmica'`` (1 / log(r + 1)), ``'exponencial'``
        (e^-r), ``'polinomial'`` (r^-2), or a function of ``r``.

    Returns
    -------
    list of int
        Feasible binary solution where no item outside fits anymore.
    """
    solucao = [0] * len(itens)
    for j in _sequencia_gulosa_aleatoria(itens, capacidade, alfa, vies):
        solucao[j] = 1
    return solucao
