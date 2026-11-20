"""GRASP with path-relinking for the 0-1 knapsack problem."""

import random
from collections.abc import Callable
from collections.abc import Sequence

from metaheuristics.utils import binaria
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.reconexao import DIRECOES
from metaheuristics.utils.reconexao import atualizar_elite
from metaheuristics.utils.reconexao import reconectar


def grasp_mochila(
    itens: list[Item],
    capacidade: int,
    max_iteracoes: int = 50,
    alfa: float | Sequence[float] = 0.3,
    periodo_reativo: int = 10,
    hashing: bool = True,
    tamanho_elite: int = 5,
    diferenca_minima: int = 2,
    direcao: str = "backward",
    periodo_reconexao: int = 1,
    avaliar: Callable = binaria.avaliar,
    construtiva: Callable = binaria.construtiva_gulosa_aleatoria,
    busca_local: Callable | None = binaria.busca_local_primeira_melhora,
    reconexao: Callable | None = binaria.passos_para_guia,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Solve the 0-1 knapsack problem with GRASP and path-relinking.

    Each iteration builds a solution with the greedy randomized ``construtiva``
    and improves it with ``busca_local``. With ``reconexao``, the result is
    relinked with a solution drawn from the elite pool, and the best solution on
    the path replaces it when better; then the result is offered to the pool.
    With ``reconexao=None`` this is pure GRASP.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    max_iteracoes : int, default 50
        Number of GRASP iterations (at least 1).
    alfa : float or sequence of float, default 0.3
        RCL parameter in ``[0, 1]``. A sequence makes GRASP reactive: each
        iteration draws one value, with probabilities proportional to
        ``mean value / best value`` of the solutions found with it, recomputed
        every ``periodo_reativo`` iterations (unused values count as 1).
    periodo_reativo : int, default 10
        Iterations between updates of the probabilities of reactive GRASP.
    hashing : bool, default True
        Reuse the local optimum of a constructed solution seen before instead of
        running the local search again.
    tamanho_elite : int, default 5
        Capacity of the elite pool.
    diferenca_minima : int, default 2
        Smallest distance to the pool for a solution that does not beat its best.
    direcao : {'backward', 'forward', 'backward_forward'}, default 'backward'
        Where path-relinking starts: the better end, the worse end or both.
    periodo_reconexao : int, default 1
        Apply path-relinking every ``periodo_reconexao`` iterations.
    avaliar : callable, default binaria.avaliar
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_gulosa_aleatoria
        Greedy randomized construction, ``(itens, capacidade, alfa) -> solucao``.
    busca_local : callable or None, default binaria.busca_local_primeira_melhora
        ``(solucao, itens, capacidade, debug) -> (solucao, avaliacoes)``; None
        skips the local search.
    reconexao : callable or None, default binaria.passos_para_guia
        Moves towards a guide, ``(solucao, itens, capacidade, guia) ->
        [(rotulo, vizinha)]``; None turns path-relinking off.
    debug : Depurador, optional
        Draws one figure per step.

    Returns
    -------
    melhor_solucao : list of int
        Best solution found, in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        Per iteration, from 1: ``valor_candidato`` (the constructed solution),
        ``valor_atual`` (after local search and path-relinking),
        ``melhor_valor``, ``avaliacoes`` and ``alfa``.
    """
    alfas = [alfa] if isinstance(alfa, (int, float)) else list(alfa)
    if not alfas or any(not 0 <= a <= 1 for a in alfas):
        raise ValueError("alfa deve estar entre 0 e 1.")
    if max_iteracoes < 1:
        raise ValueError("max_iteracoes deve ser pelo menos 1.")
    if tamanho_elite < 1 or diferenca_minima < 0:
        raise ValueError("tamanho_elite >= 1 e diferenca_minima >= 0.")
    if periodo_reativo < 1 or periodo_reconexao < 1:
        raise ValueError("Os períodos devem ser pelo menos 1.")
    if direcao not in DIRECOES:
        raise ValueError(f"direcao deve ser uma de {DIRECOES}.")

    probabilidades = [1 / len(alfas)] * len(alfas)
    somas = [0.0] * len(alfas)
    usos = [0] * len(alfas)
    elite = []
    otimos_locais = {}
    melhor_solucao, melhor_valor = None, None
    avaliacoes = 0
    historico = novo_historico()

    def distancia(a: list[int], b: list[int]) -> int:
        return len(reconexao(a, itens, capacidade, b))

    for iteracao in range(1, max_iteracoes + 1):
        if debug is not None:
            debug.inicio_iteracao(
                "GRASP", iteracao, ultima=iteracao == max_iteracoes
            )
        k = (
            random.choices(range(len(alfas)), probabilidades)[0]
            if len(alfas) > 1
            else 0
        )
        construida = construtiva(itens, capacidade, alfas[k])
        valor_construida = avaliar(construida, itens, capacidade)
        avaliacoes += 1
        notas = []
        chave = tuple(construida)
        if hashing and chave in otimos_locais:
            solucao = list(otimos_locais[chave])
            notas.append("hashing: busca local reaproveitada")
        else:
            solucao = construida
            if busca_local is not None:
                solucao, examinadas = busca_local(
                    construida, itens, capacidade, debug=debug
                )
                avaliacoes += examinadas
            if hashing:
                otimos_locais[chave] = list(solucao)
        valor = avaliar(solucao, itens, capacidade)
        avaliacoes += 1
        somas[k] += valor
        usos[k] += 1

        if reconexao is not None:
            if elite and iteracao % periodo_reconexao == 0:
                guia = random.choice(elite)[1]
                caminho, valor_caminho, examinadas = reconectar(
                    solucao,
                    guia,
                    itens,
                    capacidade,
                    avaliar,
                    reconexao,
                    direcao,
                    debug,
                )
                avaliacoes += examinadas
                if caminho is not None and valor_caminho > valor:
                    notas.append(f"PR melhorou: {valor} → {valor_caminho}")
                    solucao, valor = caminho, valor_caminho
            atualizar_elite(
                elite, solucao, valor, tamanho_elite, diferenca_minima, distancia
            )

        if melhor_valor is None or valor > melhor_valor:
            melhor_solucao, melhor_valor = list(solucao), valor
        if len(alfas) > 1 and iteracao % periodo_reativo == 0 and melhor_valor > 0:
            q = [
                somas[i] / usos[i] / melhor_valor if usos[i] else 1.0
                for i in range(len(alfas))
            ]
            probabilidades = [qi / sum(q) for qi in q]
        registrar(
            historico,
            iteracao,
            valor_candidato=valor_construida,
            valor_atual=valor,
            melhor_valor=melhor_valor,
            avaliacoes=avaliacoes,
            alfa=alfas[k],
        )
        if debug is not None:
            debug.fim_iteracao(
                construida,
                solucao,
                valor,
                True,
                valor,
                melhor_valor,
                extras={"alfa": alfas[k]},
                info={"nota": " · ".join(notas)} if notas else None,
            )
    return melhor_solucao, historico
