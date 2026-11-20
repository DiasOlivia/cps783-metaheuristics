from datetime import datetime
from functools import partial
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MaxNLocator

from metaheuristics.trabalho.protocol import ClienteId
from metaheuristics.trabalho.protocol import FacilidadeId
from metaheuristics.trabalho.protocol import Problem
from metaheuristics.trabalho.protocol import Solucao
from metaheuristics.utils.plot import COR_ATUAL
from metaheuristics.utils.plot import COR_CANDIDATO
from metaheuristics.utils.plot import COR_FORA
from metaheuristics.utils.plot import COR_MELHOR
from metaheuristics.utils.plot import COR_NOVO_MELHOR
from metaheuristics.utils.plot import COR_SUPERFICIE
from metaheuristics.utils.plot import COR_TEXTO
from metaheuristics.utils.plot import COR_TEXTO_SECUNDARIO
from metaheuristics.utils.plot import ESTILO
from metaheuristics.utils.plot import PASTA_PLOTS
from metaheuristics.utils.plot import finalizar
from metaheuristics.utils.plot import milhar
from metaheuristics.utils.plot import novas_melhores
from metaheuristics.utils.plot import plotar_historico

COR_ETAPA = "#0b0b0b"
PALETA_CLIENTES = [plt.get_cmap("tab20")(k) for k in range(20)]
# Segmentos mais estreitos que essa fração da maior capacidade ficam sem rótulo
LARGURA_MINIMA_ROTULO = 0.08

plot_grasp = partial(
    plotar_historico,
    titulo="Histórico do GRASP",
    rotulo_y="custo total",
    rotulo_x="soluções avaliadas",
)


def _cor(cliente_id: ClienteId):
    return PALETA_CLIENTES[(int(cliente_id) - 1) % len(PALETA_CLIENTES)]


