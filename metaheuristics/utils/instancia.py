import random


class Item:
    """Item of the 0-1 knapsack problem.

    Parameters
    ----------
    peso : int
        Positive integer weight.
    valor : int
        Non-negative integer value.
    """

    def __init__(self, peso: int, valor: int) -> None:
        self.peso = peso
        self.valor = valor

    def __repr__(self) -> str:
        return f"Item(peso={self.peso}, valor={self.valor})"


def gerar_instancia_aleatoria(
    num_itens: int, max_peso: int, max_valor: int, correlacionada: bool = False
) -> list[Item]:
    """Generate random knapsack items using the global ``random`` state.

    Weights are drawn uniformly from ``[1, max_peso]``. Without correlation, values
    are drawn uniformly from ``[1, max_valor]``, one weight and one value per item.
    A correlated instance draws only the weight and sets
    ``valor = peso + max(1, max_peso // 10)`` (Pisinger's strongly correlated
    instance), so every item has a similar value per unit of weight.

    Parameters
    ----------
    num_itens : int
        Number of items.
    max_peso : int
        Largest possible weight.
    max_valor : int
        Largest possible value; ignored when ``correlacionada`` is True.
    correlacionada : bool, default False
        Whether values follow the weights.

    Returns
    -------
    list of Item
        Generated items.
    """
    if num_itens < 0 or max_peso < 1 or max_valor < 1:
        raise ValueError("Quantidade de itens e limites devem ser válidos.")
    itens = []
    for _ in range(num_itens):
        peso = random.randint(1, max_peso)
        if correlacionada:
            valor = peso + max(1, max_peso // 10)
        else:
            valor = random.randint(1, max_valor)
        itens.append(Item(peso, valor))
    return itens


def programacao_dinamica(
    itens: list[Item], capacidade: int
) -> tuple[int, list[int]]:
    """Solve the integer-weight 0-1 knapsack problem exactly.

    Parameters
    ----------
    itens : list of Item
        Items with positive integer weights.
    capacidade : int
        Non-negative integer capacity.

    Returns
    -------
    tuple of (int, list of int)
        Optimal value and one optimal binary selection vector.
    """
    if capacidade < 0:
        raise ValueError("Capacidade não pode ser negativa.")
    n = len(itens)
    dp = [[0] * (capacidade + 1) for _ in range(n + 1)]
    for i, item in enumerate(itens, start=1):
        for w in range(capacidade + 1):
            dp[i][w] = dp[i - 1][w]
            if item.peso <= w:
                dp[i][w] = max(dp[i][w], item.valor + dp[i - 1][w - item.peso])
    # Reconstrução: se o valor muda da linha de cima para a atual, o item entrou
    selecao = [0] * n
    w = capacidade
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selecao[i - 1] = 1
            w -= itens[i - 1].peso
    return dp[n][capacidade], selecao
