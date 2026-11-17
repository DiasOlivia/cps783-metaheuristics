from collections.abc import Callable

from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item

Passos = Callable[
    [list[int], list[Item], int, list[int]], list[tuple[str, list[int]]]
]
Elite = list[tuple[float, list[int]]]

DIRECOES = ("backward", "forward", "backward_forward")


def reconectar(
    inicial: list[int],
    guia: list[int],
    itens: list[Item],
    capacidade: int,
    avaliar: Callable,
    passos: Passos,
    direcao: str = "backward",
    debug: Depurador | None = None,
) -> tuple[list[int] | None, float | None, int]:
    """Walk the path between two solutions and return its best intermediate one.

    Created for the GRASP (path-relinking).

    At each step every move given by ``passos`` (each brings one attribute of the
    other end) is evaluated, and the best one is applied (path-relinking). The
    two ends are not candidates. ``'backward'`` starts from the better of the two
    solutions, ``'forward'`` from the worse, and ``'backward_forward'`` moves both
    ends alternately, each towards the current position of the other, until they
    meet.

    Parameters
    ----------
    inicial, guia : list of int
        The two ends of the path, left unchanged.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    avaliar : callable
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    passos : callable
        Moves towards a target, ``(solucao, itens, capacidade, alvo) ->
        [(rotulo, vizinha)]``.
    direcao : {'backward', 'forward', 'backward_forward'}, default 'backward'
        Where the walk starts.
    debug : Depurador, optional
        When given, records each step as a debug step.

    Returns
    -------
    tuple of (list of int or None, float or None, int)
        Best intermediate solution and its value (None when the ends are
        neighbors), and the number of evaluations, including the two ends.
    """
    if direcao not in DIRECOES:
        raise ValueError(f"direcao deve ser uma de {DIRECOES}.")
    valor_inicial = avaliar(inicial, itens, capacidade)
    valor_guia = avaliar(guia, itens, capacidade)
    avaliacoes = 2
    melhor, pior = (
        (inicial, guia) if valor_inicial >= valor_guia else (guia, inicial)
    )
    frentes = [pior, melhor] if direcao == "forward" else [melhor, pior]
    caminho, valor_caminho = None, None
    lado = 0
    while True:
        movel, alvo = frentes[lado], frentes[1 - lado]
        opcoes = [
            (rotulo, vizinha)
            for rotulo, vizinha in passos(movel, itens, capacidade, alvo)
            if vizinha != alvo
        ]
        if not opcoes:
            return caminho, valor_caminho, avaliacoes
        valores = [avaliar(vizinha, itens, capacidade) for _, vizinha in opcoes]
        avaliacoes += len(opcoes)
        k = max(range(len(opcoes)), key=lambda i: valores[i])
        if debug is not None:
            debug.passo("reconexão", movel, opcoes, opcoes[k][0], direcao)
        frentes[lado] = opcoes[k][1]
        if valor_caminho is None or valores[k] > valor_caminho:
            caminho, valor_caminho = opcoes[k][1], valores[k]
        if direcao == "backward_forward":
            lado = 1 - lado


def atualizar_elite(
    elite: Elite,
    solucao: list[int],
    valor: float,
    tamanho: int,
    diferenca_minima: int,
    distancia: Callable[[list[int], list[int]], int],
) -> bool:
    """Offer a solution to the elite pool, updating it in place.

    Created for the GRASP (elite pool).

    While the pool is not full, any new solution enters. Afterwards, a solution
    enters if it beats the best of the pool, or if it beats the worst and its
    distance to every solution of the pool is at least ``diferenca_minima``. It
    replaces the worst solution.

    Parameters
    ----------
    elite : list of (float, list of int)
        Pool of ``(valor, solucao)`` pairs, changed in place.
    solucao : list of int
        Candidate solution.
    valor : float
        Value of the candidate.
    tamanho : int
        Pool capacity.
    diferenca_minima : int
        Smallest distance to the pool for a candidate that does not beat its best.
    distancia : callable
        Distance between two solutions, e.g. the number of reconnection moves.

    Returns
    -------
    bool
        Whether the solution entered the pool.
    """
    if any(outra == solucao for _, outra in elite):
        return False
    if len(elite) < tamanho:
        elite.append((valor, list(solucao)))
        return True
    pior = min(range(len(elite)), key=lambda k: elite[k][0])
    supera_melhor = valor > max(v for v, _ in elite)
    diferente = valor > elite[pior][0] and all(
        distancia(solucao, outra) >= diferenca_minima for _, outra in elite
    )
    if supera_melhor or diferente:
        elite[pior] = (valor, list(solucao))
        return True
    return False
