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
from controllers.fornecedor_controller import FornecedorController
from controllers.categoria_controller import CategoriaController
from controllers.movimentacao_controller import MovimentacaoController

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
        self.fornecedor_controller = FornecedorController()
        self.categoria_controller = CategoriaController()
        self.movimentacao_controller = MovimentacaoController()
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

            # Produtos
            "salvar_produto": self._salvar_produto,
            "buscar_produto": self._buscar_produto,
            "listar_categorias": self.produto_controller.listar_categorias,

            # Categorias
            "salvar_categoria": self._salvar_categoria,
            "atualizar_categoria": self._atualizar_categoria,
            "excluir_categoria": self._excluir_categoria,
            "listar_categorias_view": self._listar_categorias,

            # Ordens de serviço
            "listar_ordens": self.ordem_controller.listar,
            "nova_ordem": self.ordem_controller.nova_ordem,
            "visualizar_ordem": self.ordem_controller.visualizar,
            "editar_ordem": self.ordem_controller.editar,
            "excluir_ordem": self.ordem_controller.excluir,

            # Movimentações
            "salvar_movimentacao": self._salvar_movimentacao,
            "listar_movimentacoes": self._listar_movimentacoes,
            "carregar_dados_movimentacao": self._carregar_dados_movimentacao,
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

    def _salvar_fornecedor(self, dados):
        return self.fornecedor_controller.cadastrar(**dados)


    def _atualizar_fornecedor(self, fornecedor_id, dados):
        return self.fornecedor_controller.atualizar(
            fornecedor_id,
            **dados
        )


    def _excluir_fornecedor(self, fornecedor_id):
        return self.fornecedor_controller.excluir(fornecedor_id)


    def _listar_fornecedores(self):
        return self.fornecedor_controller.listar()

    def _logout(self):
        self.main_view.destroy()
        self.usuario_logado = None
        self.login_view = LoginView(self, on_login=self._login)
        self.login_view.pack(fill="both", expand=True)

    def _salvar_categoria(self, dados):
        try:
            categoria_id = self.categoria_controller.cadastrar(**dados)
            messagebox.showinfo(
                "Categorias",
                f"Categoria cadastrada com sucesso! ID: {categoria_id}",
                parent=self
            )
            return True

        except Exception as exc:
            messagebox.showerror(
                "Erro ao cadastrar categoria",
                str(exc),
                parent=self
            )
            return False


    def _atualizar_categoria(self, categoria_id, dados):
        try:
            resultado = self.categoria_controller.atualizar(
                categoria_id,
                **dados
            )

            if resultado:
                messagebox.showinfo(
                    "Categorias",
                    "Categoria atualizada com sucesso!",
                    parent=self
                )
                return True

            return False

        except Exception as exc:
            messagebox.showerror(
                "Erro ao atualizar categoria",
                str(exc),
                parent=self
            )
            return False


    def _excluir_categoria(self, categoria_id):
        try:
            resultado = self.categoria_controller.excluir(categoria_id)

            if resultado:
                messagebox.showinfo(
                    "Categorias",
                    "Categoria excluída com sucesso!",
                    parent=self
                )
                return True

            return False

        except Exception as exc:
            messagebox.showerror(
                "Erro ao excluir categoria",
                str(exc),
                parent=self
            )
            return False


    def _listar_categorias(self):
        return self.categoria_controller.listar()

    def _salvar_movimentacao(self, dados):
        try:
            usuario_id = self.usuario_logado["id"]
            return self.movimentacao_controller.cadastrar(
                usuario_id, dados
            )
        except Exception as exc:
            messagebox.showerror(
                "Erro de movimentação", str(exc), parent=self
            )
            return False


    def _listar_movimentacoes(self, termo=None):
        return self.movimentacao_controller.listar(termo)


    def _carregar_dados_movimentacao(self):
        return {
            "produtos": self.movimentacao_controller.listar_produtos(),
            "fornecedores": self.movimentacao_controller.listar_fornecedores(),
            "ordens": self.movimentacao_controller.listar_ordens_servico(),
        }

if __name__ == "__main__":
    app = EstoqueApp()
    app.mainloop()