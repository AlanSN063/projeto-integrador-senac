
from models.relatorio_model import RelatorioModel


class RelatorioController:

    def __init__(self, model=None):
        self.model = model or RelatorioModel()

    def gerar(self, tipo):
        tipos_validos = (
            "estoque_atual",
            "estoque_baixo",
            "movimentacoes",
            "categorias"
        )

        if tipo not in tipos_validos:
            raise ValueError(
                "Selecione um relatório válido."
            )

        return self.model.gerar(tipo)

