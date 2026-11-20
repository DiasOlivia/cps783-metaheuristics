"""Adaptive Large Neighbourhood Search (ALNS) for the 0-1 knapsack problem."""

import random
from collections.abc import Callable
from collections.abc import Sequence

from metaheuristics.utils import binaria
from metaheuristics.utils.aceitacao import metropolis
from metaheuristics.utils.aceitacao import temperaturas
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar
from metaheuristics.utils.instancia import Item


def _roleta(pesos: list[float]) -> int:
    # Com todos os pesos zerados (fator_reacao = 1 sem pontos), o sorteio é uniforme
    opcoes = range(len(pesos))
    return random.choices(opcoes, weights=pesos if any(pesos) else None)[0]


def _atualizar_pesos(
    pesos: list[float], pontos: list[float], usos: list[int], fator_reacao: float
) -> list[float]:
    """Apply ``π ← (1 - r) π + r p / θ``; an operator not used keeps its weight."""
    return [
        (1 - fator_reacao) * peso + fator_reacao * ponto / vezes if vezes else peso
        for peso, ponto, vezes in zip(pesos, pontos, usos)
    ]


def adaptive_large_neighborhood_search_mochila(
    itens: list[Item],
    capacidade: int,
    temperatura_inicial: float,
    temperatura_minima: float,
    fator_resfriamento: float,
    remocoes: Sequence[Callable] = (
        binaria.remocao_aleatoria,
        binaria.remocao_pior,
        binaria.remocao_shaw,
    ),
    insercoes: Sequence[Callable] = (
        binaria.insercao_aleatoria,
        binaria.insercao_gulosa,
    ),
    grau_remocao: float = 0.2,
    tamanho_segmento: int = 100,
    fator_reacao: float = 0.1,
    pontuacoes: tuple[float, float, float] = (33, 13, 9),
    avaliar: Callable = binaria.avaliar,
    construtiva: Callable = binaria.construtiva_aleatoria,
    busca_local: Callable | None = None,
    aceitacao: Callable | None = None,
    debug: Depurador | None = None,
) -> tuple[list[int], Historico]:
    """Solve the 0-1 knapsack problem with Adaptive Large Neighbourhood Search.

    Each iteration draws one removal and one insertion operator by roulette
    wheel, proportionally to their weights, removes ``q`` items from the current
    solution and inserts items back. An improving candidate is always accepted; a
    worse or equal one goes through ``aceitacao`` and is accepted only if it was
    never generated before. Both operators earn ``pontuacoes[0]`` for a new best
    solution, ``pontuacoes[1]`` for a new improving one and ``pontuacoes[2]`` for
    a new worse one that was accepted. At the end of each segment, every operator
    used ``θ`` times with score ``p`` gets the weight ``(1 - r) * π + r * p / θ``.
    The temperature drops after every iteration, as in Ropke and Pisinger (2006),
    so the schedule defines the number of iterations.

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
        Multiplicative cooling factor applied after each iteration.
    remocoes : sequence of callable
        Removal operators, ``(solucao, itens, capacidade, k, debug) -> solucao``.
        Their names label the weights in the history, so they must differ.
    insercoes : sequence of callable
        Insertion operators, ``(solucao, itens, capacidade, debug) -> solucao``.
    grau_remocao : float, default 0.2
        Each iteration removes ``q`` items, drawn from
        ``[1, round(grau_remocao * len(itens))]``.
    tamanho_segmento : int, default 100
        Iterations per segment, after which the weights are updated.
    fator_reacao : float, default 0.1
        Reaction factor ``r`` in ``[0, 1]``: 0 keeps the weights, 1 replaces them
        by the mean score of the segment.
    pontuacoes : tuple of float, default (33, 13, 9)
        Scores ``(σ1, σ2, σ3)`` for a new best, a new improving and a new
        accepted worse candidate.
    avaliar : callable, default binaria.avaliar
        Solution value, ``(solucao, itens, capacidade) -> valor``.
    construtiva : callable, default binaria.construtiva_aleatoria
        Initial solution, ``(itens, capacidade) -> solucao``.
    busca_local : callable, optional
        Applied to each candidate after the insertion,
        ``(solucao, itens, capacidade, debug) -> (solucao, avaliacoes)``.
    aceitacao : callable, optional
        Acceptance rule ``(delta, iteracao) -> bool``; defaults to the Metropolis
        rule with one iteration per temperature.
    debug : Depurador, optional
        Draws one figure per step.

    Returns
    -------
    melhor_solucao : list of int
        Best solution found, in the representation of the pieces.
    historico : dict of {str: dict of {int: float}}
        ``valor_candidato``, ``valor_atual``, ``melhor_valor``, ``avaliacoes`` and
        ``temperatura`` per iteration, plus ``peso <operator>`` with the weight of
        each operator at the end of the iteration; iteration 0 is the initial
        solution.
    """
    if not remocoes or not insercoes:
        raise ValueError("É preciso ao menos uma remoção e uma inserção.")
    familias = (list(remocoes), list(insercoes))
    nomes = [operador.__name__ for familia in familias for operador in familia]
    if len(set(nomes)) != len(nomes):
        raise ValueError("Os operadores precisam ter nomes diferentes.")
    if not 0 < grau_remocao <= 1:
        raise ValueError("grau_remocao deve estar em (0, 1].")
    if tamanho_segmento < 1:
        raise ValueError("tamanho_segmento deve ser pelo menos 1.")
    if not 0 <= fator_reacao <= 1:
        raise ValueError("fator_reacao deve estar em [0, 1].")

    niveis = temperaturas(
        temperatura_inicial, temperatura_minima, fator_resfriamento
    )
    if aceitacao is None and niveis:
        aceitacao = metropolis(niveis, 1)
    total = len(niveis)
    if not itens and total > 0:
        raise ValueError("É necessário ao menos um item para remover e inserir.")
    q_maximo = max(1, round(grau_remocao * len(itens)))
    sigma_melhor, sigma_melhora, sigma_piora = pontuacoes
    pesos = [[1.0] * len(familia) for familia in familias]
    pontos = [[0.0] * len(familia) for familia in familias]
    usos = [[0] * len(familia) for familia in familias]

    def pesos_por_nome() -> dict[str, float]:
        return {
            f"peso {operador.__name__}": peso
            for familia, pesos_familia in zip(familias, pesos)
            for operador, peso in zip(familia, pesos_familia)
        }

    if debug is not None:
        debug.inicio_iteracao("ALNS", 0, ultima=total == 0)
    atual = construtiva(itens, capacidade)
    valor_atual = avaliar(atual, itens, capacidade)
    avaliacoes = 1
    melhor_solucao, melhor_valor = list(atual), valor_atual
    encontradas = {tuple(atual)}
    historico = novo_historico()
    registrar(
        historico,
        0,
        valor_candidato=valor_atual,
        valor_atual=valor_atual,
        melhor_valor=melhor_valor,
        avaliacoes=avaliacoes,
        **pesos_por_nome(),
    )
    if debug is not None:
        debug.fim_iteracao(
            atual, atual, valor_atual, True, valor_atual, melhor_valor
        )

    for iteracao in range(1, total + 1):
        temperatura = niveis[iteracao - 1]
        if debug is not None:
            debug.inicio_iteracao("ALNS", iteracao, ultima=iteracao == total)
        escolhidos = [_roleta(pesos_familia) for pesos_familia in pesos]
        remocao = familias[0][escolhidos[0]]
        insercao = familias[1][escolhidos[1]]
        q = random.randint(1, q_maximo)
        parcial = remocao(atual, itens, capacidade, q, debug=debug)
        candidato = insercao(parcial, itens, capacidade, debug=debug)
        if busca_local is not None:
            candidato, examinadas = busca_local(
                candidato, itens, capacidade, debug=debug
            )
            avaliacoes += examinadas
        valor_candidato = avaliar(candidato, itens, capacidade)
        avaliacoes += 1
        delta = valor_candidato - valor_atual
        nova = tuple(candidato) not in encontradas
        encontradas.add(tuple(candidato))
        anterior = atual
        # Piora ou empate só é aceita se a solução ainda não foi encontrada (slide 16)
        aceito = aceitacao(delta, iteracao) and (delta > 0 or nova)
        if aceito:
            atual, valor_atual = candidato, valor_candidato
        if valor_atual > melhor_valor:
            melhor_solucao, melhor_valor = list(atual), valor_atual
            pontuacao = sigma_melhor
        elif aceito and nova:
            pontuacao = sigma_melhora if delta > 0 else sigma_piora
        else:
            pontuacao = 0
        for familia, escolhido in enumerate(escolhidos):
            pontos[familia][escolhido] += pontuacao
            usos[familia][escolhido] += 1
        if iteracao % tamanho_segmento == 0:
            for familia in range(len(familias)):
                pesos[familia] = _atualizar_pesos(
                    pesos[familia], pontos[familia], usos[familia], fator_reacao
                )
                pontos[familia] = [0.0] * len(pontos[familia])
                usos[familia] = [0] * len(usos[familia])
        registrar(
            historico,
            iteracao,
            valor_candidato=valor_candidato,
            valor_atual=valor_atual,
            melhor_valor=melhor_valor,
            avaliacoes=avaliacoes,
            temperatura=temperatura,
            **pesos_por_nome(),
        )
        if debug is not None:
            info = getattr(aceitacao, "ultimo", None)
            if not aceito and not nova and delta <= 0:
                info = {**(info or {}), "nota": "já encontrada"}
            debug.fim_iteracao(
                anterior,
                candidato,
                valor_candidato,
                aceito,
                valor_atual,
                melhor_valor,
                extras={"temperatura": temperatura},
                info=info,
            )
    return melhor_solucao, historico
