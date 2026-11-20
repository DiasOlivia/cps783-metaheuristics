import random


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
        self.custos: dict[FacilidadeId, int] = {}
        self.conflitos: set[ClienteId] = set()

    def __repr__(self) -> str:
        return f"Cliente(demanda={self.demanda}, id={self.id})"

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

    def gen_solucao_inicial_gulosa(self) -> Solucao:
        demanda_by_cliente = self.demanda_by_cliente()

        abertas: list[FacilidadeId] = []
        alocacao: dict[tuple[ClienteId, FacilidadeId], int] = {}
        custo_total = 0

        for facilidade in sorted(
            self.facilidades, key=lambda f: f.custo_by_capacidade
        ):
            if not any(demanda_by_cliente.values()):
                break

            abertas.append(facilidade.id)
            custo_total += facilidade.custo_fixo
            capacidade = facilidade.capacidade
            atendidos: set[ClienteId] = set()

            for cliente in sorted(
                self.clientes,
                key=lambda c: c.custo_transporte(facilidade),
            ):
                if capacidade == 0:
                    break
                if demanda_by_cliente[cliente.id] == 0:
                    continue
                if cliente.conflitos & atendidos:
                    continue

                quantidade = min(demanda_by_cliente[cliente.id], capacidade)
                alocacao[(cliente.id, facilidade.id)] = quantidade
                demanda_by_cliente[cliente.id] -= quantidade
                capacidade -= quantidade
                atendidos.add(cliente.id)
                custo_total += cliente.custo_transporte(facilidade) * quantidade

        if any(demanda_by_cliente.values()):
            raise ValueError(
                "A solução gulosa não atende toda a demanda com todas as facilidades abertas."
            )

        return Solucao(abertas=abertas, alocacao=alocacao, custo_total=custo_total)
