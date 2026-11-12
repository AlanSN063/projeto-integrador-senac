import customtkinter as ctk
from .theme import COLORS
from .components import Sidebar
from .dashboard_view import DashboardView
from .produtos_view import ProdutosView
from .ordens_servico_view import OrdensServicoView
from .placeholder_view import PlaceholderView


class MainView(ctk.CTkFrame):
    def __init__(self, master, on_logout=None, callbacks=None, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.callbacks = callbacks or {}
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self, self.mostrar_tela, on_logout)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.views = {}
        self.mostrar_tela("Início")

    def mostrar_tela(self, nome):
        for view in self.views.values():
            view.grid_forget()

        if nome not in self.views:
            if nome == "Início":
                view = DashboardView(
                    self.content,
                    resumo=self.callbacks.get("resumo_dashboard"),
                    movimentacoes=self.callbacks.get("movimentacoes_recentes")
                )
            elif nome == "Produtos":
                view = ProdutosView(
                    self.content,
                    on_salvar=self.callbacks.get("salvar_produto"),
                    on_limpar=self.callbacks.get("limpar_produto"),
                    on_buscar=self.callbacks.get("buscar_produto")
                )
            elif nome == "Ordens de serviço":
                view = OrdensServicoView(
                    self.content,
                    ordens=self.callbacks.get("listar_ordens"),
                    on_nova_ordem=self.callbacks.get("nova_ordem"),
                    on_visualizar=self.callbacks.get("visualizar_ordem"),
                    on_editar=self.callbacks.get("editar_ordem"),
                    on_excluir=self.callbacks.get("excluir_ordem")
                )
            else:
                descricoes = {
                    "Fornecedores": "Cadastro e consulta de fornecedores.",
                    "Categorias": "Organização e manutenção das categorias.",
                    "Movimentações": "Registro de entradas e saídas do estoque.",
                    "Usuários": "Gerenciamento de usuários e permissões.",
                    "Relatórios": "Indicadores e consultas do estoque.",
                    "Configurações": "Ajustes gerais do sistema."
                }
                view = PlaceholderView(
                    self.content, nome, descricoes.get(nome, "Área do sistema.")
                )
            self.views[nome] = view

        self.views[nome].grid(row=0, column=0, sticky="nsew")
        self.sidebar.set_active(nome)
