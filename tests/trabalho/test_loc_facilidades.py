import random
from pathlib import Path

from metaheuristics.trabalho import Problem
from metaheuristics.trabalho import grasp
from metaheuristics.trabalho.debug import Debug
from metaheuristics.trabalho.instance import load_instance_from_txt

PLOT = True


def test_loc_facilidade():
    seed = 0
    random.seed(seed)

    instance = load_instance_from_txt(Path(__file__).parent / "toy.txt")

    problem = Problem.gen_problem_from_instance(instance)

    melhor_solucao, historico = grasp(
        problem, 0.7, 100, debug=Debug(save=True) if PLOT else None
    )
