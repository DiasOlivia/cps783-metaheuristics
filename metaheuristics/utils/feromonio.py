from collections.abc import Hashable


class Feromonio(dict):
    """Pheromone trail: a dict from solution component to its pheromone ``τ``.

    A component that no ant has used yet is not stored and is worth the
    ``fundo``, the initial pheromone ``τ0`` evaporated along with the others. So
    the trail works for any kind of component (an item, a transition between
    items...) without listing them in advance.

    Parameters
    ----------
    inicial : float
        Initial pheromone ``τ0`` of every component.

    Examples
    --------
    >>> tau = Feromonio(1.0)
    >>> tau.evaporar(0.5)
    >>> tau[(3, 5)] += 0.102 + 0.102 + 0.081  # slide 27
    >>> round(tau[(3, 5)], 3)
    0.785
    """

    def __init__(self, inicial: float) -> None:
        super().__init__()
        self.fundo = inicial

    def __missing__(self, componente: Hashable) -> float:
        return self.fundo

    def evaporar(self, taxa: float) -> None:
        """Apply ``τ ← (1 - taxa) τ`` to every component, stored or not."""
        self.fundo *= 1 - taxa
        for componente in self:
            self[componente] *= 1 - taxa
