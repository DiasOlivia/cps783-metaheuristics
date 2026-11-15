from metaheuristics.utils import binaria


def test_passos_para_guia__um_passo_por_bit_diferente():
    solucao = [1, 0, 1, 0]
    passos = binaria.passos_para_guia(solucao, [], 0, [0, 0, 1, 1])
    assert passos == [("−1", [0, 0, 1, 0]), ("+4", [1, 0, 1, 1])]
    assert binaria.passos_para_guia(solucao, [], 0, solucao) == []
    assert solucao == [1, 0, 1, 0]
