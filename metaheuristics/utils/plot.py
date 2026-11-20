from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from metaheuristics.utils.historico import Historico

PASTA_PLOTS = Path(__file__).resolve().parents[2] / "plots"

COR_SUPERFICIE = "#fcfcfb"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_EIXO = "#c3c2b7"
COR_GRADE = "#e1e0d9"
COR_ATUAL = "royalblue"
COR_MELHOR = "#7b3fa0"
COR_CANDIDATO = "#9b9a94"
COR_EXTRA = "#e07a1f"
COR_MELHORA = "#2a9d55"
COR_PIORA = "#d1495b"
COR_IGUAL = "#c9a227"
COR_FORA = "#d9d8d2"
COR_NOVO_MELHOR = "#d1495b"

ESTILO = {
    "figure.facecolor": COR_SUPERFICIE,
    "axes.facecolor": COR_SUPERFICIE,
    "axes.edgecolor": COR_EIXO,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": COR_GRADE,
    "grid.linewidth": 0.75,
    "axes.labelcolor": COR_TEXTO_SECUNDARIO,
    "axes.titlecolor": COR_TEXTO,
    "xtick.color": COR_EIXO,
    "ytick.color": COR_EIXO,
    "xtick.labelcolor": COR_TEXTO_SECUNDARIO,
    "ytick.labelcolor": COR_TEXTO_SECUNDARIO,
    "legend.frameon": False,
    "legend.labelcolor": COR_TEXTO_SECUNDARIO,
}

CHAVES_COMUNS = ("valor_candidato", "valor_atual", "melhor_valor", "avaliacoes")
PREFIXO_PESO = "peso "
CORES_OPERADORES = (
    "#1f6fb4",
    "#2a9d55",
    "#d1495b",
    "#7b3fa0",
    "#c9a227",
    "#17a2b8",
    "#8c564b",
)


def milhar(valor: float, _posicao: int | None = None) -> str:
    """Format a tick value with Brazilian thousands separators.

    Integers become ``30.289`` and other values keep one decimal place, as in
    ``1.234,5``. Use it with ``matplotlib.ticker.FuncFormatter``.
    """
    texto = f"{valor:,.0f}" if float(valor).is_integer() else f"{valor:,.1f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def novas_melhores(
    xs: Sequence[float], melhores: Sequence[float]
) -> tuple[list[float], list[float]]:
    """Points where the best value changes, the first one included.

    Parameters
    ----------
    xs : list of float
        Horizontal position of each recorded iteration.
    melhores : list of float
        Best value at each recorded iteration.

    Returns
    -------
    tuple of (list of float, list of float)
        Horizontal positions and best values of the points.
    """
    pontos = [
        (x, valor)
        for k, (x, valor) in enumerate(zip(xs, melhores))
        if k == 0 or valor != melhores[k - 1]
    ]
    return [x for x, _ in pontos], [valor for _, valor in pontos]


def finalizar(
    fig: Figure, nome: str, show: bool, save: bool, pasta: Path | None = None
) -> Path | None:
    """Save the figure as PNG and/or show it.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to output.
    nome : str
        File name, without extension.
    show : bool
        Whether to show the figure (inline in a notebook).
    save : bool
        Whether to save the figure.
    pasta : pathlib.Path, optional
        Destination folder; defaults to ``plots/`` at the repository root.

    Returns
    -------
    pathlib.Path or None
        Saved file, or None when not saving.
    """
    caminho = None
    if save:
        pasta = pasta if pasta is not None else PASTA_PLOTS
        pasta.mkdir(parents=True, exist_ok=True)
        caminho = pasta / f"{nome}.png"
        fig.savefig(str(caminho))
    if show:
        plt.show()
    return caminho


def _eixo_x(historico: Historico, eixo_x: str) -> list[float]:
    iteracoes = sorted(historico["valor_atual"])
    if eixo_x == "avaliacoes":
        return [historico["avaliacoes"][t] for t in iteracoes]
    if eixo_x == "iteracao":
        return iteracoes
    raise ValueError("eixo_x deve ser 'avaliacoes' ou 'iteracao'.")


