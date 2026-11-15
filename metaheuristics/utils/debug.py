import re
import unicodedata
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from metaheuristics.utils.instancia import Item
from metaheuristics.utils.plot import COR_ATUAL
from metaheuristics.utils.plot import COR_CANDIDATO
from metaheuristics.utils.plot import COR_EXTRA
from metaheuristics.utils.plot import COR_FORA
from metaheuristics.utils.plot import COR_IGUAL
from metaheuristics.utils.plot import COR_MELHOR
from metaheuristics.utils.plot import COR_MELHORA
from metaheuristics.utils.plot import COR_PIORA
from metaheuristics.utils.plot import COR_SUPERFICIE
from metaheuristics.utils.plot import COR_TEXTO
from metaheuristics.utils.plot import COR_TEXTO_SECUNDARIO
from metaheuristics.utils.plot import ESTILO
from metaheuristics.utils.plot import PASTA_PLOTS
from metaheuristics.utils.plot import finalizar

MAX_VIZINHAS = 40
TRILHA_RECENTE = 40
COR_ETAPA = "#0b0b0b"

Ponto = tuple[int, int]


def _br(numero: float, casas: int = 2) -> str:
    return f"{numero:.{casas}f}".replace(".", ",")


def _porcentagem(chance: float) -> str:
    return "< 0,1%" if chance < 0.001 else f"{_br(chance * 100, 1)}%"


