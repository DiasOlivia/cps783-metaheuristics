from itertools import combinations

from metaheuristics.trabalho.debug import Debug
from metaheuristics.trabalho.protocol import Problem
from metaheuristics.trabalho.protocol import Solucao
from metaheuristics.utils.historico import Historico
from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar


def busca_local(problem: Problem, solucao: Solucao) -> tuple[Solucao, int]:
    """Busca local de primeira melhora que troca duas facilidades de posição na ordem.

    A ordem começa pelas abertas da ``solucao``, na ordem de abertura, seguidas das
    fechadas. Vizinhas inviáveis são ignoradas. Devolve o ótimo local e quantas
    vizinhas foram avaliadas.
    """
    facilidade_by_id = {f.id: f for f in problem.facilidades}
    abertas_ids = set(solucao.abertas)
    # ordem_facilidade = abertas + fechadas
    ordem_facilidades = [facilidade_by_id[f_id] for f_id in solucao.abertas]
    ordem_facilidades += [f for f in problem.facilidades if f.id not in abertas_ids]

    atual = solucao
    avaliacoes = 0
    melhorou = True
    while melhorou:
        melhorou = False
        for i, j in combinations(range(len(ordem_facilidades)), 2):
            if i >= len(atual.abertas):
                break

            vizinha = ordem_facilidades.copy()
            vizinha[i], vizinha[j] = vizinha[j], vizinha[i]
            avaliacoes += 1
            try:
                candidata = problem.decodificar(vizinha)
            except ValueError:
                continue

            if candidata.custo_total < atual.custo_total:
                ordem_facilidades, atual = vizinha, candidata
                melhorou = True
                break

    return atual, avaliacoes


def grasp(
    problem: Problem,
    alfa: float,
    max_iterations: int,
    debug: Debug | None = None,
) -> tuple[Solucao, Historico]:

    if alfa < 0 or alfa > 1:
        raise ValueError(f"O valor de alfa precisa estar entre 0 e 1, ele é {alfa}")

    historico = novo_historico()
    avaliacoes = 0
    melhor_solucao: Solucao | None = None

    for iteracao in range(1, max_iterations + 1):
        if debug is not None:
            debug.inicio_iteracao(problem, iteracao, max_iterations)

        try:
            construida = problem.gen_solucao_aleatoria_gulosa(alfa)
        except ValueError:
            continue

        avaliacoes += 1

        # a busca nunca piora a solucao
        melhorada, vizinhas = busca_local(problem, construida)
        avaliacoes += vizinhas

        if (
            melhor_solucao is None
            or melhorada.custo_total < melhor_solucao.custo_total
        ):
            melhor_solucao = melhorada

        if debug is not None:
            debug.fim_iteracao(construida, melhorada, melhor_solucao)

        registrar(
            historico,
            iteracao,
            valor_candidato=construida.custo_total,
            valor_atual=melhorada.custo_total,
            melhor_valor=melhor_solucao.custo_total,
            avaliacoes=avaliacoes,
        )

    if melhor_solucao is None:
        raise ValueError("Nenhuma construção do GRASP atendeu toda a demanda.")

    return melhor_solucao, historico
