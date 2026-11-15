import math
import random

import pytest

from metaheuristics.utils.aceitacao import aceita_melhora
from metaheuristics.utils.aceitacao import metropolis
from metaheuristics.utils.aceitacao import temperaturas


def test_aceita_melhora__so_melhora_estrita():
    assert aceita_melhora(1, 1)
    assert not aceita_melhora(0, 1)
    assert not aceita_melhora(-5, 1)


def test_temperaturas__agenda_do_sa_do_curso():
    niveis = temperaturas(1000, 1, 0.9)
    assert len(niveis) == 66
    assert niveis[0] == 1000
    assert niveis[40] == pytest.approx(14.78, abs=0.005)
    with pytest.raises(ValueError):
        temperaturas(1000, 1, 1.5)


def test_metropolis__melhora_nao_sorteia():
    aceitar = metropolis([50.0], 10)
    estado = random.getstate()
    assert aceitar(3, 1)
    assert random.getstate() == estado


def test_metropolis__piora_aceita_com_chance_exp():
    aceitar = metropolis([100.0, 50.0], 10)
    random.seed(1)
    sorteio = random.uniform(0, 1)
    random.seed(1)
    aceito = aceitar(-76, 11)
    assert aceitar.ultimo["temperatura"] == 50.0
    assert aceitar.ultimo["chance"] == pytest.approx(math.exp(-76 / 50))
    assert aceito == (sorteio < math.exp(-76 / 50))


def test_metropolis__depois_do_ultimo_nivel_fica_na_ultima_temperatura():
    aceitar = metropolis([100.0, 50.0], 10)
    aceitar(-1, 999)
    assert aceitar.ultimo["temperatura"] == 50.0
