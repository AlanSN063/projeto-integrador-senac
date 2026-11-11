from base_model import BaseModel


class ProdutoModel(BaseModel):
    tabela = "produto"
    campos = (
        "categoria_id",
        "codigo",
        "nome",
        "marca",
        "preco_venda",
        "estoque_minimo",
        "ativo",
    )
