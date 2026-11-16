from controllers.cadastro_controller import CadastroController
from models.usuario_model import UsuarioModel

class UsuarioController(CadastroController):
    def __init__(self): super().__init__(UsuarioModel())

    def cadastrar_usuario(self, nome, login, senha, cargo="OPERADOR"):
        if not nome.strip() or not login.strip() or not senha:
            raise ValueError("Nome, login e senha são obrigatórios.")
        return self.model.criar_usuario(nome, login, senha, cargo)
