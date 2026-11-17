import random

import pytest

from metaheuristics.adaptive_large_neighborhood_search import (
    adaptive_large_neighborhood_search_mochila,
)
from metaheuristics.ant_colony_optimization import ant_colony_optimization_mochila
from metaheuristics.genetic_algorithm import genetic_algorithm_mochila
from metaheuristics.grasp import grasp_mochila
from metaheuristics.iterated_local_search import iterated_local_search_mochila
from metaheuristics.particle_swarm_optimization import (
    particle_swarm_optimization_mochila,
)
from metaheuristics.simulated_annealing import simulated_annealing_mochila
from metaheuristics.tabu_search import tabu_search_mochila
from metaheuristics.utils import ordem
from metaheuristics.utils.debug import Depurador
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria


def _instancia():
    random.seed(3)
    itens = gerar_instancia_aleatoria(8, 20, 100)
    return itens, sum(item.peso for item in itens) // 2


def _iteracoes_salvas(pasta):
    return sorted({int(arquivo.name[:5]) for arquivo in pasta.glob("*.png")})


def test_depurador__desenha_so_as_iteracoes_multiplas_de_a_cada(tmp_path):
    itens, capacidade = _instancia()
    debug = Depurador(itens, capacidade, save=True, a_cada=5, pasta=tmp_path)
    random.seed(1)
    iterated_local_search_mochila(itens, capacidade, 12, 3, debug=debug)
    assert _iteracoes_salvas(tmp_path) == [0, 5, 10, 12]
    assert any("busca_local" in arquivo.name for arquivo in tmp_path.glob("*.png"))


def test_depurador__respeita_o_limite_e_avisa_uma_vez(tmp_path, capsys):
    itens, capacidade = _instancia()
    debug = Depurador(itens, capacidade, save=True, limite=3, pasta=tmp_path)
    random.seed(1)
    iterated_local_search_mochila(itens, capacidade, 5, 3, debug=debug)
    assert len(list(tmp_path.glob("*.png"))) == 3
    assert capsys.readouterr().out.count("limite de 3 figuras") == 1


def test_depurador__nao_muda_o_resultado(tmp_path):
    itens, capacidade = _instancia()
    random.seed(2)
    sem_debug = simulated_annealing_mochila(itens, capacidade, 50, 1, 0.5, 5)
    debug = Depurador(
        itens, capacidade, save=True, a_cada=4, limite=5, pasta=tmp_path
    )
    random.seed(2)
    com_debug = simulated_annealing_mochila(
        itens, capacidade, 50, 1, 0.5, 5, debug=debug
    )
    assert sem_debug == com_debug


def test_depurador__representacao_por_ordem(tmp_path):
    itens, capacidade = _instancia()
    debug = Depurador(
        itens,
        capacidade,
        decodificar=ordem.decodificar,
        save=True,
        a_cada=10,
        pasta=tmp_path,
    )
    random.seed(1)
    simulated_annealing_mochila(
        itens,
        capacidade,
        50,
        1,
        0.5,
        5,
        avaliar=ordem.avaliar,
        construtiva=ordem.construtiva_aleatoria,
        movimento=ordem.gerar_vizinho,
        debug=debug,
    )
    assert _iteracoes_salvas(tmp_path) == [0, 10, 20, 30]


def test_depurador__alns_desenha_remocao_e_insercao(tmp_path):
    itens, capacidade = _instancia()
    random.seed(2)
    sem_debug = adaptive_large_neighborhood_search_mochila(
        itens, capacidade, 50, 1, 0.8
    )
    debug = Depurador(
        itens, capacidade, save=True, a_cada=5, limite=12, pasta=tmp_path
    )
    random.seed(2)
    com_debug = adaptive_large_neighborhood_search_mochila(
        itens, capacidade, 50, 1, 0.8, debug=debug
    )
    nomes = [arquivo.name for arquivo in tmp_path.glob("*.png")]
    assert sem_debug == com_debug
    assert any("remocao" in nome for nome in nomes)
    assert any("insercao" in nome for nome in nomes)


