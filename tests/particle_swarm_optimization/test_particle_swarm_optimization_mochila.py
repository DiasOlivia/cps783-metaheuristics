"""Pytest tests for PSO on the 0-1 knapsack problem."""

import itertools
import random

import pytest

from metaheuristics.particle_swarm_optimization import (
    particle_swarm_optimization_mochila,
)
from metaheuristics.utils import binaria
from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria
from metaheuristics.utils.instancia import programacao_dinamica
from metaheuristics.utils.plot import plotar_historico

PLOT = False


def _instancia(n=20):
    random.seed(0)
    itens = gerar_instancia_aleatoria(n, 20, 100)
    return itens, sum(item.peso for item in itens) // 2


def test_particle_swarm_optimization_mochila__instancia_de_referencia():
    """Benchmark the same 20-item seed-0 instance as the other schemes."""
    itens, capacidade = _instancia()
    valor_otimo, _ = programacao_dinamica(itens, capacidade)

    random.seed(1)
    melhor_solucao, historico = particle_swarm_optimization_mochila(
        itens, capacidade
    )
    melhor_valor, peso = binaria.calcular_valor_peso(
        melhor_solucao, itens, capacidade
    )
    gap = (valor_otimo - melhor_valor) / valor_otimo * 100 if valor_otimo else 0
    melhores = list(historico["melhor_valor"].values())

    assert sorted(historico["valor_atual"]) == list(range(101))
    assert set(historico["inercia"].values()) == {1.0}
    assert historico["avaliacoes"][100] == 20 * 101
    assert peso <= capacidade
    assert melhor_valor == historico["melhor_valor"][100]
    assert all(b >= a for a, b in itertools.pairwise(melhores))
    assert gap <= 5

    if PLOT:
        plotar_historico(historico, valor_otimo, save=True)


def test_velocidade_limitada_por_vmax():
    itens, capacidade = _instancia()
    velocidades = []

    def mover(solucao, itens, capacidade, velocidade):
        velocidades.append(velocidade)
        return binaria.mover_sigmoide(solucao, itens, capacidade, velocidade)

    random.seed(1)
    particle_swarm_optimization_mochila(
        itens, capacidade, tamanho_enxame=5, max_iteracoes=10, vmax=2, mover=mover
    )
    componentes = [v for velocidade in velocidades for v in velocidade]

    assert all(abs(v) <= 2 for v in componentes)
    assert any(abs(v) == 2 for v in componentes)  # o limite foi usado


def test_inercia_decrescente():
    itens, capacidade = _instancia()
    random.seed(1)
    _, historico = particle_swarm_optimization_mochila(
        itens, capacidade, max_iteracoes=7, inercia=(1.0, 0.4)
    )
    inercias = [historico["inercia"][t] for t in range(1, 8)]

    assert inercias[0] == pytest.approx(1.0)
    assert inercias[-1] == pytest.approx(0.4)
    assert all(b < a for a, b in itertools.pairwise(inercias))


def test_busca_local_no_pbest():
    itens, capacidade = _instancia()
    random.seed(1)
    solucao, historico = particle_swarm_optimization_mochila(
        itens,
        capacidade,
        max_iteracoes=10,
        busca_local=binaria.busca_local_primeira_melhora,
    )

    assert binaria.calcular_valor_peso(solucao, itens, capacidade)[1] <= capacidade
    assert historico["avaliacoes"][10] > 20 * 11


def test_particle_swarm_optimization_mochila__representacao_por_ordem():
    itens, capacidade = _instancia(12)

    random.seed(1)
    melhor_ordem, historico = particle_swarm_optimization_mochila(
        itens,
        capacidade,
        max_iteracoes=20,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_aleatoria,
        coordenadas=ordem.coordenadas,
        mover=ordem.mover_chaves,
    )
    valor, peso = binaria.calcular_valor_peso(
        ordem.decodificar(melhor_ordem, itens, capacidade), itens, capacidade
    )

    assert sorted(melhor_ordem) == list(range(12))
    assert peso <= capacidade
    assert valor == historico["melhor_valor"][20]


def test_zero_iteracoes_devolve_a_melhor_particula_inicial():
    itens, capacidade = _instancia()
    random.seed(1)
    solucao, historico = particle_swarm_optimization_mochila(
        itens, capacidade, max_iteracoes=0
    )
    assert list(historico["melhor_valor"]) == [0]
    assert (
        binaria.avaliar(solucao, itens, capacidade) == historico["melhor_valor"][0]
    )


def test_parametros_invalidos():
    itens = [Item(1, 2), Item(2, 3)]
    for parametros in (
        {"tamanho_enxame": 0},
        {"max_iteracoes": -1},
        {"vmax": 0},
        {"inercia": -0.1},
        {"c1": -1},
    ):
        with pytest.raises(ValueError):
            particle_swarm_optimization_mochila(itens, 2, **parametros)
