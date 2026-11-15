import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.reconexao import atualizar_elite
from metaheuristics.utils.reconexao import reconectar


def _avaliar(solucao, *_):
    # [1, 1, 0, 0] é um pico escondido no meio do caminho
    return 10 if solucao == [1, 1, 0, 0] else sum(solucao)


def _reconectar(direcao):
    return reconectar(
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [],
        0,
        _avaliar,
        binaria.passos_para_guia,
        direcao,
    )


def test_reconectar__a_direcao_muda_o_caminho():
    # forward parte da pior ponta, (0000), e passa pelo pico
    assert _reconectar("forward") == ([1, 1, 0, 0], 10, 2 + 4 + 3 + 2)
    # backward parte da melhor, (1111), e desce por (0111), (0011), (0001)
    assert _reconectar("backward") == ([0, 1, 1, 1], 3, 2 + 4 + 3 + 2)


def test_reconectar__backward_forward_anda_pelas_duas_pontas():
    # (1111) → (0111); (0000) → (0100); (0111) → (0101); as pontas se encontram
    assert _reconectar("backward_forward") == ([0, 1, 1, 1], 3, 2 + 4 + 3 + 2)


def test_reconectar__vizinhas_nao_tem_intermediaria():
    resultado = reconectar([0, 0], [1, 0], [], 0, _avaliar, binaria.passos_para_guia)
    assert resultado == (None, None, 2)
    with pytest.raises(ValueError):
        reconectar([0], [1], [], 0, _avaliar, binaria.passos_para_guia, "lateral")


def test_atualizar_elite__regras_do_slide():
    def hamming(a, b):
        return sum(x != y for x, y in zip(a, b))

    elite = []

    def oferecer(solucao, valor):
        return atualizar_elite(elite, solucao, valor, 2, 2, hamming)

    assert oferecer([1, 0, 0, 0], 5)
    assert not oferecer([1, 0, 0, 0], 5)  # repetida
    assert oferecer([0, 1, 0, 0], 3)  # o pool ainda não estava cheio
    # supera a pior (3), mas está a distância 1 das duas: não entra
    assert not oferecer([1, 1, 0, 0], 4)
    # supera a pior e está longe das duas: substitui a pior
    assert oferecer([0, 0, 1, 1], 4)
    assert elite == [(5, [1, 0, 0, 0]), (4, [0, 0, 1, 1])]
    # supera a melhor: entra mesmo perto de (1000)
    assert oferecer([1, 0, 0, 1], 6)
    assert elite == [(5, [1, 0, 0, 0]), (6, [1, 0, 0, 1])]
