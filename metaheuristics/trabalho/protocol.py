import random
from collections.abc import Mapping

from metaheuristics.trabalho.instance import Instance


class ClienteId(int):
    def __repr__(self) -> str:
        return f"C{int(self)}"


class FacilidadeId(int):
    def __repr__(self) -> str:
        return f"F{int(self)}"


class Cliente:
    def __init__(self, demanda: int, id: int) -> None:
        self.demanda = demanda
        self.id = ClienteId(id)
        self.custos: dict[FacilidadeId, int] = {}  # custo para cada facilidade
        self.conflitos: set[ClienteId] = set()

    def __repr__(self) -> str:
        return f"Cliente(demanda={self.demanda}, id={self.id}, custos={self.custos}, conflitos={self.conflitos})"

    def custo_transporte(self, facilidade: "Facilidade") -> int:
        return self.custos[facilidade.id]

    @staticmethod
    def gen_random_clientes(
        num_itens: int = 4,
        max_demanda: int = 30,
    ) -> list["Cliente"]:
        itens: list[Cliente] = []
        for id in range(num_itens):
            demanda = random.randint(1, max_demanda)
            itens.append(
                Cliente(
                    demanda=demanda,
                    id=id + 1,
                )
            )
        return itens

    @staticmethod
    def gen_clientes(demandas: list[int]) -> list["Cliente"]:
        itens: list[Cliente] = []
        for idx, cap in enumerate(demandas):
            itens.append(Cliente(demanda=cap, id=idx + 1))
        return itens


class Facilidade:
    def __init__(self, capacidade: int, custo_fixo: int, id: int) -> None:
        self.capacidade = capacidade
        self.custo_fixo = custo_fixo
        self.id = FacilidadeId(id)

    def __repr__(self) -> str:
        return f"Facilidade(capacidade={self.capacidade}, custo_fixo={self.custo_fixo}, id={self.id})"

    @property
    def custo_by_capacidade(self) -> float:
        return self.custo_fixo / self.capacidade

    @staticmethod
    def gen_random_facilities(
        num_itens: int = 4,
        max_capacidade: int = 95,
        max_custo_fixo: int = 600,
    ) -> list["Facilidade"]:
        itens: list[Facilidade] = []
        for id in range(num_itens):
            capacidade = random.randint(1, max_capacidade)
            custo_fixo = random.randint(1, max_custo_fixo)
            itens.append(
                Facilidade(
                    capacidade=capacidade,
                    custo_fixo=custo_fixo,
                    id=id + 1,
                )
            )
        return itens

    def alocar(
        self,
        clientes: list[Cliente],
        demanda_restante: Mapping[ClienteId, int],
    ) -> tuple[dict[ClienteId, int], int]:
        """Calcula quanto a ``facilidade`` envia a cada cliente.

        Os clientes são atendidos do menor para o maior custo de transporte.
        Devolve os envios por cliente e o custo de transporte deles.
        """
        capacidade = self.capacidade
        envios: dict[ClienteId, int] = {}
        custo_transporte = 0

        for cliente in sorted(clientes, key=lambda c: c.custo_transporte(self)):
            if capacidade == 0:
                break
            if demanda_restante[cliente.id] == 0:
                continue
            if cliente.conflitos & envios.keys():
                continue

            quantidade = min(demanda_restante[cliente.id], capacidade)
            envios[cliente.id] = quantidade
            capacidade -= quantidade
            custo_transporte += cliente.custo_transporte(self) * quantidade

        return envios, custo_transporte

    @staticmethod
    def gen_facilities(
        capacidades: list[int],
        custos_fixos: list[int],
    ) -> list["Facilidade"]:
        if len(capacidades) != len(custos_fixos):
            raise ValueError(
                "Quantidade de capacidades e custos_fixos devem ser iguais."
            )

        itens: list[Facilidade] = []
        for idx, cap in enumerate(capacidades):
            itens.append(
                Facilidade(capacidade=cap, custo_fixo=custos_fixos[idx], id=idx + 1)
            )
        return itens


class Solucao:
    """
    Attributes
    ----------
    abertas : list of FacilidadeId
        Ids das facilidades abertas, na ordem de abertura.
    alocacao : dict of {(ClienteId, FacilidadeId): int}
        Quanto cada facilidade envia a cada cliente, indexado por
        ``(cliente_id, facilidade_id)``. Um cliente pode ser atendido por mais de
        uma facilidade, e pares ausentes não recebem nada.
    custo_total : int
        Custos fixos das facilidades abertas mais os custos de transporte.
    """

    def __init__(
        self,
        abertas: list[FacilidadeId],
        alocacao: dict[tuple[ClienteId, FacilidadeId], int],
        custo_total: int,
    ) -> None:
        self.abertas = abertas
        self.alocacao = alocacao
        self.custo_total = custo_total

    def __repr__(self) -> str:
        return f"Solucao(abertas={self.abertas}, alocacao={self.alocacao}, custo_total={self.custo_total})"


