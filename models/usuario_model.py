from base_model import BaseModel


class UsuarioModel(BaseModel):
    tabela = "usuario"
    campos = ("nome", "login", "cargo", "ativo")
