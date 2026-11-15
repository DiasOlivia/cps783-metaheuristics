Historico = dict[str, dict[int, float]]


def novo_historico() -> Historico:
    """Create the history shared by every search scheme.

    Returns
    -------
    dict of {str: dict of {int: float}}
        Empty mappings from iteration to value for ``valor_candidato``,
        ``valor_atual``, ``melhor_valor`` and ``avaliacoes``. Schemes may add
        extra keys, such as ``temperatura`` or ``k``.
    """
    return {
        "valor_candidato": {},
        "valor_atual": {},
        "melhor_valor": {},
        "avaliacoes": {},
    }


def registrar(historico: Historico, iteracao: int, **valores: float) -> None:
    """Record the values of one iteration, creating extra keys when needed.

    Parameters
    ----------
    historico : dict of {str: dict of {int: float}}
        History to update in place.
    iteracao : int
        Iteration number; 0 is the initial solution.
    **valores : float
        Value of each key at this iteration.
    """
    for chave, valor in valores.items():
        historico.setdefault(chave, {})[iteracao] = valor
