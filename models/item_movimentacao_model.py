from base_model import BaseModel


class ItemMovimentacaoModel(BaseModel):
    tabela = "item_movimentacao"
    campos = (
        "movimentacao_id",
        "produto_id",
        "quantidade",
        "valor_unitario",
    )
