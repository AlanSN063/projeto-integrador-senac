from controllers.cadastro_controller import CadastroController
from models.usuario_model import UsuarioModel

from models.usuario_model import UsuarioModel


class UsuarioController(CadastroController):
    def __init__(self): super().__init__(UsuarioModel())



class UsuarioController:
    def __init__(self):
        self.model = UsuarioModel()

    def cadastrar_usuario(self, nome, login, senha, cargo="OPERADOR"):
        if not nome.strip() or not login.strip() or not senha:
            raise ValueError("Nome, login e senha são obrigatórios.")
        return self.model.criar_usuario(nome, login, senha, cargo)

    def listar(self):
        """Lista usuários sem retornar o hash das senhas."""
        usuarios = self.model.listar()

        campos_publicos = ("id", "nome", "login", "cargo", "ativo")

        return [
            {campo: usuario.get(campo) for campo in campos_publicos}
            for usuario in usuarios
        ]

    def cadastrar(self, dados):
        nome = dados.get("nome", "").strip()
        login = dados.get("login", "").strip()
        senha = dados.get("senha", "")
        cargo = dados.get("cargo", "OPERADOR").strip()

        if not nome or not login or not senha:
            raise ValueError(
                "Nome, login e senha são obrigatórios."
            )

        if len(senha) < 8:
            raise ValueError(
                "A senha deve possuir pelo menos 8 caracteres."
            )

        if not cargo:
            raise ValueError("Informe o cargo do usuário.")

        return self.model.criar_usuario(
            nome=nome,
            login=login,
            senha=senha,
            cargo=cargo
        )

    def atualizar(self, usuario_id, dados):
        nome = dados.get("nome", "").strip()
        login = dados.get("login", "").strip()
        cargo = dados.get("cargo", "").strip()

        if not nome or not login or not cargo:
            raise ValueError(
                "Nome, login e cargo são obrigatórios."
            )

        atualizacoes = {
            "nome": nome,
            "login": login,
            "cargo": cargo,
            "ativo": dados.get("ativo", True)
        }

        senha = dados.get("senha", "")

        # Somente altera a senha quando uma nova for informada.
        if senha:
            if len(senha) < 8:
                raise ValueError(
                    "A nova senha deve possuir pelo menos 8 caracteres."
                )

            atualizacoes["senha_hash"] = (
                self.model.gerar_hash(senha)
            )

        return self.model.atualizar(
            usuario_id,
            **atualizacoes
        )

    def desativar(self, usuario_id):
        """Desativa sem apagar o histórico relacionado ao usuário."""
        return self.model.atualizar(
            usuario_id,
            ativo=False
        )