def plotar_historico(
    historico: Historico,
    valor_otimo: int | None = None,
    eixo_x: str = "avaliacoes",
    titulo: str = "Histórico da busca",
    show: bool = False,
    save: bool = False,
    rotulo_x: str | None = None,
    rotulo_y: str = "valor",
) -> Figure:
    """Plot candidate, current and best values of one run.

    A lower panel shows the extra keys of the history (such as ``temperatura`` in
    the SA or ``k`` in the VNS). Keys starting with ``'peso '`` (the operator
    weights of the ALNS) get one line each on the left axis, and the other extras
    move to the right axis. Saved files go to ``plots/utils/``.

    Parameters
    ----------
    historico : dict of {str: dict of {int: float}}
        History returned by a search scheme.
    valor_otimo : int, optional
        Optimal value drawn as a reference line.
    eixo_x : {'avaliacoes', 'iteracao'}, default 'avaliacoes'
        Horizontal axis: accumulated evaluations or iteration number.
    titulo : str, default 'Histórico da busca'
        Figure title.
    show : bool, default False
        Whether to show the figure.
    save : bool, default False
        Whether to save the figure as PNG.
    rotulo_x : str, optional
        Horizontal axis label; defaults to 'avaliações' or 'iteração', following
        ``eixo_x``.
    rotulo_y : str, default 'valor'
        Vertical axis label.

    Returns
    -------
    matplotlib.figure.Figure
        The figure.
    """
    if rotulo_x is None:
        rotulo_x = "avaliações" if eixo_x == "avaliacoes" else "iteração"
    iteracoes = sorted(historico["valor_atual"])
    xs = _eixo_x(historico, eixo_x)
    extras = [chave for chave in historico if chave not in CHAVES_COMUNS]
    pesos = [chave for chave in extras if chave.startswith(PREFIXO_PESO)]
    outros = [chave for chave in extras if chave not in pesos]
    with plt.rc_context(ESTILO):
        if extras:
            fig, (ax, ax_extra) = plt.subplots(
                2,
                1,
                figsize=(11, 8 if pesos else 7),
                sharex=True,
                height_ratios=(3, 1.6 if pesos else 1),
                layout="constrained",
            )
        else:
            fig, ax = plt.subplots(figsize=(11, 5), layout="constrained")
        ax.plot(
            xs,
            [historico["valor_candidato"][t] for t in iteracoes],
            color=COR_CANDIDATO,
            linewidth=0.6,
            label="candidato",
        )
        ax.plot(
            xs,
            [historico["valor_atual"][t] for t in iteracoes],
            color=COR_ATUAL,
            linewidth=1.0,
            label="atual",
        )
        melhores = [historico["melhor_valor"][t] for t in iteracoes]
        ax.step(
            xs,
            melhores,
            where="post",
            color=COR_MELHOR,
            linewidth=1.8,
            label=f"melhor ({milhar(melhores[-1])})",
        )
        ax.scatter(
            *novas_melhores(xs, melhores),
            s=28,
            color=COR_NOVO_MELHOR,
            zorder=5,
            label="nova melhor solução",
        )
        if valor_otimo is not None:
            ax.axhline(
                valor_otimo,
                color=COR_TEXTO,
                linewidth=1,
                linestyle=":",
                label=f"ótimo ({milhar(valor_otimo)})",
            )
        ax.xaxis.set_major_formatter(FuncFormatter(milhar))
        ax.yaxis.set_major_formatter(FuncFormatter(milhar))
        ax.set_ylabel(rotulo_y)
        ax.set_title(titulo, loc="left", fontsize=13)
        ax.legend(loc="lower right")
        if extras:
            x_da_iteracao = dict(zip(iteracoes, xs))

            def degraus(eixo, chave: str, cor: str, rotulo: str) -> None:
                pares = sorted(historico[chave].items())
                eixo.step(
                    [x_da_iteracao[t] for t, _ in pares],
                    [v for _, v in pares],
                    where="post",
                    color=cor,
                    linewidth=1.2,
                    label=rotulo,
                )

            eixo_outros = ax_extra
            if pesos:
                for i, chave in enumerate(pesos):
                    cor = CORES_OPERADORES[i % len(CORES_OPERADORES)]
                    degraus(ax_extra, chave, cor, chave.removeprefix(PREFIXO_PESO))
                ax_extra.set_ylabel("peso do operador")
                ax_extra.legend(loc="upper right", ncol=3, fontsize=8)
                if outros:
                    # Os pesos e a temperatura têm escalas diferentes: um eixo cada
                    eixo_outros = ax_extra.twinx()
                    eixo_outros.grid(False)
                    eixo_outros.spines["right"].set_visible(True)
                    eixo_outros.tick_params(axis="y", labelcolor=COR_EXTRA)
                    eixo_outros.yaxis.label.set_color(COR_EXTRA)
            for chave in outros:
                degraus(eixo_outros, chave, COR_EXTRA, chave)
            if outros:
                eixo_outros.set_ylabel(", ".join(outros))
            ax_extra.xaxis.set_major_formatter(FuncFormatter(milhar))
            ax_extra.set_xlabel(rotulo_x)
        else:
            ax.set_xlabel(rotulo_x)
    carimbo = f"{datetime.now():%Y%m%d_%H%M%S}"
    finalizar(fig, f"historico_{carimbo}", show, save, PASTA_PLOTS / "utils")
    return fig


