import random

import pytest

from metaheuristics.iterated_local_search import iterated_local_search_mochila
from metaheuristics.simulated_annealing import simulated_annealing_mochila
from metaheuristics.utils import ordem
from metaheuristics.utils.debug import Depurador
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


def test_depurador__exige_show_ou_save():
    itens, capacidade = _instancia()
    with pytest.raises(ValueError):
        Depurador(itens, capacidade)
