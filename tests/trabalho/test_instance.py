import random
from pathlib import Path

import pytest

TOY = Path(__file__).parent / "toy.txt"


def test_load_instance_from_txt_le_a_toy(notebook):
    instance = notebook["load_instance_from_txt"](TOY)

    assert (instance.n_clientes, instance.n_facilidades) == (10, 4)
    assert (instance.n_clientes, instance.n_facilidades) == (instance.I, instance.J)
    assert instance.pares_conflitantes_0based == [(1, 4), (0, 6), (3, 5)]


def test_gen_random_instance_reproduz_com_a_mesma_semente(notebook):
    random.seed(7)
    primeira = notebook["Instance"].gen_random_instance()
    random.seed(7)
    segunda = notebook["Instance"].gen_random_instance()

    assert (primeira.capacidades == segunda.capacidades).all()
    assert (primeira.custos_transporte == segunda.custos_transporte).all()
    assert primeira.pares_conflitantes_brutos == segunda.pares_conflitantes_brutos


@pytest.mark.parametrize("seed", range(20))
def test_gen_random_instance_gera_instancia_valida(notebook, seed):
    random.seed(seed)

    instance = notebook["Instance"].gen_random_instance(
        n_facilidades=3, n_clientes=8, max_capacidade=40, n_conflitos=6
    )

    assert instance.capacidades.sum() >= instance.demandas.sum()
    pares = [tuple(par) for par in instance.pares_conflitantes_brutos]
    assert len(set(pares)) == len(pares) == 6
    assert all(1 <= cliente < outro_cliente <= 8 for cliente, outro_cliente in pares)


def test_gen_random_instance_recusa_capacidade_impossivel(notebook):
    with pytest.raises(ValueError):
        notebook["Instance"].gen_random_instance(
            n_facilidades=1, n_clientes=10, max_capacidade=5
        )