def plotar_comparacao(
    historicos: dict[str, Historico],
    valor_otimo: int | None = None,
    eixo_x: str = "avaliacoes",
    show: bool = False,
    save: bool = False,
) -> Figure:
    """Overlay the best value of several runs, one line per label.

    Saved files go to ``plots/utils/``.

    Parameters
    ----------
    historicos : dict of {str: dict}
        History of each run, keyed by the label shown in the legend.
    valor_otimo : int, optional
        Optimal value drawn as a reference line.
    eixo_x : {'avaliacoes', 'iteracao'}, default 'avaliacoes'
        Horizontal axis. Evaluations measure the same effort for every scheme.
    show : bool, default False
        Whether to show the figure.
    save : bool, default False
        Whether to save the figure as PNG.

    Returns
    -------
    matplotlib.figure.Figure
        The figure.
    """
    with plt.rc_context(ESTILO):
        fig, ax = plt.subplots(figsize=(11, 5), layout="constrained")
        for rotulo, historico in historicos.items():
            iteracoes = sorted(historico["melhor_valor"])
            final = historico["melhor_valor"][iteracoes[-1]]
            ax.step(
                _eixo_x(historico, eixo_x),
                [historico["melhor_valor"][t] for t in iteracoes],
                where="post",
                linewidth=1.6,
                label=f"{rotulo} ({milhar(final)})",
            )
        if valor_otimo is not None:
            ax.axhline(
                valor_otimo,
                color=COR_TEXTO,
                linewidth=1,
                linestyle=":",
                label=f"ótimo ({milhar(valor_otimo)})",
            )
        ax.xaxis.set_major_formatter(FuncFormatter(milhar))
        ax.yaxis.set_major_formatter(FuncFormatter(milhar))
        ax.set_xlabel("avaliações" if eixo_x == "avaliacoes" else "iteração")
        ax.set_ylabel("melhor valor")
        ax.set_title("Comparação: melhor valor encontrado", loc="left", fontsize=13)
        ax.legend(loc="lower right")
    carimbo = f"{datetime.now():%Y%m%d_%H%M%S}"
    finalizar(fig, f"comparacao_{carimbo}", show, save, PASTA_PLOTS / "utils")
    return fig
