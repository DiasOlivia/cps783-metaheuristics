import json
from pathlib import Path
from typing import Any

import pytest

NOTEBOOK = (
    Path(__file__).parents[2]
    / "metaheuristics"
    / "trabalho"
    / "Trabalho_MH_Grafos.ipynb"
)


def funcoes_do_notebook() -> dict[str, Any]:
    """Executa as células de código do notebook, menos as com a tag ``experimento``."""
    celulas = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    namespace: dict[str, Any] = {}
    for celula in celulas:
        if celula["cell_type"] != "code":
            continue
        if "experimento" in celula["metadata"].get("tags", []):
            continue
        exec("".join(celula["source"]), namespace)  # noqa: S102
    return namespace


@pytest.fixture(scope="session")
def notebook() -> dict[str, Any]:
    """Funções e variáveis definidas pelo notebook, como ``Instance`` e ``instance``."""
    return funcoes_do_notebook()
