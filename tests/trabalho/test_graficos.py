ROTULOS = {
    "Gulosa": "Gulosa",
    "GRASP": "GRASP",
    "GRASP + SA": "GRASP + SA",
    "GRASP + SA com grafos": "GRASP + SA (grafos)",
    "GA": "GA",
}


def _rodada(semente: int, custo_final: int) -> dict:
    resultado = {
        "custo": custo_final,
        "historico": [120, 110, custo_final],
        "progresso": [(1, 110), (2, custo_final)],
    }
    return {"semente": semente, **{metodo: resultado for metodo in ROTULOS}}


def test_salvar_graficos_grafos_salva_os_tres_pngs(notebook, tmp_path):
    caminhos = notebook["salvar_graficos_grafos"](
        [_rodada(1, 100), _rodada(2, 105)], ROTULOS, tmp_path
    )

    assert [caminho.name for caminho in caminhos] == [
        "boxplot_custos_grafos.png",
        "convergencia_metodos_grafos.png",
        "progresso_iteracoes_geracoes_grafos.png",
    ]
    assert all(caminho.exists() for caminho in caminhos)
