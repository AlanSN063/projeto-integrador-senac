from models.usuario_model import UsuarioModel


class LoginController:
    def __init__(self, usuario_model=None):
        self.usuario_model = usuario_model or UsuarioModel()

    def autenticar(self, login, senha):
        login = (login or "").strip()
        if not login or not senha:
            raise ValueError("Informe o usuário e a senha.")
        usuario = self.usuario_model.autenticar(login, senha)
        if not usuario:
            raise ValueError("Usuário ou senha inválidos, ou usuário inativo.")
        return usuario
