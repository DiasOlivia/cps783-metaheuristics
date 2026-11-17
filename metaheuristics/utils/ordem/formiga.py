from metaheuristics.utils.binaria.formiga import _sequencia_formiga
from metaheuristics.utils.feromonio import Feromonio
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.ordem.avaliacao import decodificar


def construtiva_formiga(
    itens: list[Item],
    capacidade: int,
    feromonio: Feromonio | None = None,
    alfa: float = 1.0,
    beta: float = 1.0,
    q0: float = 0.0,
) -> list[int]:
    """Build an order the way an ant does, with pheromone per transition.

    As in the traveling salesman, the pheromone sits on the move from the last
    chosen item ``i`` to the next one ``j``, the component ``(i, j)``; the first
    item comes from ``None``. While some item fits, the next one is drawn among
    those that fit with probability proportional to ``τ_ij^α η_j^β``, where
    ``η_j`` is its value-to-weight ratio; with probability ``q0`` the ant takes
    the largest ``τ_ij η_j^β`` instead. The items that did not fit come after,
    by non-increasing ratio.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    feromonio : Feromonio, optional
        Pheromone of each transition; without it, ``τ = 1`` everywhere.
    alfa : float, default 1.0
        Weight ``α`` of the pheromone.
    beta : float, default 1.0
        Weight ``β`` of the heuristic information.
    q0 : float, default 0.0
        Chance of choosing the best item instead of drawing one.

    Returns
    -------
    list of int
        Permutation of the item indices; its decoding is the chosen items.
    """
    escolhidos = _sequencia_formiga(
        itens,
        capacidade,
        feromonio,
        alfa,
        beta,
        q0,
        lambda anterior, j: (anterior, j),
    )
    resto = set(range(len(itens))) - set(escolhidos)
    return escolhidos + sorted(
        resto, key=lambda j: (-itens[j].valor / itens[j].peso, j)
    )


def trilha(
    solucao: list[int], itens: list[Item], capacidade: int
) -> list[tuple[int | None, int]]:
    """Return the components of an order: the transitions between packed items.

    The order is decoded, and the items that go into the knapsack, in the order
    they appear, form the path ``None → a → b → ...``.

    Parameters
    ----------
    solucao : list of int
        Order (permutation of the item indices).
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.

    Returns
    -------
    list of tuple of (int or None, int)
        Transitions ``(anterior, j)`` where the ant deposits pheromone.
    """
    dentro = decodificar(solucao, itens, capacidade)
    caminho = [j for j in solucao if dentro[j]]
    return list(zip([None, *caminho], caminho))
