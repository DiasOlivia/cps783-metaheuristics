import random

import pytest

from metaheuristics.estudo.iterated_local_search import iterated_local_search_mochila
from metaheuristics.utils.experimento import resumir
from metaheuristics.utils.experimento import rodar_sementes
from metaheuristics.utils.experimento import tabela
from metaheuristics.utils.instancia import gerar_instancia_aleatoria


def test_rodar_sementes__mesma_semente_mesmo_resultado():
    random.seed(0)
    itens = gerar_instancia_aleatoria(12, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    execucoes = rodar_sementes(
        iterated_local_search_mochila, itens, capacidade, [5, 5, 6], max_iteracoes=5
    )
    assert [e["semente"] for e in execucoes] == [5, 5, 6]
    assert execucoes[0]["historico"] == execucoes[1]["historico"]
    assert all(e["tempo"] >= 0 for e in execucoes)


def test_resumir__gap_e_avaliacoes_ate_o_melhor():
    def execucao(melhores, avaliacoes):
        return {
            "historico": {"melhor_valor": melhores, "avaliacoes": avaliacoes},
            "tempo": 1.0,
        }

    execucoes = [
        execucao({0: 80, 1: 100, 2: 100}, {0: 1, 1: 10, 2: 20}),
        execucao({0: 80, 1: 90}, {0: 1, 1: 30}),
    ]
    resumo = resumir(execucoes, 100)
    assert resumo["otimo_atingido"] == 1
    assert resumo["gap_medio"] == pytest.approx(5.0)
    assert resumo["gap_pior"] == pytest.approx(10.0)
    assert resumo["avaliacoes_ate_melhor"] == pytest.approx(20.0)
    assert resumo["avaliacoes_total"] == pytest.approx(25.0)


def test_tabela__uma_linha_por_combinacao():
    resumo = {
        "execucoes": 2,
        "otimo_atingido": 1,
        "gap_medio": 5.0,
        "gap_melhor": 0.0,
        "gap_pior": 10.0,
        "avaliacoes_ate_melhor": 20,
        "avaliacoes_total": 25,
        "tempo_medio": 1.0,
    }
    texto = tabela({"SA": resumo, "ILS": resumo})
    linhas = texto.splitlines()
    assert len(linhas) == 3
    assert linhas[1].startswith("SA")
