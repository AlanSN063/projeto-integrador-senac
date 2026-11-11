from base_model import BaseModel


class FornecedorModel(BaseModel):
    tabela = "fornecedor"
    campos = ("razao_social", "cnpj", "telefone", "email")
