import random

from metaheuristics.utils import ordem
from metaheuristics.utils.instancia import gerar_instancia_aleatoria


def test_busca_local_primeira_melhora__nao_piora_e_termina_em_otimo_local():
    random.seed(1)
    itens = gerar_instancia_aleatoria(10, 20, 100)
    capacidade = sum(item.peso for item in itens) // 2
    inicial = ordem.construtiva_aleatoria(itens, capacidade)
    final, avaliacoes = ordem.busca_local_primeira_melhora(
        inicial, itens, capacidade
    )
    valor = ordem.avaliar(final, itens, capacidade)

    assert sorted(final) == list(range(10))
    assert valor >= ordem.avaliar(inicial, itens, capacidade)
    assert avaliacoes >= 45  # ao menos a última passada, com as 45 trocas
    for i in range(9):
        for j in range(i + 1, 10):
            vizinha = list(final)
            vizinha[i], vizinha[j] = vizinha[j], vizinha[i]
            assert ordem.avaliar(vizinha, itens, capacidade) <= valor
