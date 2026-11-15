from metaheuristics.utils import ordem


def test_passos_para_guia__cada_passo_coloca_um_item_da_guia():
    solucao, guia = [0, 1, 2, 3], [2, 3, 0, 1]
    passos = ordem.passos_para_guia(solucao, [], 0, guia)
    assert len(passos) == 4
    for rotulo, nova in passos:
        posicao, item = (int(parte) - 1 for parte in rotulo.split("←"))
        assert guia[posicao] == item == nova[posicao]
        assert sorted(nova) == [0, 1, 2, 3]
    assert ordem.passos_para_guia(guia, [], 0, guia) == []
