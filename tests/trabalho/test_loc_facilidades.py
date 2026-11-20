from pathlib import Path
import random

from metaheuristics.trabalho import Problem
from metaheuristics.trabalho import grasp
from metaheuristics.trabalho.debug import Debug
from metaheuristics.trabalho.debug import plot_grasp
from metaheuristics.trabalho.instance import load_instance_from_txt

PLOT = True


def test_loc_facilidade():
    seed = 0
    random.seed(seed)

    instance = load_instance_from_txt(Path(__file__).parent / "toy.txt")

    problem = Problem.gen_problem_from_instance(instance)

    melhor_solucao, historico = grasp(
        problem, 1.0, 100, debug=Debug(save=True, a_cada=10) if PLOT else None
    )

    # if PLOT:
    #     plot_grasp(historico, save=True)
