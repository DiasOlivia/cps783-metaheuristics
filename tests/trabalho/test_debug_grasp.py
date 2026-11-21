from typing import Any

import numpy as np

from metaheuristics.trabalho.debug import Debug

# Solução ótima da toy (custo 7.932): uma linha por cliente, uma coluna por facilidade
ALOCACAO_OTIMA = np.array(
    [
        [10, 0, 0, 0],
        [0, 17, 3, 0],
        [8, 0, 0, 0],
        [12, 0, 0, 0],
        [23, 0, 0, 0],
        [0, 0, 25, 0],
        [0, 0, 0, 16],
        [16, 0, 2, 0],
        [0, 13, 0, 0],
        [2, 0, 0, 19],
    ]
)
ABERTAS = (ALOCACAO_OTIMA.sum(axis=0) > 0).astype(int)
SOLUCAO = (ALOCACAO_OTIMA, ABERTAS, 7932)


def _rodar(
    debug: Debug,
    notebook: dict[str, Any],
    metodo: str,
    iteracoes: range,
    total: int | None,
) -> None:
    debug.iniciar(
        notebook["instance"],
        metodo,
        "reinício",
        ("construída", "fim da busca"),
        total,
    )
    for iteracao in iteracoes:
        debug.inicio_iteracao(iteracao)
        debug.fim_iteracao(SOLUCAO, SOLUCAO, SOLUCAO)
    debug.fim()


def test_debug_desenha_cada_iteracao_com_o_nome_do_metodo(notebook, tmp_path):
    debug = Debug(save=True, a_cada=1, pasta=tmp_path)

    _rodar(debug, notebook, "GRASP + SA com grafos", range(1, 3), total=2)

    assert sorted(png.name for png in tmp_path.glob("*.png")) == [
        "grasp_sa_com_grafos_00001.png",
        "grasp_sa_com_grafos_00002.png",
    ]


def test_debug_sem_a_cada_desenha_so_a_ultima_iteracao(notebook, tmp_path):
    debug = Debug(save=True, pasta=tmp_path)

    _rodar(debug, notebook, "GRASP", range(1, 4), total=3)

    assert [png.name for png in tmp_path.glob("*.png")] == ["grasp_00003.png"]


def test_debug_sem_total_desenha_a_primeira_e_a_ultima(notebook, tmp_path):
    debug = Debug(save=True, a_cada=10, pasta=tmp_path)

    _rodar(debug, notebook, "Gulosa com reinícios", range(4), total=None)

    assert sorted(png.name for png in tmp_path.glob("*.png")) == [
        "gulosa_com_reinicios_00000.png",
        "gulosa_com_reinicios_00003.png",
    ]