class Depurador:
    """Draw one figure per step of a search, to see what the algorithm sees.

    Pass an instance as ``debug`` to a search scheme. The scheme marks the start
    and the end of each iteration; local searches and perturbations report their
    own steps. A figure is drawn only for iterations that are multiples of
    ``a_cada`` (plus the first and the last one), and drawing stops after
    ``limite`` figures. The depurador never draws random numbers, so results
    with and without it are identical.

    Each figure has three panels: the current solution as a thin strip; the
    weight × value plane, with the trail of current solutions and the neighbors
    seen at this step; and the value history, on the same vertical scale.

    Parameters
    ----------
    itens : list of Item
        Items of the instance.
    capacidade : int
        Knapsack capacity.
    decodificar : callable, optional
        Turns a solution into a binary vector, e.g. ``ordem.decodificar`` for the
        order representation. None means solutions are already binary.
    valor_otimo : int, optional
        Optimal value drawn as a reference line.
    show : bool, default False
        Whether to show each figure (inline in a notebook).
    save : bool, default False
        Whether to save each figure as PNG.
    a_cada : int, default 1
        Draw every ``a_cada`` iterations.
    limite : int, default 100
        Maximum number of figures.
    pasta : str or pathlib.Path, optional
        Folder for saved figures; defaults to ``plots/debug/<date-time>/``.
    """

    def __init__(
        self,
        itens: list[Item],
        capacidade: int,
        decodificar: Callable[[list[int], list[Item], int], list[int]] | None = None,
        valor_otimo: int | None = None,
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
        self.itens = itens
        self.capacidade = capacidade
        self.decodificar = decodificar
        self.valor_otimo = valor_otimo
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
        self.esquema = ""
        self.iteracao = 0
        self.iteracoes: list[int] = []
        self.atuais: list[float] = []
        self.melhores: list[float] = []
        self.candidatos: list[float] = []
        self.extras: dict[str, list[tuple[int, float]]] = {}
        self.trilha: list[Ponto] = []
        self.melhor_ponto: Ponto | None = None

    def inicio_iteracao(
        self, esquema: str, iteracao: int, ultima: bool = False
    ) -> None:
        """Mark the start of an iteration and decide whether it is drawn.

        Parameters
        ----------
        esquema : str
            Name of the scheme, shown in the titles.
        iteracao : int
            Iteration number; 0 is the initial solution.
        ultima : bool, default False
            Whether this is the last iteration, which is always drawn.
        """
        self.esquema = esquema
        self.iteracao = iteracao
        self.ativo = iteracao == 0 or ultima or iteracao % self.a_cada == 0

    def passo(
        self,
        etapa: str,
        atual: list[int],
        vizinhas: list[tuple[str, list[int]]],
        escolhida: str | None = None,
        nota: str = "",
    ) -> None:
        """Draw a step reported by a piece, such as a local search pass.

        Parameters
        ----------
        etapa : str
            Name of the step, e.g. 'busca local' or 'perturbação'.
        atual : list of int
            Solution the step starts from.
        vizinhas : list of (str, list of int)
            Solutions examined at the step, with a label each.
        escolhida : str, optional
            Label of the solution the step moved to, if any.
        nota : str, default ''
            Extra text for the title.
        """
        if not self._pode_desenhar():
            return
        valor_atual = self._ponto(atual)[1]
        pontos = [self._ponto(solucao) for _, solucao in vizinhas]
        if len(vizinhas) == 1:
            texto = f"{vizinhas[0][0]}: {valor_atual} → {self._valor(pontos[0])}"
        else:
            contagem = {"melhora": 0, "igual": 0, "piora": 0, "não cabe": 0}
            for ponto in pontos:
                contagem[self._classe(ponto, valor_atual)] += 1
            plural = {
                "melhora": "melhoram",
                "igual": "iguais",
                "piora": "pioram",
                "não cabe": "não cabem",
            }
            texto = f"{len(vizinhas)} vizinhas: " + " · ".join(
                f"{n} {plural[classe] if n != 1 else classe}"
                for classe, n in contagem.items()
            )
            if escolhida is not None:
                valor = self._valor(
                    pontos[[r for r, _ in vizinhas].index(escolhida)]
                )
                texto += f" → escolhida {escolhida} ({valor})"
        if nota:
            texto += f" · {nota}"
        self._desenhar(
            etapa, atual, vizinhas, escolhida, texto, True, None, self.trilha
        )

    def fim_iteracao(
        self,
        anterior: list[int],
        candidato: list[int],
        valor_candidato: float,
        aceito: bool,
        valor_atual: float,
        melhor_valor: float,
        extras: dict[str, float] | None = None,
        info: dict | None = None,
    ) -> None:
        """Record the result of an iteration and draw it when active.

        Parameters
        ----------
        anterior : list of int
            Current solution at the start of the iteration.
        candidato : list of int
            Candidate generated in the iteration.
        valor_candidato : float
            Value of the candidate.
        aceito : bool
            Whether the candidate became the current solution.
        valor_atual : float
            Current value after the decision.
        melhor_valor : float
            Best value found so far, after the decision.
        extras : dict of {str: float}, optional
            Values shown in the title and on the right axis, e.g. the temperature.
        info : dict, optional
            Last decision of the acceptance rule (probability and draw); an
            optional ``nota`` is added to the title.
        """
        extras = extras or {}
        valor_anterior = self.atuais[-1] if self.atuais else valor_atual
        melhor_antes = self.melhores[-1] if self.melhores else None
        self.iteracoes.append(self.iteracao)
        self.atuais.append(valor_atual)
        self.melhores.append(melhor_valor)
        self.candidatos.append(valor_candidato)
        for chave, valor in extras.items():
            self.extras.setdefault(chave, []).append((self.iteracao, valor))
        ponto = self._ponto(candidato if aceito else anterior)
        self.trilha.append(ponto)
        if melhor_antes is None or melhor_valor > melhor_antes:
            self.melhor_ponto = ponto
        if not self._pode_desenhar():
            return

        if self.iteracao == 0:
            texto = "solução inicial"
            if candidato != anterior:
                texto += f" após a busca local ({valor_candidato})"
        else:
            delta = valor_candidato - valor_anterior
            if not aceito:
                decisao = "REJEITADO"
            elif delta > 0:
                decisao = "ACEITO"
            else:
                decisao = "ACEITO (empate)" if delta == 0 else "ACEITO (piora)"
            texto = (
                f"candidato: {self._descrever(anterior, candidato)} · Δ = {delta:+}"
            )
            if info and info.get("sorteio") is not None:
                texto += (
                    f" · chance {_porcentagem(info['chance'])}"
                    f" · sorteio {_br(info['sorteio'])}"
                )
            if info and info.get("nota"):
                texto += f" · {info['nota']}"
            texto += f" → {decisao}"
            if melhor_antes is not None and melhor_valor > melhor_antes:
                texto += f" · novo melhor ({melhor_valor})"
        detalhes = " · ".join(
            f"{'T' if chave == 'temperatura' else chave} = "
            f"{_br(valor, 1) if isinstance(valor, float) else valor}"
            for chave, valor in extras.items()
        )
        etapa = f"iteração · {detalhes}" if detalhes else "iteração"
        vizinhas, escolhida = self._vizinhas_da_iteracao(anterior, candidato)
        self._desenhar(
            etapa,
            anterior,
            vizinhas,
            escolhida,
            texto,
            aceito,
            (self.iteracao, valor_candidato),
            self.trilha[:-1],
        )

    def _pode_desenhar(self) -> bool:
        if not self.ativo:
            return False
        if self.figuras >= self.limite:
            if not self._avisou:
                print(
                    f"Depurador: limite de {self.limite} figuras atingido; "
                    "as próximas etapas não serão desenhadas."
                )
                self._avisou = True
            return False
        return True

    def _binaria(self, solucao: list[int]) -> list[int]:
        if self.decodificar is None:
            return list(solucao)
        return self.decodificar(solucao, self.itens, self.capacidade)

    def _ponto(self, solucao: list[int]) -> Ponto:
        """Weight and raw value (even if overweight) of a solution."""
        binaria = self._binaria(solucao)
        peso = sum(item.peso for item, bit in zip(self.itens, binaria) if bit)
        valor = sum(item.valor for item, bit in zip(self.itens, binaria) if bit)
        return peso, valor

    def _valor(self, ponto: Ponto) -> int:
        return ponto[1] if ponto[0] <= self.capacidade else 0

    def _classe(self, ponto: Ponto, valor_atual: float) -> str:
        if ponto[0] > self.capacidade:
            return "não cabe"
        if ponto[1] > valor_atual:
            return "melhora"
        return "igual" if ponto[1] == valor_atual else "piora"

    def _descrever(self, anterior: list[int], candidato: list[int]) -> str:
        antes, depois = self._binaria(anterior), self._binaria(candidato)
        mudancas = [j for j in range(len(antes)) if antes[j] != depois[j]]
        if self.decodificar is not None:
            return f"nova ordem ({len(mudancas)} itens mudam na mochila)"
        if len(mudancas) == 1:
            j = mudancas[0]
            return f"{'entra' if depois[j] else 'sai'} o item {j + 1}"
        return f"{len(mudancas)} itens mudam"

    def _vizinhas_da_iteracao(
        self, anterior: list[int], candidato: list[int]
    ) -> tuple[list[tuple[str, list[int]]], str | None]:
        """Neighbors drawn for an iteration: ±item (binary) plus the candidate."""
        if candidato == anterior:
            return [], None
        vizinhas = []
        escolhida = None
        if self.decodificar is None:
            for j in range(len(anterior)):
                vizinha = list(anterior)
                vizinha[j] ^= 1
                rotulo = f"{'−' if anterior[j] else '+'}{j + 1}"
                vizinhas.append((rotulo, vizinha))
                if vizinha == candidato:
                    escolhida = rotulo
        if escolhida is None:
            vizinhas.append(("candidato", candidato))
            escolhida = "candidato"
        return vizinhas, escolhida

    def _desenhar(
        self,
        etapa: str,
        atual: list[int],
        vizinhas: list[tuple[str, list[int]]],
        escolhida: str | None,
        texto: str,
        aceito: bool,
        candidato_historico: tuple[int, float] | None,
        trilha: list[Ponto],
    ) -> None:
        titulo = f"{self.esquema} · iteração {self.iteracao} · etapa: {etapa}"
        with plt.rc_context(ESTILO):
            fig = plt.figure(figsize=(15, 7.0), layout="constrained")
            grade = fig.add_gridspec(
                2, 2, height_ratios=(0.45, 6), width_ratios=(1.15, 1)
            )
            ax_faixa = fig.add_subplot(grade[0, :])
            ax_plano = fig.add_subplot(grade[1, 0])
            ax_historico = fig.add_subplot(grade[1, 1], sharey=ax_plano)
            fig.suptitle(
                f"{titulo}\n{texto}",
                x=0.01,
                ha="left",
                fontsize=11.5,
                fontweight="bold",
            )
            self._faixa(ax_faixa, atual)
            ys_plano = self._plano(
                ax_plano, atual, vizinhas, escolhida, aceito, trilha
            )
            ys_historico = self._historico(ax_historico, candidato_historico)
            topo = max(ys_plano + ys_historico + [self.valor_otimo or 0, 1])
            ax_plano.set_ylim(0, topo * 1.12)
            self._legenda(fig)
            sem_acento = unicodedata.normalize("NFKD", etapa.split(" · ")[0])
            sem_acento = sem_acento.encode("ascii", "ignore").decode().lower()
            slug = re.sub(r"[^a-z0-9]+", "_", sem_acento).strip("_")
            nome = f"{self.iteracao:05d}_{self.figuras:03d}_{slug or 'etapa'}"
            finalizar(fig, nome, self.show, self.save, self.pasta)
            plt.close(fig)
        self.figuras += 1

    def _faixa(self, ax, solucao: list[int]) -> None:
        binaria = self._binaria(solucao)
        inicio = 0
        for j, (item, bit) in enumerate(zip(self.itens, binaria)):
            if not bit:
                continue
            ax.barh(
                0,
                item.peso,
                left=inicio,
                height=0.5,
                color=COR_ATUAL,
                edgecolor=COR_SUPERFICIE,
                linewidth=1,
            )
            if item.peso >= 0.05 * self.capacidade:
                ax.text(
                    inicio + item.peso / 2,
                    0,
                    f"{j + 1}",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=7,
                    fontweight="bold",
                )
            inicio += item.peso
        if inicio < self.capacidade:
            ax.barh(
                0,
                self.capacidade - inicio,
                left=inicio,
                height=0.5,
                color=COR_FORA,
                edgecolor=COR_SUPERFICIE,
                linewidth=1,
            )
        ax.plot(
            [self.capacidade] * 2,
            [-0.4, 0.4],
            color=COR_TEXTO,
            linewidth=1,
            linestyle="--",
        )
        linhas = [
            "dentro: "
            + ", ".join(
                f"{j + 1} ({i.peso}/{i.valor})"
                for j, (i, b) in enumerate(zip(self.itens, binaria))
                if b
            ),
            "fora: "
            + ", ".join(
                f"{j + 1} ({i.peso}/{i.valor})"
                for j, (i, b) in enumerate(zip(self.itens, binaria))
                if not b
            ),
        ]
        if self.decodificar is not None:
            linhas.append("ordem: " + ", ".join(str(j + 1) for j in solucao))
        for k, linha in enumerate(linhas):
            ax.text(
                self.capacidade * 1.04,
                0.2 - 0.33 * k,
                linha,
                va="center",
                fontsize=7,
                color=COR_TEXTO_SECUNDARIO,
            )
        peso, valor = self._ponto(solucao)
        ax.set_xlim(0, self.capacidade * 3.1)
        ax.set_ylim(-0.45 - 0.2 * (len(linhas) - 2), 0.45)
        ax.set_axis_off()
        ax.set_title(
            f"1. Solução atual: valor {valor} · peso {peso} de "
            f"C = {self.capacidade}   (item (peso/valor))",
            loc="left",
            fontsize=10,
        )

    def _plano(
        self,
        ax,
        atual: list[int],
        vizinhas: list[tuple[str, list[int]]],
        escolhida: str | None,
        aceito: bool,
        trilha: list[Ponto],
    ) -> list[float]:
        peso_atual, valor_atual = self._ponto(atual)
        ys = [valor_atual]
        xs = [peso_atual]

        caminho = []
        for ponto in trilha:
            if not caminho or ponto != caminho[-1]:
                caminho.append(ponto)
        antigos = caminho[:-TRILHA_RECENTE]
        recentes = caminho[-TRILHA_RECENTE - 1 :]
        if len(antigos) > 1:
            px, py = zip(*antigos)
            ax.plot(px, py, color=COR_ATUAL, linewidth=0.4, alpha=0.15, zorder=1)
            ax.scatter(px, py, s=5, color=COR_ATUAL, alpha=0.15, zorder=1)
        if recentes:
            px, py = zip(*recentes)
            ax.plot(px, py, color=COR_ATUAL, linewidth=1.4, zorder=2)
            ax.scatter(px, py, s=12, color=COR_ATUAL, zorder=2)
            xs += list(px)
            ys += list(py)

        pontos = [(rotulo, self._ponto(solucao)) for rotulo, solucao in vizinhas]
        viaveis = [(r, p) for r, p in pontos if p[0] <= self.capacidade]
        melhor_vizinha = (
            max(viaveis, key=lambda rp: rp[1][1])[0] if viaveis else None
        )
        if len(pontos) > MAX_VIZINHAS:
            prioridade = {escolhida, melhor_vizinha}
            pontos = [rp for rp in pontos if rp[0] in prioridade] + [
                rp for rp in pontos if rp[0] not in prioridade
            ][: MAX_VIZINHAS - len(prioridade)]
        for rotulo, (x, y) in pontos:
            classe = self._classe((x, y), valor_atual)
            cor = {
                "melhora": COR_MELHORA,
                "igual": COR_IGUAL,
                "piora": COR_PIORA,
                "não cabe": COR_CANDIDATO,
            }[classe]
            e_escolhida = rotulo == escolhida
            marcador = "x" if classe == "não cabe" else ("*" if e_escolhida else "o")
            ax.plot(
                [peso_atual, x],
                [valor_atual, y],
                color=COR_ETAPA if e_escolhida else cor,
                linewidth=2.4 if e_escolhida else 0.7,
                linestyle="-" if (aceito or not e_escolhida) else "--",
                alpha=1 if e_escolhida else 0.6,
                zorder=3,
            )
            ax.scatter(
                [x],
                [y],
                s=280 if e_escolhida else 40,
                marker=marcador,
                color=cor,
                zorder=4,
            )
            if e_escolhida or rotulo == melhor_vizinha:
                ax.annotate(
                    rotulo,
                    (x, y),
                    fontsize=8,
                    fontweight="bold",
                    color=COR_TEXTO,
                    xytext=(6, 4),
                    textcoords="offset points",
                )
            xs.append(x)
            ys.append(y)

        if self.melhor_ponto is not None:
            ax.scatter(
                [self.melhor_ponto[0]],
                [self.melhor_ponto[1]],
                s=150,
                marker="D",
                color=COR_MELHOR,
                edgecolor=COR_SUPERFICIE,
                zorder=5,
            )
        ax.scatter([peso_atual], [valor_atual], s=170, color=COR_ETAPA, zorder=6)
        ax.axvline(self.capacidade, color=COR_TEXTO, linewidth=1.2, linestyle="--")
        if self.valor_otimo is not None:
            ax.axhline(self.valor_otimo, color=COR_TEXTO, linewidth=1, linestyle=":")
        ax.set_xlim(0, max(self.capacidade * 1.35, max(xs) * 1.05))
        ax.text(
            self.capacidade,
            0,
            f" C = {self.capacidade} (à direita não cabe)",
            va="bottom",
            fontsize=8.5,
        )
        ax.set_xlabel("peso total da solução")
        ax.set_ylabel("valor total da solução")
        ax.set_title(
            "2. Plano peso × valor: trilha da atual e vizinhas",
            loc="left",
            fontsize=11,
        )
        return ys

    def _historico(self, ax, candidato: tuple[int, float] | None) -> list[float]:
        ys = []
        if self.iteracoes:
            ax.plot(
                self.iteracoes[1:],
                self.candidatos[1:],
                color=COR_CANDIDATO,
                linewidth=0.4,
                alpha=0.6,
            )
            ax.plot(self.iteracoes, self.atuais, color=COR_ATUAL, linewidth=1.0)
            ax.step(
                self.iteracoes,
                self.melhores,
                where="post",
                color=COR_MELHOR,
                linewidth=1.8,
            )
            ax.scatter(
                [self.iteracoes[-1]],
                [self.atuais[-1]],
                color=COR_ETAPA,
                s=60,
                zorder=6,
            )
            ys += self.atuais + self.candidatos + self.melhores
        if candidato is not None:
            anterior = self.atuais[-2] if len(self.atuais) > 1 else None
            if anterior is None or candidato[1] > anterior:
                cor = COR_MELHORA
            else:
                cor = COR_IGUAL if candidato[1] == anterior else COR_PIORA
            ax.scatter(
                [candidato[0]],
                [candidato[1]],
                s=260,
                marker="*",
                color=cor,
                zorder=5,
            )
            ys.append(candidato[1])
        if self.valor_otimo is not None:
            ax.axhline(self.valor_otimo, color=COR_TEXTO, linewidth=1, linestyle=":")
        fim = max([1] + self.iteracoes + ([candidato[0]] if candidato else []))
        ax.set_xlim(-0.02 * fim, fim * 1.03)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel("iteração")
        ax.tick_params(labelleft=False)
        if self.extras:
            chave, pares = next(iter(self.extras.items()))
            eixo = ax.twinx()
            eixo.step(
                [t for t, _ in pares],
                [v for _, v in pares],
                where="post",
                color=COR_EXTRA,
                linewidth=1.2,
                alpha=0.8,
            )
            eixo.set_ylabel(chave, color=COR_EXTRA)
            eixo.tick_params(axis="y", colors=COR_EXTRA, labelcolor=COR_EXTRA)
            eixo.set_ylim(0, max(v for _, v in pares) * 1.1 or 1)
            eixo.grid(False)
            eixo.spines["right"].set_visible(True)
        ax.set_title(
            "3. Mini-histórico (mesma escala de valor do painel 2)",
            loc="left",
            fontsize=11,
        )
        return ys

    def _legenda(self, fig) -> None:
        def ponto(cor, marcador="o", tamanho=7):
            return {
                "marker": marcador,
                "linestyle": "none",
                "color": cor,
                "markersize": tamanho,
            }

        itens = [
            Line2D(
                [],
                [],
                color=COR_ATUAL,
                linewidth=1.6,
                marker="o",
                markersize=3,
                label="atual (trilha no 2, linha no 3)",
            ),
            Line2D([], [], **ponto(COR_ETAPA, tamanho=9), label="etapa atual"),
            Line2D(
                [],
                [],
                color=COR_MELHOR,
                linewidth=1.8,
                marker="D",
                markersize=6,
                label="melhor até agora",
            ),
            Line2D(
                [],
                [],
                **ponto(COR_MELHORA, "*", 13),
                label="escolhida / candidato (cor = melhora ou piora)",
            ),
            Line2D(
                [],
                [],
                color=COR_CANDIDATO,
                linewidth=0.8,
                label="candidatos anteriores (painel 3)",
            ),
            Line2D([], [], **ponto(COR_MELHORA), label="vizinha que melhora"),
            Line2D([], [], **ponto(COR_IGUAL), label="vizinha igual"),
            Line2D([], [], **ponto(COR_PIORA), label="vizinha que piora"),
            Line2D(
                [], [], **ponto(COR_CANDIDATO, "x"), label="vizinha que não cabe"
            ),
        ]
        if self.valor_otimo is not None:
            itens.append(
                Line2D(
                    [],
                    [],
                    color=COR_TEXTO,
                    linewidth=1,
                    linestyle=":",
                    label=f"ótimo ({self.valor_otimo})",
                )
            )
        if self.extras:
            itens.append(
                Line2D(
                    [],
                    [],
                    color=COR_EXTRA,
                    linewidth=1.2,
                    label=f"{next(iter(self.extras))} (eixo da direita)",
                )
            )
        fig.legend(handles=itens, loc="outside lower center", ncol=5, fontsize=8.5)
