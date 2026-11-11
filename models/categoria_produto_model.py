from base_model import BaseModel


class CategoriaProdutoModel(BaseModel):
    tabela = "categoria_produto"
    campos = ("nome", "descricao")
