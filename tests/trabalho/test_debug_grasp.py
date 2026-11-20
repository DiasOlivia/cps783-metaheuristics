import random
from pathlib import Path

import pytest

from metaheuristics.trabalho import grasp
from metaheuristics.trabalho.debug import Debug
from metaheuristics.trabalho.instance import load_instance_from_txt
from metaheuristics.trabalho.protocol import Problem


def _toy() -> Problem:
    instance = load_instance_from_txt(Path(__file__).parent / "toy.txt")
    return Problem.gen_problem_from_instance(instance)


def test_debug__a_cada_none_desenha_so_a_ultima(tmp_path):
    random.seed(0)
    _, historico = grasp(
        _toy(), 1.0, 30, debug=Debug(save=True, a_cada=None, pasta=tmp_path)
    )

    ultima = max(historico["valor_atual"])
    assert sorted(p.name for p in tmp_path.glob("*.png")) == [
        f"grasp_{ultima:05d}.png"
    ]


@pytest.mark.parametrize("seed", range(5))
def test_debug__sempre_desenha_a_ultima_bem_sucedida(tmp_path, seed):
    random.seed(seed)
    _, historico = grasp(
        _toy(), 1.0, 30, debug=Debug(save=True, a_cada=10, pasta=tmp_path)
    )

    ultima = max(historico["valor_atual"])
    assert (tmp_path / f"grasp_{ultima:05d}.png").exists()
