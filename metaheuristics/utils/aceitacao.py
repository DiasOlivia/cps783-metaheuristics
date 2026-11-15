import math
import random
from collections.abc import Callable


def aceita_melhora(delta: float, iteracao: int) -> bool:
    """Accept a candidate only when it strictly improves the current value.

    Parameters
    ----------
    delta : float
        Candidate value minus current value.
    iteracao : int
        Iteration number; unused, kept so every acceptance shares one signature.

    Returns
    -------
    bool
        Whether the candidate is accepted.
    """
    return delta > 0


def temperaturas(
    temperatura_inicial: float, temperatura_minima: float, fator_resfriamento: float
) -> list[float]:
    """List the temperature of each level of a geometric cooling schedule.

    Each level is the previous one times the cooling factor, while it stays above
    the minimum temperature.

    Parameters
    ----------
    temperatura_inicial : float
        First temperature.
    temperatura_minima : float
        Temperature at or below which the schedule stops.
    fator_resfriamento : float
        Multiplicative factor between levels, in ``(0, 1)``.

    Returns
    -------
    list of float
        Temperature of each level, from the first to the last.
    """
    if not 0 < fator_resfriamento < 1:
        raise ValueError("O fator de resfriamento deve estar entre 0 e 1.")
    niveis = []
    temperatura = temperatura_inicial
    while temperatura > temperatura_minima:
        niveis.append(temperatura)
        temperatura *= fator_resfriamento
    return niveis


def metropolis(
    niveis: list[float], iteracoes_por_temperatura: int
) -> Callable[[float, int], bool]:
    """Build the Metropolis acceptance rule for a cooling schedule.

    An improvement is always accepted. A worsening ``delta`` is accepted with
    probability ``exp(delta / T)``, where ``T`` is the level of the iteration;
    iterations past the last level keep the last temperature. A random number is
    drawn only for worsening or equal candidates.

    The returned function keeps the data of its last decision in the attribute
    ``ultimo`` (temperature, probability and draw), used by the debug plots.

    Parameters
    ----------
    niveis : list of float
        Temperature of each level, as returned by ``temperaturas``.
    iteracoes_por_temperatura : int
        Number of iterations spent at each level.

    Returns
    -------
    callable
        Acceptance rule ``(delta, iteracao) -> bool``, with 1-based iterations.
    """
    if not niveis:
        raise ValueError("A agenda de temperaturas está vazia.")

    def aceitar(delta: float, iteracao: int) -> bool:
        nivel = min((iteracao - 1) // iteracoes_por_temperatura, len(niveis) - 1)
        temperatura = niveis[nivel]
        if delta > 0:
            aceitar.ultimo = {
                "temperatura": temperatura,
                "chance": 1.0,
                "sorteio": None,
            }
            return True
        chance = math.exp(delta / temperatura)
        sorteio = random.uniform(0, 1)
        aceitar.ultimo = {
            "temperatura": temperatura,
            "chance": chance,
            "sorteio": sorteio,
        }
        return sorteio < chance

    aceitar.ultimo = None
    return aceitar
