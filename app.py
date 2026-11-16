import customtkinter as ctk
from tkinter import messagebox

from conexao import conectar
from views.theme import configure_appearance, COLORS
from views.login_view import LoginView
from views.main_view import MainView
from controllers.login_controller import LoginController
from controllers.dashboard_controller import DashboardController
from controllers.produto_controller import ProdutoController
from controllers.ordem_servico_controller import OrdemServicoController


class EstoqueApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        configure_appearance()
        self.title("Controle de Estoque")
        self.geometry("1360x820")
        self.minsize(1050, 680)
        self.configure(fg_color=COLORS["background"])

        self.login_controller = LoginController()
        self.dashboard_controller = DashboardController()
        self.produto_controller = ProdutoController()
        self.usuario_logado = None
        self.login_view = LoginView(self, on_login=self._login)
        self.login_view.pack(fill="both", expand=True)

    def _login(self, usuario, senha):
        try:
            self.usuario_logado = self.login_controller.autenticar(usuario, senha)
            self.login_view.destroy()
            self._abrir_sistema()
        except ValueError as exc:
            self.login_view.show_error(str(exc))
        except Exception as exc:
            messagebox.showerror("Erro de conexão",
                f"Não foi possível acessar o banco de dados.\n{exc}", parent=self)

    def _abrir_sistema(self):
        self.ordem_controller = OrdemServicoController(self, on_change=self._refresh_orders)
        callbacks = {
            "resumo_dashboard": self.dashboard_controller.resumo,
            "movimentacoes_recentes": self.dashboard_controller.movimentacoes_recentes,
            "estoque_por_categoria": self.dashboard_controller.estoque_por_categoria,
            "salvar_produto": self._salvar_produto,
            "buscar_produto": self._buscar_produto,
            "listar_categorias": self.produto_controller.listar_categorias,
            "listar_ordens": self.ordem_controller.listar,
            "nova_ordem": self.ordem_controller.nova_ordem,
            "visualizar_ordem": self.ordem_controller.visualizar,
            "editar_ordem": self.ordem_controller.editar,
            "excluir_ordem": self.ordem_controller.excluir,
        }
        self.main_view = MainView(self, on_logout=self._logout, callbacks=callbacks)
        self.main_view.pack(fill="both", expand=True)

    def _salvar_produto(self, dados):
        try:
            produto_id = self.produto_controller.salvar(dados)
            messagebox.showinfo("Produtos", f"Produto cadastrado com sucesso! ID: {produto_id}", parent=self)
            return True
        except Exception as exc:
            messagebox.showerror("Não foi possível salvar", str(exc), parent=self)
            return False

    def _refresh_orders(self):
        if hasattr(self, "main_view") and "Ordens de serviço" in self.main_view.views:
            self.main_view.views["Ordens de serviço"].atualizar(self.ordem_controller.listar())

    def _buscar_produto(self, termo=None):
        try:
            produtos = self.produto_controller.listar(termo)
            if not produtos:
                messagebox.showinfo("Produtos", "Nenhum produto encontrado.", parent=self)
                return
            linhas = [f"{p['codigo']} | {p['nome']} | Estoque: {p['estoque_atual']} | Mínimo: {p['estoque_minimo']}" for p in produtos]
            messagebox.showinfo("Produtos cadastrados", "\n".join(linhas), parent=self)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc), parent=self)

    def _logout(self):
        self.main_view.destroy()
        self.usuario_logado = None
        self.login_view = LoginView(self, on_login=self._login)
        self.login_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = EstoqueApp()
    app.mainloop()