class Problem:
    def __init__(
        self, facilidades: list[Facilidade], clientes: list[Cliente]
    ) -> None:
        self.facilidades = facilidades
        self.clientes = clientes

    def __repr__(self) -> str:
        return f"Problem(facilidades={self.facilidades}, clientes={self.clientes})"

    def demanda_by_cliente(self) -> dict[ClienteId, int]:
        return {cliente.id: cliente.demanda for cliente in self.clientes}

    @staticmethod
    def gen_random_problem(
        facilidade_num_itens: int = 4,
        facilidade_max_capacidade: int = 95,
        facilidade_max_custo_fixo: int = 600,
        cliente_num_itens: int = 4,
        cliente_max_demanda: int = 30,
        max_custo: int = 100,
        n_conflito: int = 3,
    ) -> "Problem":
        facilidades = Facilidade.gen_random_facilities(
            num_itens=facilidade_num_itens,
            max_capacidade=facilidade_max_capacidade,
            max_custo_fixo=facilidade_max_custo_fixo,
        )

        clientes = Cliente.gen_random_clientes(
            num_itens=cliente_num_itens,
            max_demanda=cliente_max_demanda,
        )

        for cliente in clientes:
            for facilidade in facilidades:
                cliente.custos[facilidade.id] = random.randint(1, max_custo)

        for _ in range(n_conflito):
            cliente_a, cliente_b = random.sample(clientes, 2)
            cliente_a.conflitos.add(cliente_b.id)
            cliente_b.conflitos.add(cliente_a.id)

        return Problem(facilidades=facilidades, clientes=clientes)

    @staticmethod
    def gen_problem_from_instance(instance: Instance) -> "Problem":
        return Problem.gen_problem(
            capacidades=instance.capacidades.tolist(),
            custos_fixos=instance.custos_fixos.tolist(),
            demandas=instance.demandas.tolist(),
            custo_transporte=instance.custos_transporte.tolist(),
            pares_conflitantes=instance.pares_conflitantes_brutos,
        )

    @staticmethod
    def gen_problem(
        capacidades: list[int],
        custos_fixos: list[int],
        demandas: list[int],
        custo_transporte: list[list[int]],
        pares_conflitantes: list[tuple[int, int]],
    ) -> "Problem":
        facilidades = Facilidade.gen_facilities(
            capacidades=capacidades, custos_fixos=custos_fixos
        )
        clientes = Cliente.gen_clientes(demandas=demandas)

        for cliente, custos in zip(clientes, custo_transporte, strict=True):
            for facilidade, custo in zip(facilidades, custos, strict=True):
                cliente.custos[facilidade.id] = custo

        for a, b in pares_conflitantes:
            clientes[a - 1].conflitos.add(clientes[b - 1].id)
            clientes[b - 1].conflitos.add(clientes[a - 1].id)

        return Problem(facilidades=facilidades, clientes=clientes)

    def solve(self, ordem: list[Facilidade]) -> Solucao:
        """Abre as facilidades na ``ordem`` dada até atender toda a demanda.
        As facilidades do fim da ordem que não forem necessárias ficam fechadas.
        """
        demanda_by_cliente = self.demanda_by_cliente()

        abertas: list[FacilidadeId] = []
        alocacao: dict[tuple[ClienteId, FacilidadeId], int] = {}
        custo_total = 0

        for facilidade in ordem:
            if not any(demanda_by_cliente.values()):
                break

            envios, custo_transporte = facilidade.alocar(
                self.clientes, demanda_by_cliente
            )
            for cliente_id, quantidade in envios.items():
                alocacao[(cliente_id, facilidade.id)] = quantidade
                demanda_by_cliente[cliente_id] -= quantidade

            abertas.append(facilidade.id)
            custo_total += facilidade.custo_fixo + custo_transporte

        if any(demanda_by_cliente.values()):
            raise ValueError(
                "A ordem não atende toda a demanda, mesmo abrindo todas as facilidades."
            )

        return Solucao(abertas=abertas, alocacao=alocacao, custo_total=custo_total)

    def gen_solucao_aleatoria_gulosa(self, alfa: float) -> Solucao:
        demanda_restante = self.demanda_by_cliente()
        fechadas = list(self.facilidades)
        ordem: list[Facilidade] = []

        while any(demanda_restante.values()) and fechadas:
            custos = {f: f.custo_by_capacidade for f in fechadas}

            # avaliadas = {
            #     f: f.alocar(self.clientes, demanda_restante) for f in fechadas
            # }
            # custos = {
            #     f: (f.custo_fixo + custo_transporte) / sum(envios.values())
            #     for f, (envios, custo_transporte) in avaliadas.items()
            #     if envios
            # }
            if not custos:
                break

            lrc = _gen_lrc(custos, alfa)
            facilidade = random.choice(lrc)
            fechadas.remove(facilidade)
            ordem.append(facilidade)

            envios, _ = facilidade.alocar(self.clientes, demanda_restante)
            # envios, _ = avaliadas[facilidade]

            for cliente_id, quantidade in envios.items():
                demanda_restante[cliente_id] -= quantidade

        return self.solve(ordem)

    def gen_solucao_inicial_gulosa(self) -> Solucao:
        return self.solve(
            sorted(self.facilidades, key=lambda f: f.custo_by_capacidade)
        )


def _gen_lrc(custos: dict[Facilidade, float], alfa: float) -> list[Facilidade]:
    if alfa < 0 or alfa > 1:
        raise ValueError(f"O valor de alfa precisa estar entre 0 e 1, ele é {alfa}")

    c_min, c_max = min(custos.values()), max(custos.values())
    limite = max(c_min, (1 - alfa) * c_min + alfa * c_max)  # erro de arredondamento
    return [f for f, c in custos.items() if c <= limite]
