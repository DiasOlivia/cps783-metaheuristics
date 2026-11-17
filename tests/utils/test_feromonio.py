import pytest

from metaheuristics.utils.feromonio import Feromonio


def test_feromonio__componente_novo_vale_o_fundo():
    tau = Feromonio(2.0)
    assert tau[7] == 2.0
    assert tau[(None, 3)] == 2.0
    assert len(tau) == 0  # ler não guarda o componente


def test_feromonio__evaporar_reduz_guardados_e_fundo():
    tau = Feromonio(1.0)
    tau[1] += 3.0
    tau.evaporar(0.5)
    assert tau[1] == pytest.approx(2.0)
    assert tau[2] == pytest.approx(0.5)


def test_feromonio__exemplo_do_slide_27():
    # τ35 = (1 − 0,5)·1 + 1/9,8 + 1/9,8 + 1/12,4
    tau = Feromonio(1.0)
    tau.evaporar(0.5)
    for comprimento in (9.8, 9.8, 12.4):
        tau[(3, 5)] += 1 / comprimento
    assert tau[(3, 5)] == pytest.approx(0.785, abs=0.001)