def test_depurador__busca_tabu_desenha_a_vizinhanca(tmp_path):
    itens = [Item(4, 2), Item(5, 2), Item(7, 3), Item(9, 4), Item(6, 4)]
    parametros = {
        "tamanho_tabu": 1,
        "max_sem_melhora": 1,
        "construtiva": lambda *_: [0, 1, 0, 1, 0],
    }
    sem_debug = tabu_search_mochila(itens, 23, **parametros)
    debug = Depurador(itens, 23, save=True, pasta=tmp_path)
    com_debug = tabu_search_mochila(itens, 23, debug=debug, **parametros)
    nomes = [arquivo.name for arquivo in tmp_path.glob("*.png")]
    assert sem_debug == com_debug
    assert sum("vizinhanca" in nome for nome in nomes) == 5


def test_depurador__grasp_desenha_a_reconexao(tmp_path):
    # Na instância correlacionada os ótimos locais variam, e o PR tem caminho
    random.seed(3)
    itens = gerar_instancia_aleatoria(8, 20, 100, correlacionada=True)
    capacidade = sum(item.peso for item in itens) // 2
    random.seed(4)
    sem_debug = grasp_mochila(itens, capacidade, max_iteracoes=6, alfa=0.9)
    debug = Depurador(itens, capacidade, save=True, limite=60, pasta=tmp_path)
    random.seed(4)
    com_debug = grasp_mochila(
        itens, capacidade, max_iteracoes=6, alfa=0.9, debug=debug
    )
    nomes = [arquivo.name for arquivo in tmp_path.glob("*.png")]
    assert sem_debug == com_debug
    assert any("reconexao" in nome for nome in nomes)


def test_depurador__pso_desenha_o_enxame(tmp_path):
    itens, capacidade = _instancia()
    random.seed(5)
    sem_debug = particle_swarm_optimization_mochila(
        itens, capacidade, tamanho_enxame=6, max_iteracoes=4
    )
    debug = Depurador(itens, capacidade, save=True, a_cada=2, pasta=tmp_path)
    random.seed(5)
    com_debug = particle_swarm_optimization_mochila(
        itens, capacidade, tamanho_enxame=6, max_iteracoes=4, debug=debug
    )
    nomes = [arquivo.name for arquivo in tmp_path.glob("*.png")]
    assert sem_debug == com_debug
    assert sum("enxame" in nome for nome in nomes) == 3  # iterações 0, 2 e 4


def test_depurador__ag_desenha_a_populacao(tmp_path):
    itens, capacidade = _instancia()
    random.seed(5)
    sem_debug = genetic_algorithm_mochila(
        itens, capacidade, tamanho_populacao=6, max_geracoes=4, prob_mutacao=0.5
    )
    debug = Depurador(itens, capacidade, save=True, a_cada=2, pasta=tmp_path)
    random.seed(5)
    com_debug = genetic_algorithm_mochila(
        itens,
        capacidade,
        tamanho_populacao=6,
        max_geracoes=4,
        prob_mutacao=0.5,
        debug=debug,
    )
    nomes = [arquivo.name for arquivo in tmp_path.glob("*.png")]
    assert sem_debug == com_debug
    assert sum("populacao" in nome for nome in nomes) == 3  # gerações 0, 2 e 4
    assert any("movimento" in nome for nome in nomes)  # a mutação


def test_depurador__aco_desenha_as_formigas(tmp_path):
    itens, capacidade = _instancia()
    random.seed(5)
    sem_debug = ant_colony_optimization_mochila(
        itens, capacidade, numero_formigas=4, max_sem_melhora=3
    )
    debug = Depurador(itens, capacidade, save=True, a_cada=2, pasta=tmp_path)
    random.seed(5)
    com_debug = ant_colony_optimization_mochila(
        itens, capacidade, numero_formigas=4, max_sem_melhora=3, debug=debug
    )
    nomes = [arquivo.name for arquivo in tmp_path.glob("*.png")]
    pares = [t for t in sem_debug[1]["melhor_valor"] if t % 2 == 0]
    assert sem_debug == com_debug
    assert sum("formigas" in nome for nome in nomes) == len(pares)


def test_depurador__exige_show_ou_save():
    itens, capacidade = _instancia()
    with pytest.raises(ValueError):
        Depurador(itens, capacidade)
