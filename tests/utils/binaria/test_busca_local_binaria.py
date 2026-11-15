import random

import pytest

from metaheuristics.utils import binaria
from metaheuristics.utils.instancia import Item
from metaheuristics.utils.instancia import gerar_instancia_aleatoria


class DebugFalso:
    def __init__(self):
        self.passos = []

    def passo(self, etapa, atual, vizinhas, escolhida=None, nota=""):
        self.passos.append((etapa, len(vizinhas), escolhida))


def _e_otimo_local(solucao, itens, capacidade):
    valor, _ = binaria.calcular_valor_peso(solucao, itens, capacidade)
    for i in range(len(solucao)):
        for j in range(i, len(solucao)):
            vizinha = list(solucao)
            vizinha[i] ^= 1
            if j != i:
                if solucao[i] == solucao[j]:
                    continue
                vizinha[j] ^= 1
            novo_valor, peso = binaria.calcular_valor_peso(
                vizinha, itens, capacidade
            )
            if peso <= capacidade and novo_valor > valor:
                return False
    return True


@pytest.mark.parametrize(
    ("buscar", "esperado"),
    [
        (binaria.busca_local_melhor_melhora, (8, 4)),
        # a primeira melhora entra com o item 2 (valor 7) e para num ótimo local
        # diferente do da melhor melhora
        (binaria.busca_local_primeira_melhora, (7, 5)),
    ],
)
def test_busca_local__nao_piora_e_respeita_capacidade(buscar, esperado):
    itens = [Item(2, 3), Item(3, 4), Item(4, 8)]
    inicial = [1, 0, 0]
    final, avaliacoes = buscar(inicial, itens, 5)
    assert inicial == [1, 0, 0]  # entrada não é modificada
    assert binaria.calcular_valor_peso(final, itens, 5) == esperado
    assert avaliacoes > 0


@pytest.mark.parametrize(
    "buscar",
    [binaria.busca_local_melhor_melhora, binaria.busca_local_primeira_melhora],
)
def test_busca_local__termina_em_otimo_local(buscar):
    random.seed(1)
    itens = gerar_instancia_aleatoria(15, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    final, _ = buscar(
        binaria.construtiva_aleatoria(itens, capacidade), itens, capacidade
    )
    assert _e_otimo_local(final, itens, capacidade)


def test_busca_local__um_passo_de_debug_por_passada():
    itens = [Item(2, 3), Item(3, 4), Item(4, 8)]
    debug = DebugFalso()
    binaria.busca_local_melhor_melhora([1, 0, 0], itens, 5, debug=debug)
    assert [escolhida for _, _, escolhida in debug.passos] == ["1→3", None]