class Debug:
    """Desenha uma figura por iteração do GRASP do CFLP.

    Passe uma instância como ``debug`` para o ``grasp``. À esquerda, a figura mostra
    a alocação da solução construída e a do ótimo local da iteração: uma barra por
    facilidade aberta, de cima para baixo na ordem de abertura, dividida nos
    clientes atendidos na ordem de atendimento, com a capacidade livre no fim. Cada
    cliente tem sempre a mesma cor. À direita fica o mini-histórico do custo total.
    Só desenha as iterações múltiplas de ``a_cada``, além da primeira e da última,
    até ``limite`` figuras. O depurador nunca sorteia números, então os resultados
    são os mesmos com e sem ele.

    Parameters
    ----------
    show : bool, default False
        Se mostra cada figura (no notebook).
    save : bool, default False
        Se salva cada figura como PNG.
    a_cada : int, default 1
        Desenha a cada ``a_cada`` iterações.
    limite : int, default 100
        Número máximo de figuras.
    pasta : str or pathlib.Path, optional
        Pasta das figuras; por padrão, ``plots/debug/<data-hora>/``.
    """

    def __init__(
        self,
        show: bool = False,
        save: bool = False,
        a_cada: int = 1,
        limite: int = 100,
        pasta: str | Path | None = None,
    ) -> None:
        if a_cada < 1:
            raise ValueError("a_cada deve ser pelo menos 1.")
        if not (show or save):
            raise ValueError(
                "Ligue show e/ou save: sem eles o depurador não gera nada."
            )
        self.capacidade: dict[FacilidadeId, int] = {}
        self.show = show
        self.save = save
        self.a_cada = a_cada
        self.limite = limite
        self.pasta = (
            Path(pasta)
            if pasta is not None
            else PASTA_PLOTS / "debug" / f"{datetime.now():%Y%m%d_%H%M%S}"
        )
        self.figuras = 0
        self._avisou = False
        self.ativo = False
        self.iteracao = 0
        self.total = 0
        self.iteracoes: list[int] = []
        self.custos_construidas: list[int] = []
        self.custos_atuais: list[int] = []
        self.custos_melhores: list[int] = []

    def inicio_iteracao(self, problem: Problem, iteracao: int, total: int) -> None:
        """Marca o início de uma iteração e decide se ela será desenhada.

        O ``problem`` dá a capacidade de cada facilidade, que define o tamanho das
        barras.
        """
        self.capacidade = {f.id: f.capacidade for f in problem.facilidades}
        self.iteracao = iteracao
        self.total = total
        self.ativo = iteracao in (1, total) or iteracao % self.a_cada == 0

    def fim_iteracao(
        self, construida: Solucao, melhorada: Solucao, melhor: Solucao
    ) -> None:
        """Registra o resultado da iteração e desenha a figura, se ela estiver ativa."""
        self.iteracoes.append(self.iteracao)
        self.custos_construidas.append(construida.custo_total)
        self.custos_atuais.append(melhorada.custo_total)
        self.custos_melhores.append(melhor.custo_total)
        if self._pode_desenhar():
            self._desenhar(construida, melhorada, melhor)

    def _pode_desenhar(self) -> bool:
        if not self.ativo:
            return False
        if self.figuras >= self.limite:
            if not self._avisou:
                print(
                    f"Depurador: limite de {self.limite} figuras atingido; "
                    "as próximas iterações não serão desenhadas."
                )
                self._avisou = True
            return False
        return True

    def _desenhar(
        self, construida: Solucao, melhorada: Solucao, melhor: Solucao
    ) -> None:
        texto = (
            f"construída {milhar(construida.custo_total)} → ótimo local "
            f"{milhar(melhorada.custo_total)} · melhor {milhar(melhor.custo_total)}"
        )
        with plt.rc_context(ESTILO):
            fig = plt.figure(figsize=(15, 7.5), layout="constrained")
            grade = fig.add_gridspec(2, 2, width_ratios=(1.15, 1))
            ax_construida = fig.add_subplot(grade[0, 0])
            ax_otimo = fig.add_subplot(grade[1, 0], sharex=ax_construida)
            ax_historico = fig.add_subplot(grade[:, 1])
            fig.suptitle(
                f"GRASP · iteração {self.iteracao} de {self.total}\n{texto}",
                x=0.01,
                ha="left",
                fontsize=11.5,
                fontweight="bold",
            )
            self._alocacao(ax_construida, construida, "1. Alocação da construída")
            self._alocacao(ax_otimo, melhorada, "2. Alocação do ótimo local")
            ax_otimo.set_xlabel("unidades enviadas, na ordem de atendimento →")
            self._historico(ax_historico)
            self._legenda(fig)
            finalizar(
                fig, f"grasp_{self.iteracao:05d}", self.show, self.save, self.pasta
            )
            plt.close(fig)
        self.figuras += 1

    def _alocacao(self, ax, solucao: Solucao, titulo: str) -> None:
        maior = max(self.capacidade.values())
        for posicao, facilidade_id in enumerate(solucao.abertas):
            envios = [
                (cliente_id, quantidade)
                for (cliente_id, f_id), quantidade in solucao.alocacao.items()
                if f_id == facilidade_id
            ]
            usado = 0
            for cliente_id, quantidade in envios:
                ax.barh(
                    posicao,
                    quantidade,
                    left=usado,
                    height=0.7,
                    color=_cor(cliente_id),
                    edgecolor=COR_SUPERFICIE,
                    linewidth=1,
                )
                if quantidade >= LARGURA_MINIMA_ROTULO * maior:
                    ax.text(
                        usado + quantidade / 2,
                        posicao,
                        f"{cliente_id} {quantidade}",
                        ha="center",
                        va="center",
                        fontsize=7.5,
                        color=COR_TEXTO,
                    )
                usado += quantidade
            capacidade = self.capacidade[facilidade_id]
            ax.barh(
                posicao, capacidade - usado, left=usado, height=0.7, color=COR_FORA
            )
            ax.text(
                capacidade + 0.01 * maior,
                posicao,
                f"{usado}/{capacidade}",
                va="center",
                fontsize=8,
                color=COR_TEXTO_SECUNDARIO,
            )
        ax.set_yticks(
            range(len(solucao.abertas)),
            [f"{k}º {f_id}" for k, f_id in enumerate(solucao.abertas, 1)],
        )
        ax.invert_yaxis()
        ax.set_xlim(0, maior * 1.12)
        ax.grid(axis="y", visible=False)
        ax.set_title(
            f"{titulo} ({milhar(solucao.custo_total)})", loc="left", fontsize=11
        )

    def _historico(self, ax) -> None:
        ax.plot(
            self.iteracoes,
            self.custos_construidas,
            color=COR_CANDIDATO,
            linewidth=0.8,
        )
        ax.plot(self.iteracoes, self.custos_atuais, color=COR_ATUAL, linewidth=1.2)
        ax.step(
            self.iteracoes,
            self.custos_melhores,
            where="post",
            color=COR_MELHOR,
            linewidth=1.8,
        )
        ax.scatter(
            *novas_melhores(self.iteracoes, self.custos_melhores),
            s=28,
            color=COR_NOVO_MELHOR,
            zorder=5,
        )
        ax.scatter(
            [self.iteracoes[-1]],
            [self.custos_atuais[-1]],
            s=60,
            color=COR_ETAPA,
            zorder=6,
        )
        ax.set_xlim(0, self.total + 1)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_formatter(FuncFormatter(milhar))
        ax.yaxis.set_major_formatter(FuncFormatter(milhar))
        ax.set_xlabel("iteração")
        ax.set_ylabel("custo total")
        ax.set_title("3. Mini-histórico do custo total", loc="left", fontsize=11)

    def _legenda(self, fig) -> None:
        def ponto(cor, tamanho=7):
            return {
                "marker": "o",
                "linestyle": "none",
                "color": cor,
                "markersize": tamanho,
            }

        itens = [
            Patch(
                color=_cor(ClienteId(1)), label="cliente (a mesma cor em toda barra)"
            ),
            Patch(color=COR_FORA, label="capacidade livre"),
            Line2D([], [], color=COR_CANDIDATO, linewidth=0.8, label="construída"),
            Line2D([], [], color=COR_ATUAL, linewidth=1.2, label="ótimo local"),
            Line2D(
                [], [], color=COR_MELHOR, linewidth=1.8, label="melhor até agora"
            ),
            Line2D([], [], **ponto(COR_NOVO_MELHOR), label="nova melhor solução"),
            Line2D([], [], **ponto(COR_ETAPA, 8), label="iteração desta figura"),
        ]
        fig.legend(handles=itens, loc="outside lower center", ncol=4, fontsize=8.5)
