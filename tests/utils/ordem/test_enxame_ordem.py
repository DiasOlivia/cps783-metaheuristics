from metaheuristics.utils import ordem


def test_coordenadas__o_primeiro_tem_a_maior_chave():
    # ordem (2, 0, 1): o item 2 tem chave 3, o 0 tem 2 e o 1 tem 1
    assert ordem.coordenadas([2, 0, 1], [], 0) == [2.0, 1.0, 3.0]


def test_mover_chaves__a_velocidade_adianta_o_item():
    solucao = [2, 0, 1]
    assert ordem.mover_chaves(solucao, [], 0, [0, 0, 0]) == [2, 0, 1]
    # o item 1 (chave 1) com v = +3 passa à frente de todos (chave 4)
    assert ordem.mover_chaves(solucao, [], 0, [0, 3, 0]) == [1, 2, 0]
    # com v = +1 ele empata com o item 0, e o empate mantém a ordem atual
    assert ordem.mover_chaves(solucao, [], 0, [0, 1, 0]) == [2, 0, 1]
    assert solucao == [2, 0, 1]
