from metaheuristics.utils.historico import novo_historico
from metaheuristics.utils.historico import registrar


def test_registrar__chaves_comuns_e_extras():
    historico = novo_historico()
    registrar(
        historico,
        0,
        valor_candidato=5,
        valor_atual=5,
        melhor_valor=5,
        avaliacoes=1,
        k=0,
    )
    registrar(
        historico,
        1,
        valor_candidato=7,
        valor_atual=7,
        melhor_valor=7,
        avaliacoes=2,
        k=1,
    )
    assert historico["valor_atual"] == {0: 5, 1: 7}
    assert historico["k"] == {0: 0, 1: 1}
