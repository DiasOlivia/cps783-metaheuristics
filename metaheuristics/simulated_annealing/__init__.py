from collections.abc import Callable

from metaheuristics.utils import binaria
from metaheuristics.utils.aceitacao import metropolis
from metaheuristics.utils.aceitacao import temperaturas
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item


def simulated_annealing_mochila(
    itens: list[Item],
    capacidade: int,
    temperatura_inicial: float,
    temperatura_minima: float,
    fator_resfriamento: float,
    iteracoes_por_temperatura: int,
    avaliar: Callable = binaria.avaliar,
    construtiva: Callable = binaria.construtiva_aleatoria,
    movimento: Callable = binaria.gerar_vizinho,
    intensidade_movimento: int = 1,
    busca_local: Callable | None = None,
    aceitacao: Callable | None = None,
    verbose: bool = False,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Solve the 0-1 knapsack problem with simulated annealing.

    Each iteration generates a candidate with ``movimento``, optionally improves
    it with ``busca_local``, and accepts it according to ``aceitacao``. The
    temperature schedule (geometric, from ``temperatura_inicial`` down to
    ``temperatura_minima``) defines the number of iterations. The default pieces
    are the binary ones; pass the pieces of another representation to change it.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    temperatura_inicial : float
        Starting temperature.
    temperatura_minima : float
        Temperature at or below which the search stops.
    fator_resfriamento : float
        Multiplicative cooling factor applied after each temperature level.
    iteracoes_por_temperatura : int
        Number of iterations per temperature level.
    avaliar : callable, default binaria.avaliar
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_aleatoria
        Initial solution, ``(itens, capacidade) -> solucao``.
    movimento : callable, default binaria.gerar_vizinho
        Candidate generator, ``(solucao, itens, capacidade, k) -> solucao``.
    intensidade_movimento : int, default 1
        The ``k`` passed to the move.
    busca_local : callable, optional
        Applied to each candidate before the decision,
        ``(solucao, itens, capacidade, debug) -> (solucao, avaliacoes)``.
    aceitacao : callable, optional
        Acceptance rule ``(delta, iteracao) -> bool``; defaults to the Metropolis
        rule with the temperature schedule above.
    verbose : bool, default False
        Whether to print the initial solution and every improvement.
    debug : Depurador, optional
        Draws one figure per step.

    Returns
    -------
    melhor_solucao : list of int
        Best solution found, in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        ``valor_candidato``, ``valor_atual``, ``melhor_valor``, ``avaliacoes`` and
        ``temperatura`` per iteration; iteration 0 is the initial solution.
    """
    niveis = temperaturas(
        temperatura_inicial, temperatura_minima, fator_resfriamento
    )
    if aceitacao is None and niveis:
        aceitacao = metropolis(niveis, iteracoes_por_temperatura)
    total = len(niveis) * iteracoes_por_temperatura

    if debug is not None:
        debug.inicio_iteracao("SA", 0, ultima=total == 0)
    atual = construtiva(itens, capacidade)
    valor_atual = avaliar(atual, itens, capacidade)
    avaliacoes = 1
    melhor_solucao, melhor_valor = list(atual), valor_atual
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
    if verbose:
        print("\n--- Solução Inicial ---")
        print(f"Solução Inicial: {melhor_solucao}")
        print(f"Valor Inicial: {melhor_valor}")
        print("\n--- Iterações SA ---")

    for iteracao in range(1, total + 1):
        temperatura = niveis[(iteracao - 1) // iteracoes_por_temperatura]
        if debug is not None:
            debug.inicio_iteracao("SA", iteracao, ultima=iteracao == total)
        candidato = movimento(atual, itens, capacidade, intensidade_movimento)
        if busca_local is not None:
            candidato, examinadas = busca_local(
                candidato, itens, capacidade, debug=debug
            )
            avaliacoes += examinadas
        valor_candidato = avaliar(candidato, itens, capacidade)
        avaliacoes += 1
        anterior = atual
        aceito = aceitacao(valor_candidato - valor_atual, iteracao)
        if aceito:
            atual, valor_atual = candidato, valor_candidato
        if valor_atual > melhor_valor:
            melhor_solucao, melhor_valor = list(atual), valor_atual
            if verbose:
                print(
                    f"Iteração {iteracao}, Temperatura {temperatura:.2f}: "
                    f"valor = {melhor_valor}, solução = {melhor_solucao}"
                )
        registrar(
            historico,
            iteracao,
            valor_candidato=valor_candidato,
            valor_atual=valor_atual,
            melhor_valor=melhor_valor,
            avaliacoes=avaliacoes,
            temperatura=temperatura,
        )
        if debug is not None:
            debug.fim_iteracao(
                anterior,
                candidato,
                valor_candidato,
                aceito,
                valor_atual,
                melhor_valor,
                extras={"temperatura": temperatura},
                info=getattr(aceitacao, "ultimo", None),
            )
    return melhor_solucao, historico
