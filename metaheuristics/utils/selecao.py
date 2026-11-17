import random


def selecao_roleta(valores: list[float], quantidade: int) -> list[int]:
    """Draw individuals with probability proportional to their fitness.

    Each individual gets a slice of the wheel proportional to its value, and the
    wheel is spun ``quantidade`` times, so the same individual may come out more
    than once. Values below zero count as zero; if every slice is zero, the draw
    is uniform.

    Parameters
    ----------
    valores : list of float
        Fitness of each individual.
    quantidade : int
        Number of individuals to draw.

    Returns
    -------
    list of int
        Indices of the drawn individuals.
    """
    fatias = [max(0, valor) for valor in valores]
    return random.choices(
        range(len(valores)), weights=fatias if any(fatias) else None, k=quantidade
    )


def selecao_ranking(valores: list[float], quantidade: int) -> list[int]:
    """Draw individuals with probability proportional to their rank.

    The worst individual has weight 1 and the best has weight ``len(valores)``
    (linear ranking), whatever the size of the differences in fitness. Ties get
    consecutive ranks.

    Parameters
    ----------
    valores : list of float
        Fitness of each individual.
    quantidade : int
        Number of individuals to draw, with repetition.

    Returns
    -------
    list of int
        Indices of the drawn individuals.
    """
    posicoes = [0] * len(valores)
    ranking = sorted(range(len(valores)), key=valores.__getitem__)
    for posicao, i in enumerate(ranking, start=1):
        posicoes[i] = posicao
    return random.choices(range(len(valores)), weights=posicoes, k=quantidade)


def selecao_torneio(valores: list[float], quantidade: int, q: int = 2) -> list[int]:
    """Run ``quantidade`` tournaments of ``q`` individuals; the best one wins each.

    The competitors are drawn uniformly and with replacement, so an individual may
    face itself. A larger ``q`` means a stronger selective pressure; ``q = 2`` is
    the binary tournament.

    Parameters
    ----------
    valores : list of float
        Fitness of each individual.
    quantidade : int
        Number of tournaments, one winner each.
    q : int, default 2
        Individuals per tournament.

    Returns
    -------
    list of int
        Indices of the winners.
    """
    if q < 1:
        raise ValueError("q deve ser pelo menos 1.")
    indices = range(len(valores))
    return [
        max(random.choices(indices, k=q), key=valores.__getitem__)
        for _ in range(quantidade)
    ]


def selecao_classes(
    valores: list[float],
    quantidade: int,
    melhores: float = 0.2,
    piores: float = 0.2,
) -> list[int]:
    """Take the best and the worst individuals and draw the rest at random.

    Of the ``quantidade`` chosen, a fraction ``melhores`` are the best individuals,
    a fraction ``piores`` are the worst ones, and the remaining are drawn
    uniformly, with replacement. Changing the two fractions balances
    intensification and diversification.

    Parameters
    ----------
    valores : list of float
        Fitness of each individual.
    quantidade : int
        Number of individuals to choose.
    melhores : float, default 0.2
        Fraction of ``quantidade`` taken from the best individuals.
    piores : float, default 0.2
        Fraction of ``quantidade`` taken from the worst individuals.

    Returns
    -------
    list of int
        Indices of the chosen individuals: the best, the worst, then the drawn.
    """
    if melhores < 0 or piores < 0 or melhores + piores > 1:
        raise ValueError("melhores e piores devem ser >= 0 e somar no máximo 1.")
    ranking = sorted(range(len(valores)), key=lambda i: -valores[i])
    n_melhores = min(round(melhores * quantidade), quantidade, len(valores))
    n_piores = min(
        round(piores * quantidade),
        quantidade - n_melhores,
        len(valores) - n_melhores,
    )
    escolhidos = ranking[:n_melhores] + ranking[len(ranking) - n_piores :]
    sorteados = random.choices(range(len(valores)), k=quantidade - len(escolhidos))
    return escolhidos + sorteados
