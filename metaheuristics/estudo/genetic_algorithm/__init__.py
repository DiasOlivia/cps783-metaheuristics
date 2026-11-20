"""Genetic Algorithm (GA) for the 0-1 knapsack problem."""

import random
import statistics
from collections.abc import Callable

from metaheuristics.utils import binaria
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.selecao import selecao_roleta


def genetic_algorithm_mochila(
    itens: list[Item],
    capacidade: int,
    tamanho_populacao: int = 50,
    max_geracoes: int = 100,
    prob_cruzamento: float = 0.8,
    prob_mutacao: float = 0.05,
    intensidade_mutacao: int = 1,
    tamanho_elite: int = 2,
    avaliar: Callable = binaria.avaliar,
    construtiva: Callable = binaria.construtiva_aleatoria,
    cruzamento: Callable = binaria.cruzamento_uniforme,
    mutacao: Callable = binaria.gerar_vizinho,
    reparo: Callable | None = binaria.reparar,
    selecao_pais: Callable = selecao_roleta,
    selecao_sobreviventes: Callable = selecao_roleta,
    busca_local: Callable | None = None,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Solve the 0-1 knapsack problem with a Genetic Algorithm.

    At each generation, ``tamanho_populacao // 2`` pairs are tried: with
    probability ``prob_cruzamento``, a pair of parents chosen by ``selecao_pais``
    produces two children by ``cruzamento``. Then ``tamanho_populacao``
    mutations are tried: with probability ``prob_mutacao``, an individual chosen
    by ``selecao_pais`` produces a child by ``mutacao``. Every child goes through
    ``reparo`` and ``busca_local``, when given. The next population keeps the
    ``tamanho_elite`` best individuals of the current one and takes the others
    from the current population plus the children, by ``selecao_sobreviventes``.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    tamanho_populacao : int, default 50
        Number of individuals ``p``, at least 2.
    max_geracoes : int, default 100
        Number of generations; zero returns the best initial individual.
    prob_cruzamento : float, default 0.8
        Chance that each of the ``p // 2`` pairs is crossed.
    prob_mutacao : float, default 0.05
        Chance of each of the ``p`` mutation attempts.
    intensidade_mutacao : int, default 1
        The ``k`` passed to ``mutacao``.
    tamanho_elite : int, default 2
        Best individuals kept from one generation to the next (elitism).
    avaliar : callable, default binaria.avaliar
        Fitness, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_aleatoria
        Each initial individual, ``(itens, capacidade) -> solucao``.
    cruzamento : callable, default binaria.cruzamento_uniforme
        ``(pai1, pai2, itens, capacidade) -> (filho1, filho2)``.
    mutacao : callable, default binaria.gerar_vizinho
        ``(solucao, itens, capacidade, k, debug) -> solucao``.
    reparo : callable or None, default binaria.reparar
        Applied to every child, ``(solucao, itens, capacidade) -> solucao``;
        ``None`` for the order representation, which is always feasible.
    selecao_pais : callable, default selecao_roleta
        Chooses the parents, ``(valores, quantidade) -> [indices]``.
    selecao_sobreviventes : callable, default selecao_roleta
        Chooses the rest of the next population, with the same signature.
    busca_local : callable, optional
        Applied to every child after the repair,
        ``(solucao, itens, capacidade, debug) -> (solucao, avaliacoes)``.
    debug : Depurador, optional
        Draws the population and the result of each generation.

    Returns
    -------
    melhor_solucao : list of int
        Best individual evaluated, in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        Per generation, from 0 (the initial population): ``valor_candidato``
        (mean value of the population), ``valor_atual`` (best individual of the
        population), ``melhor_valor``, ``avaliacoes`` and ``distintos`` (number of
        different individuals in the population).
    """
    if tamanho_populacao < 2 or max_geracoes < 0:
        raise ValueError("tamanho_populacao >= 2 e max_geracoes >= 0.")
    if not (0 <= prob_cruzamento <= 1 and 0 <= prob_mutacao <= 1):
        raise ValueError("As probabilidades devem estar entre 0 e 1.")
    if not 0 <= tamanho_elite <= tamanho_populacao:
        raise ValueError("tamanho_elite deve estar entre 0 e tamanho_populacao.")

    def registrar_geracao(geracao: int) -> None:
        registrar(
            historico,
            geracao,
            valor_candidato=statistics.mean(valores),
            valor_atual=max(valores),
            melhor_valor=melhor_valor,
            avaliacoes=avaliacoes,
            distintos=len({tuple(individuo) for individuo in populacao}),
        )

    def desenhar(geracao: int, anterior: list[int]) -> None:
        lider = max(range(tamanho_populacao), key=valores.__getitem__)
        debug.passo(
            "população",
            anterior,
            [(f"i{i + 1}", individuo) for i, individuo in enumerate(populacao)],
            f"i{lider + 1}",
        )
        debug.fim_iteracao(
            anterior,
            populacao[lider],
            valores[lider],
            True,
            valores[lider],
            melhor_valor,
            extras={"distintos": historico["distintos"][geracao]},
        )

    if debug is not None:
        debug.inicio_iteracao("AG", 0, ultima=max_geracoes == 0)
    populacao = [construtiva(itens, capacidade) for _ in range(tamanho_populacao)]
    valores = [avaliar(individuo, itens, capacidade) for individuo in populacao]
    avaliacoes = tamanho_populacao
    lider = max(range(tamanho_populacao), key=valores.__getitem__)
    melhor_solucao, melhor_valor = list(populacao[lider]), valores[lider]
    historico = novo_historico()
    registrar_geracao(0)
    if debug is not None:
        desenhar(0, melhor_solucao)

    for geracao in range(1, max_geracoes + 1):
        if debug is not None:
            debug.inicio_iteracao("AG", geracao, ultima=geracao == max_geracoes)
        melhor_anterior = list(melhor_solucao)
        filhos = []
        for _ in range(tamanho_populacao // 2):
            if random.random() < prob_cruzamento:
                i, j = selecao_pais(valores, 2)
                filhos.extend(
                    cruzamento(populacao[i], populacao[j], itens, capacidade)
                )
        for _ in range(tamanho_populacao):
            if random.random() < prob_mutacao:
                (i,) = selecao_pais(valores, 1)
                filhos.append(
                    mutacao(
                        populacao[i],
                        itens,
                        capacidade,
                        intensidade_mutacao,
                        debug=debug,
                    )
                )
        valores_filhos = []
        for f, filho in enumerate(filhos):
            if reparo is not None:
                filho = reparo(filho, itens, capacidade)
            if busca_local is not None:
                filho, examinadas = busca_local(
                    filho, itens, capacidade, debug=debug
                )
                avaliacoes += examinadas
            filhos[f] = filho
            valores_filhos.append(avaliar(filho, itens, capacidade))
            avaliacoes += 1
            if valores_filhos[-1] > melhor_valor:
                melhor_solucao, melhor_valor = list(filho), valores_filhos[-1]

        # Como no slide 9, a elite sai da população atual, não dos filhos
        ranking = sorted(range(tamanho_populacao), key=lambda i: -valores[i])
        elite = ranking[:tamanho_elite]
        candidatos, valores_candidatos = populacao + filhos, valores + valores_filhos
        sobreviventes = selecao_sobreviventes(
            valores_candidatos, tamanho_populacao - tamanho_elite
        )
        populacao = [populacao[i] for i in elite] + [
            candidatos[i] for i in sobreviventes
        ]
        valores = [valores[i] for i in elite] + [
            valores_candidatos[i] for i in sobreviventes
        ]
        registrar_geracao(geracao)
        if debug is not None:
            desenhar(geracao, melhor_anterior)
    return melhor_solucao, historico
