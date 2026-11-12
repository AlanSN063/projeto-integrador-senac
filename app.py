import customtkinter as ctk
from views.theme import configure_appearance, COLORS
from views.login_view import LoginView
from views.main_view import MainView


class EstoqueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        configure_appearance()
        self.title("Controle de Estoque")
        self.geometry("1360x820")
        self.minsize(1050, 680)
        self.configure(fg_color=COLORS["background"])

        self.login_view = LoginView(self, on_login=self._login)
        self.login_view.pack(fill="both", expand=True)

        # Substitua estes callbacks pelas funções do Controller.
        self.callbacks = {
            "salvar_produto": self._salvar_produto_demo,
            "nova_ordem": lambda: print("Controller: abrir formulário de nova OS"),
            "visualizar_ordem": lambda item_id: print("Visualizar OS:", item_id),
            "editar_ordem": lambda item_id: print("Editar OS:", item_id),
            "excluir_ordem": lambda item_id: print("Excluir OS:", item_id),
        }

    def _login(self, usuario, senha):
        # Ponto de integração: validar credenciais no Controller/Model.
        # A validação abaixo serve apenas para demonstrar a navegação da View.
        if not usuario or not senha:
            self.login_view.show_error("Usuário e senha são obrigatórios.")
            return
        self.login_view.destroy()
        self.main_view = MainView(
            self, on_logout=self._logout, callbacks=self.callbacks
        )
        self.main_view.pack(fill="both", expand=True)

    def _logout(self):
        self.main_view.destroy()
        self.login_view = LoginView(self, on_login=self._login)
        self.login_view.pack(fill="both", expand=True)

    @staticmethod
    def _salvar_produto_demo(dados):
        print("Dados recebidos pela View; encaminhe ao Controller:")
        print(dados)


if __name__ == "__main__":
    app = EstoqueApp()
    app.mainloop()
