from base_model import BaseModel


class MovimentacaoEstoqueModel(BaseModel):
    tabela = "movimentacao_estoque"
    campos = (
        "usuario_id",
        "fornecedor_id",
        "ordem_servico_id",
        "tipo",
        "motivo",
        "data_movimentacao",
        "observacao",
    )
