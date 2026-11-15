"""Tabu Search for the 0-1 knapsack problem."""

import random
from collections.abc import Callable

from metaheuristics.utils import binaria
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item


def tabu_search_mochila(
    itens: list[Item],
    capacidade: int,
    tamanho_tabu: int | tuple[int, int] = 5,
    max_sem_melhora: int = 50,
    tau: float = 1.0,
    valor_alvo: float | None = None,
    avaliar: Callable = binaria.avaliar_penalizada,
    construtiva: Callable = binaria.construtiva_aleatoria,
    vizinhanca: Callable = binaria.vizinhanca_flip,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Solve the 0-1 knapsack problem with Tabu Search.

    Each iteration evaluates the whole neighborhood and moves to the best
    admissible neighbor, even if it is worse. A move is tabu while any item it
    changes is under quarantine (``prazo[i] >= iteracao``); after a move, its items
    stay tabu for ``|T|`` iterations. A tabu move is admissible when it beats the
    best solution (aspiration by objective); when no move is admissible, the one
    whose quarantine ends first is made (aspiration by default). Ties go to the
    first neighbor listed. The search stops after ``max_sem_melhora`` iterations
    without improving the best solution, or when it reaches ``valor_alvo``.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    tamanho_tabu : int or tuple of (int, int), default 5
        Tabu tenure ``|T|``. A pair ``(Tmin, Tmax)`` makes the list dynamic:
        ``|T|`` is drawn from that range at the first iteration and again every
        ``tau * Tmax`` iterations.
    max_sem_melhora : int, default 50
        ``BTmax``: iterations without improving the best solution before stopping.
    tau : float, default 1.0
        Period factor of the dynamic list; ignored when ``tamanho_tabu`` is an int.
    valor_alvo : float, optional
        Stop as soon as the best value reaches it, e.g. a known optimum.
    avaliar : callable, default binaria.avaliar_penalizada
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_aleatoria
        Initial solution, ``(itens, capacidade) -> solucao``.
    vizinhanca : callable, default binaria.vizinhanca_flip
        Every neighbor, ``(solucao, itens, capacidade) -> [(rotulo, itens_alterados,
        vizinha)]``; the changed items are the attributes that become tabu.
    debug : Depurador, optional
        Draws one figure per step. The last iteration is not known in advance, so
        it is drawn only when it falls on ``a_cada``.

    Returns
    -------
    melhor_solucao : list of int
        Best solution found, in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        ``valor_candidato`` and ``valor_atual`` (both the value of the chosen
        neighbor), ``melhor_valor``, ``avaliacoes`` (every neighbor counts) and
        ``tamanho_tabu`` per iteration; iteration 0 is the initial solution.
    """
    if isinstance(tamanho_tabu, int):
        minimo = maximo = tamanho_tabu
    else:
        minimo, maximo = tamanho_tabu
    if not 1 <= minimo <= maximo:
        raise ValueError("tamanho_tabu deve ser pelo menos 1, com Tmin <= Tmax.")
    if max_sem_melhora < 0:
        raise ValueError("max_sem_melhora não pode ser negativo.")
    if tau <= 0:
        raise ValueError("tau deve ser positivo.")
    periodo = max(1, round(tau * maximo))
    tamanho = minimo

    if debug is not None:
        debug.inicio_iteracao("BT", 0)
    atual = construtiva(itens, capacidade)
    valor_atual = avaliar(atual, itens, capacidade)
    avaliacoes = 1
    melhor_solucao, melhor_valor = list(atual), valor_atual
    prazo = [0] * len(itens)
    historico = novo_historico()
    registrar(
        historico,
        0,
        valor_candidato=valor_atual,
        valor_atual=valor_atual,
        melhor_valor=melhor_valor,
        avaliacoes=avaliacoes,
    )
    if debug is not None:
        debug.fim_iteracao(
            atual, atual, valor_atual, True, valor_atual, melhor_valor
        )

    iteracao = melhor_iteracao = 0
    while iteracao - melhor_iteracao <= max_sem_melhora:
        if valor_alvo is not None and melhor_valor >= valor_alvo:
            break
        vizinhas = vizinhanca(atual, itens, capacidade)
        if not vizinhas:
            break
        iteracao += 1
        if minimo < maximo and (iteracao - 1) % periodo == 0:
            tamanho = random.randint(minimo, maximo)
        if debug is not None:
            debug.inicio_iteracao("BT", iteracao)
        valores = [avaliar(vizinha, itens, capacidade) for _, _, vizinha in vizinhas]
        avaliacoes += len(vizinhas)
        tabu = [
            any(prazo[i] >= iteracao for i in alterados)
            for _, alterados, _ in vizinhas
        ]
        admissiveis = [
            k
            for k in range(len(vizinhas))
            if not tabu[k] or valores[k] > melhor_valor
        ]
        if admissiveis:
            escolhida = max(admissiveis, key=lambda k: valores[k])
            nota = "aspiração" if tabu[escolhida] else ""
        else:
            # Aspiração por default: o movimento cuja quarentena acaba primeiro
            escolhida = min(
                range(len(vizinhas)),
                key=lambda k: max(prazo[i] for i in vizinhas[k][1]),
            )
            nota = "todas tabu: a de prazo mais antigo"
        _, alterados, candidato = vizinhas[escolhida]
        for i in alterados:
            prazo[i] = iteracao + tamanho
        if debug is not None:
            rotulos = [
                f"{rotulo} (tabu)" if tabu[k] else rotulo
                for k, (rotulo, _, _) in enumerate(vizinhas)
            ]
            debug.passo(
                "vizinhança",
                atual,
                [(r, vizinha) for r, (_, _, vizinha) in zip(rotulos, vizinhas)],
                rotulos[escolhida],
                nota,
            )
        anterior = atual
        atual, valor_atual = candidato, valores[escolhida]
        if valor_atual > melhor_valor:
            melhor_solucao, melhor_valor = list(atual), valor_atual
            melhor_iteracao = iteracao
        registrar(
            historico,
            iteracao,
            valor_candidato=valor_atual,
            valor_atual=valor_atual,
            melhor_valor=melhor_valor,
            avaliacoes=avaliacoes,
            tamanho_tabu=tamanho,
        )
        if debug is not None:
            debug.fim_iteracao(
                anterior,
                candidato,
                valor_atual,
                True,
                valor_atual,
                melhor_valor,
                extras={"tamanho_tabu": tamanho},
                info={"nota": nota} if nota else None,
            )
    return melhor_solucao, historico
