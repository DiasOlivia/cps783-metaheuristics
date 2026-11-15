import random

import pytest

from metaheuristics.simulated_annealing import simulated_annealing_mochila
from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

PLOT = False


def test_simulated_annealing_mochila__notebook_example():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)

    # a capacidade é definida pelo problema, nesse caso ela é cerca de metade do
    # peso total dos itens
    capacidade = sum(item.peso for item in itens) // 2

    # itens genéricos para simular um problema
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    melhor_solucao, historico = simulated_annealing_mochila(
        itens=itens,
        capacidade=capacidade,
        temperatura_inicial=1000,
        temperatura_minima=1,
        fator_resfriamento=0.9,
        iteracoes_por_temperatura=100,
    )
    melhor_valor = historico["melhor_valor"][6600]
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100

    assert len(historico["valor_candidato"]) == 6601  # inclui a solução inicial
    assert historico["temperatura"][4035] == pytest.approx(14.78, abs=0.005)
    assert (
        binaria.calcular_valor_peso(melhor_solucao, itens, capacidade)[1]
        <= capacidade
    )
    assert gap <= 5

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_simulated_annealing_mochila__representacao_por_ordem():
    random.seed(0)
    itens = gerar_instancia_aleatoria(20, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2

    melhor_ordem, historico = simulated_annealing_mochila(
        itens,
        capacidade,
        temperatura_inicial=100,
        temperatura_minima=1,
        fator_resfriamento=0.8,
        iteracoes_por_temperatura=20,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_aleatoria,
        movimento=ordem.gerar_vizinho,
    )
    valor, peso = binaria.calcular_valor_peso(
        ordem.decodificar(melhor_ordem, itens, capacidade), itens, capacidade
    )

    assert sorted(melhor_ordem) == list(range(20))
    assert peso <= capacidade
    assert valor == historico["melhor_valor"][max(historico["melhor_valor"])]
