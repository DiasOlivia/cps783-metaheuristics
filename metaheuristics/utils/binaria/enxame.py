import math
import random

from metaheuristics.utils.instancia import Item


def coordenadas(
    solucao: list[int], itens: list[Item], capacidade: int
) -> list[float]:
    """Return the position of a binary particle: its bits, as numbers.

    Created for the PSO (particle position).

    Parameters
    ----------
    solucao : list of int
        Binary solution.
    itens : list of Item
        Items of the instance; unused, kept so every coordinate map shares one
        signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.

    Returns
    -------
    list of float
        One coordinate per item, 0 or 1.
    """
    return [float(bit) for bit in solucao]


def mover_sigmoide(
    solucao: list[int],
    itens: list[Item],
    capacidade: int,
    velocidade: list[float],
) -> list[int]:
    """Fly a binary particle: each bit is 1 with probability ``sigmoide(v)``.

    Created for the PSO (flight).

    In the binary PSO of Kennedy and Eberhart (1997), the velocity of an item is
    the tendency of its bit to be 1, and the new position depends on the velocity
    only. The result may not fit in the knapsack.

    Parameters
    ----------
    solucao : list of int
        Current binary solution, left unchanged; unused by this flight.
    itens : list of Item
        Items of the instance; unused, kept so every flight shares one signature.
    capacidade : int
        Knapsack capacity; unused, kept for the same reason.
    velocidade : list of float
        Velocity of each item.

    Returns
    -------
    list of int
        New binary solution.
    """
    # sigmoide(v) = (1 + tanh(v / 2)) / 2, sem estouro para |v| grande
    return [
        1 if random.random() < (1 + math.tanh(v / 2)) / 2 else 0 for v in velocidade
    ]
