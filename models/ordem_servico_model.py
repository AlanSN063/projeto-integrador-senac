from base_model import BaseModel


class OrdemServicoModel(BaseModel):
    tabela = "ordem_servico"
    campos = (
        "numero",
        "cliente_nome",
        "placa_veiculo",
        "descricao_servico",
        "status",
        "data_abertura",
    )
