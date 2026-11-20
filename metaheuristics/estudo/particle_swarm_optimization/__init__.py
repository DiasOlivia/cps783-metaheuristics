"""Particle Swarm Optimization (PSO) for the 0-1 knapsack problem."""

import random
import statistics
from collections.abc import Callable

from metaheuristics.utils import binaria
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item


def particle_swarm_optimization_mochila(
    itens: list[Item],
    capacidade: int,
    tamanho_enxame: int = 20,
    max_iteracoes: int = 100,
    inercia: float | tuple[float, float] = 1.0,
    c1: float = 2.0,
    c2: float = 2.0,
    vmax: float = 4.0,
    avaliar: Callable = binaria.avaliar_penalizada,
    construtiva: Callable = binaria.construtiva_aleatoria,
    coordenadas: Callable = binaria.coordenadas,
    mover: Callable = binaria.mover_sigmoide,
    busca_local: Callable | None = None,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Solve the 0-1 knapsack problem with Particle Swarm Optimization.

    Each particle is a solution with a velocity per item. At every iteration,
    each particle updates its velocity with
    ``v = w v + c1 r1 (pbest - x) + c2 r2 (gbest - x)``, where ``x``, ``pbest``
    and ``gbest`` are the ``coordenadas`` of the particle, of its best position
    and of the best position of the swarm, ``r1, r2 ~ U(0, 1)`` are drawn per
    item and ``v`` is clipped to ``[-vmax, vmax]``. Then it flies with ``mover``
    and updates its best position and the swarm's right away. The default pieces
    are the binary PSO (sigmoid) with the penalized evaluation.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    tamanho_enxame : int, default 20
        Number of particles.
    max_iteracoes : int, default 100
        Number of iterations; zero returns the best initial particle.
    inercia : float or tuple of (float, float), default 1.0
        Inertia factor ``w``. A pair ``(inicial, final)`` makes it decrease
        linearly from the first to the last iteration.
    c1 : float, default 2.0
        Self-confidence constant (individual cognition).
    c2 : float, default 2.0
        Swarm-confidence constant (social learning).
    vmax : float, default 4.0
        Largest absolute velocity; initial velocities are drawn in
        ``[-vmax, vmax]``.
    avaliar : callable, default binaria.avaliar_penalizada
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_aleatoria
        Initial position of each particle, ``(itens, capacidade) -> solucao``.
    coordenadas : callable, default binaria.coordenadas
        Numeric position of a solution, ``(solucao, itens, capacidade) ->
        [float]``, one coordinate per item.
    mover : callable, default binaria.mover_sigmoide
        Flight, ``(solucao, itens, capacidade, velocidade) -> solucao``.
    busca_local : callable, optional
        Applied to a particle that improves its own best position,
        ``(solucao, itens, capacidade, debug) -> (solucao, avaliacoes)``.
    debug : Depurador, optional
        Draws the swarm and the result of each iteration.

    Returns
    -------
    melhor_solucao : list of int
        Best position found (gbest), in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        Per iteration, from 0 (the initial swarm): ``valor_candidato`` (mean
        value of the swarm), ``valor_atual`` (best particle of the iteration),
        ``melhor_valor`` (gbest), ``avaliacoes`` and ``inercia``.
    """
    inicial, final = (
        (inercia, inercia) if isinstance(inercia, (int, float)) else inercia
    )
    if tamanho_enxame < 1 or max_iteracoes < 0:
        raise ValueError("tamanho_enxame >= 1 e max_iteracoes >= 0.")
    if vmax <= 0:
        raise ValueError("vmax deve ser positivo.")
    if min(inicial, final, c1, c2) < 0:
        raise ValueError("Inércia, c1 e c2 não podem ser negativos.")

    def limitar(v: float) -> float:
        return max(-vmax, min(vmax, v))

    def desenhar(iteracao: int, anterior: list[int]) -> None:
        melhor = max(range(tamanho_enxame), key=lambda i: valores[i])
        debug.passo(
            "enxame",
            anterior,
            [(f"p{i + 1}", posicao) for i, posicao in enumerate(posicoes)],
            f"p{melhor + 1}",
        )
        debug.fim_iteracao(
            anterior,
            posicoes[melhor],
            valores[melhor],
            True,
            valores[melhor],
            gbest_valor,
            extras={"inercia": w} if iteracao else None,
        )

    if debug is not None:
        debug.inicio_iteracao("PSO", 0, ultima=max_iteracoes == 0)
    posicoes = [construtiva(itens, capacidade) for _ in range(tamanho_enxame)]
    valores = [avaliar(posicao, itens, capacidade) for posicao in posicoes]
    avaliacoes = tamanho_enxame
    velocidades = [
        [random.uniform(-vmax, vmax) for _ in itens] for _ in range(tamanho_enxame)
    ]
    pbest = [list(posicao) for posicao in posicoes]
    pbest_valor = list(valores)
    lider = max(range(tamanho_enxame), key=lambda i: valores[i])
    gbest, gbest_valor = list(posicoes[lider]), valores[lider]
    historico = novo_historico()
    registrar(
        historico,
        0,
        valor_candidato=statistics.mean(valores),
        valor_atual=max(valores),
        melhor_valor=gbest_valor,
        avaliacoes=avaliacoes,
    )
    w = inicial
    if debug is not None:
        desenhar(0, gbest)

    for iteracao in range(1, max_iteracoes + 1):
        if max_iteracoes > 1:
            w = inicial + (final - inicial) * (iteracao - 1) / (max_iteracoes - 1)
        if debug is not None:
            debug.inicio_iteracao("PSO", iteracao, ultima=iteracao == max_iteracoes)
        gbest_anterior = list(gbest)
        for i in range(tamanho_enxame):
            x = coordenadas(posicoes[i], itens, capacidade)
            p = coordenadas(pbest[i], itens, capacidade)
            g = coordenadas(gbest, itens, capacidade)
            velocidades[i] = [
                limitar(
                    w * v
                    + c1 * random.random() * (pj - xj)
                    + c2 * random.random() * (gj - xj)
                )
                for v, xj, pj, gj in zip(velocidades[i], x, p, g)
            ]
            posicoes[i] = mover(posicoes[i], itens, capacidade, velocidades[i])
            valores[i] = avaliar(posicoes[i], itens, capacidade)
            avaliacoes += 1
            if valores[i] > pbest_valor[i]:
                if busca_local is not None:
                    posicoes[i], examinadas = busca_local(
                        posicoes[i], itens, capacidade, debug=debug
                    )
                    valores[i] = avaliar(posicoes[i], itens, capacidade)
                    avaliacoes += examinadas + 1
                pbest[i], pbest_valor[i] = list(posicoes[i]), valores[i]
                if valores[i] > gbest_valor:
                    gbest, gbest_valor = list(posicoes[i]), valores[i]
        registrar(
            historico,
            iteracao,
            valor_candidato=statistics.mean(valores),
            valor_atual=max(valores),
            melhor_valor=gbest_valor,
            avaliacoes=avaliacoes,
            inercia=w,
        )
        if debug is not None:
            desenhar(iteracao, gbest_anterior)
    return gbest, historico
