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

    problem = Problem.gen_problem(
        capacidades=[95, 30, 30, 35],
        custos_fixos=[600, 250, 430, 590],
        demandas=[10, 20, 8, 12, 23, 25, 16, 18, 13, 21],
        custo_transporte=[
            [23, 70, 45, 65],
            [43, 39, 37, 36],
            [57, 80, 38, 90],
            [30, 78, 54, 88],
            [36, 78, 70, 68],
            [47, 65, 39, 41],
            [99, 98, 80, 26],
            [40, 36, 19, 65],
            [86, 50, 53, 39],
            [72, 97, 89, 29],
        ],
        pares_conflitantes=[(2, 5), (1, 7), (4, 6)],
    )

    problem = Problem.gen_problem_from_instance(instance)

    melhor_solucao, historico = grasp(
        problem, 1.0, 100, debug=Debug(save=True, a_cada=10) if PLOT else None
    )

    if PLOT:
        plot_grasp(historico, save=True)
