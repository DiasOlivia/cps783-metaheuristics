from datetime import datetime

import pytest

from metaheuristics.trabalho.debug import Debug
from metaheuristics.utils.plot import PASTA_PLOTS

# Ligue para salvar as figuras em plots/debug/<data-hora>/<método>/ e ver o que cada
# método faz; desligado, o teste só desenha a última iteração, numa pasta temporária
PLOT = True
# O mesmo orçamento da comparação do notebook
ORCAMENTO = 400
# Com PLOT ligado, iterações entre figuras: a gulosa faz centenas de tentativas, e os
# outros métodos, poucos reinícios ou gerações
A_CADA = {
    "executar_gulosa_cflp": 25,
    "grasp_cflp": 1,
    "grasp_sa_cflp": 1,
    "grasp_sa_grafos": 1,
    "algoritmo_genetico_cflp": 1,
}
PASTA_EXECUCAO = PASTA_PLOTS / "debug" / f"{datetime.now():%Y%m%d_%H%M%S}"


@pytest.mark.parametrize(
    "metodo",
    [
        "executar_gulosa_cflp",
        "grasp_cflp",
        "grasp_sa_cflp",
        "grasp_sa_grafos",
        "algoritmo_genetico_cflp",
    ],
)
def test_debug_desenha_o_metodo_sem_mudar_o_resultado(notebook, metodo, tmp_path):
    executar = notebook[metodo]
    instance = notebook["instance"]
    pasta = PASTA_EXECUCAO / metodo if PLOT else tmp_path
    debug = Debug(save=True, a_cada=A_CADA[metodo] if PLOT else None, pasta=pasta)

    com_debug = executar(instance, seed=42, max_avaliacoes=ORCAMENTO, debug=debug)
    sem_debug = executar(instance, seed=42, max_avaliacoes=ORCAMENTO)

    assert com_debug[2] == sem_debug[2]
    assert list(pasta.glob("*.png"))
