import random
import statistics
import time
from collections.abc import Callable
from collections.abc import Iterable

from metaheuristics.utils.instancia import Item


def rodar_sementes(
    esquema: Callable,
    itens: list[Item],
    capacidade: int,
    sementes: Iterable[int],
    **parametros,
) -> list[dict]:
    """Run a search scheme once per seed on the same instance.

    Parameters
    ----------
    esquema : callable
        Search scheme, called as ``esquema(itens, capacidade, **parametros)``.
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    sementes : iterable of int
        Seeds for the global ``random`` state, one run each.
    **parametros
        Keyword arguments of the scheme, including the pieces to plug in.

    Returns
    -------
    list of dict
        One entry per run with ``semente``, ``solucao``, ``historico`` and
        ``tempo`` (seconds).
    """
    execucoes = []
    for semente in sementes:
        random.seed(semente)
        inicio = time.perf_counter()
        solucao, historico = esquema(itens, capacidade, **parametros)
        execucoes.append(
            {
                "semente": semente,
                "solucao": solucao,
                "historico": historico,
                "tempo": time.perf_counter() - inicio,
            }
        )
    return execucoes


def resumir(execucoes: list[dict], valor_otimo: int) -> dict[str, float]:
    """Summarize several runs against the optimal value.

    Parameters
    ----------
    execucoes : list of dict
        Runs returned by ``rodar_sementes``.
    valor_otimo : int
        Optimal value, e.g. from ``programacao_dinamica``.

    Returns
    -------
    dict of {str: float}
        ``execucoes``, ``otimo_atingido`` (runs with gap 0), ``gap_medio``,
        ``gap_melhor`` and ``gap_pior`` (percent), ``avaliacoes_ate_melhor``
        (mean evaluations until the final best value first appeared),
        ``avaliacoes_total`` and ``tempo_medio`` (seconds).
    """
    gaps, ate_melhor, totais = [], [], []
    for execucao in execucoes:
        historico = execucao["historico"]
        melhores = historico["melhor_valor"]
        final = melhores[max(melhores)]
        gaps.append(
            (valor_otimo - final) / valor_otimo * 100 if valor_otimo else 0.0
        )
        primeira = min(t for t, valor in melhores.items() if valor == final)
        ate_melhor.append(historico["avaliacoes"][primeira])
        totais.append(historico["avaliacoes"][max(historico["avaliacoes"])])
    return {
        "execucoes": len(execucoes),
        "otimo_atingido": sum(1 for gap in gaps if gap == 0),
        "gap_medio": statistics.mean(gaps),
        "gap_melhor": min(gaps),
        "gap_pior": max(gaps),
        "avaliacoes_ate_melhor": statistics.mean(ate_melhor),
        "avaliacoes_total": statistics.mean(totais),
        "tempo_medio": statistics.mean(e["tempo"] for e in execucoes),
    }


def tabela(resumos: dict[str, dict[str, float]]) -> str:
    """Format summaries as a text table, one row per label.

    Parameters
    ----------
    resumos : dict of {str: dict}
        Summary of each combination, as returned by ``resumir``.

    Returns
    -------
    str
        Table ready to print.
    """
    colunas = [
        ("ótimo", lambda r: f"{r['otimo_atingido']}/{r['execucoes']}"),
        ("gap médio", lambda r: f"{r['gap_medio']:.2f}%"),
        ("melhor", lambda r: f"{r['gap_melhor']:.2f}%"),
        ("pior", lambda r: f"{r['gap_pior']:.2f}%"),
        ("aval. até melhor", lambda r: f"{r['avaliacoes_ate_melhor']:.0f}"),
        ("aval. total", lambda r: f"{r['avaliacoes_total']:.0f}"),
        ("tempo", lambda r: f"{r['tempo_medio']:.3f}s"),
    ]
    largura = max([len("combinação")] + [len(rotulo) for rotulo in resumos])
    linhas = [
        "  ".join(
            [f"{'combinação':<{largura}}"] + [f"{nome:>16}" for nome, _ in colunas]
        )
    ]
    for rotulo, resumo in resumos.items():
        linhas.append(
            "  ".join(
                [f"{rotulo:<{largura}}"]
                + [f"{formato(resumo):>16}" for _, formato in colunas]
            )
        )
    return "\n".join(linhas)
