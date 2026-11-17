
import customtkinter as ctk
from .theme import COLORS, FONTS
from .components import PageHeader


class RelatoriosView(ctk.CTkFrame):
    """
    Tela de relatórios do controle de estoque.

    Callback esperado:
        on_carregar(tipo: str) -> list[dict]

    Tipos:
        estoque_atual
        estoque_baixo
        movimentacoes
        categorias
    """

    RELATORIOS = {
        "Estoque atual": {
            "tipo": "estoque_atual",
            "colunas": [
                ("codigo", "Código"),
                ("produto", "Produto"),
                ("categoria", "Categoria"),
                ("estoque_atual", "Estoque"),
                ("estoque_minimo", "Mínimo"),
            ],
        },
        "Estoque baixo": {
            "tipo": "estoque_baixo",
            "colunas": [
                ("codigo", "Código"),
                ("produto", "Produto"),
                ("categoria", "Categoria"),
                ("estoque_atual", "Estoque atual"),
                ("estoque_minimo", "Estoque mínimo"),
            ],
        },
        "Movimentações": {
            "tipo": "movimentacoes",
            "colunas": [
                ("data_movimentacao", "Data"),
                ("tipo", "Tipo"),
                ("motivo", "Motivo"),
                ("produto", "Produto"),
                ("quantidade", "Quantidade"),
                ("usuario", "Responsável"),
            ],
        },
        "Estoque por categoria": {
            "tipo": "categorias",
            "colunas": [
                ("categoria", "Categoria"),
                ("total_produtos", "Produtos"),
                ("total_unidades", "Unidades"),
            ],
        },
    }

    def __init__(
        self,
        master,
        on_carregar=None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["background"],
            **kwargs
        )

        self.on_carregar = on_carregar
        self.dados = []
        self.relatorio_atual = "Estoque atual"

        PageHeader(
            self,
            "Relatórios",
            "Consulte indicadores e informações do estoque",
            "chart-no-axes-combined"
        ).pack(
            fill="x",
            padx=22,
            pady=(22, 16)
        )

        self._criar_conteudo()

        self.carregar_relatorio()

    # =====================================
    # CONTEÚDO PRINCIPAL
    # =====================================

    def _criar_conteudo(self):

        conteudo = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        conteudo.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=(0, 22)
        )

        conteudo.grid_columnconfigure(0, weight=1)
        conteudo.grid_rowconfigure(1, weight=1)

        self._criar_filtros(conteudo)
        self._criar_tabela(conteudo)

    # =====================================
    # FILTROS
    # =====================================

    def _criar_filtros(self, master):

        painel = ctk.CTkFrame(
            master,
            fg_color=COLORS["white"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )

        painel.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 14)
        )

        painel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            painel,
            text="Selecionar relatório",
            font=("Poppins", 15, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=18,
            pady=(15, 8)
        )

        self.seletor = ctk.CTkOptionMenu(
            painel,
            values=list(self.RELATORIOS.keys()),
            width=240,
            height=38,
            fg_color=COLORS["blue"],
            button_color=COLORS["blue"],
            button_hover_color=COLORS["blue_hover"],
            font=FONTS["body"],
            command=self._selecionar_relatorio
        )

        self.seletor.grid(
            row=1,
            column=0,
            sticky="w",
            padx=18,
            pady=(0, 15)
        )

        self.seletor.set("Estoque atual")

        ctk.CTkButton(
            painel,
            text="Gerar relatório",
            height=38,
            width=140,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_hover"],
            font=FONTS["button"],
            command=self.carregar_relatorio
        ).grid(
            row=1,
            column=1,
            padx=8,
            pady=(0, 15)
        )

        ctk.CTkButton(
            painel,
            text="Limpar",
            height=38,
            width=90,
            fg_color=COLORS["graphite"],
            hover_color=COLORS["charcoal"],
            font=FONTS["button"],
            command=self.limpar
        ).grid(
            row=1,
            column=2,
            padx=(8, 18),
            pady=(0, 15)
        )

    # =====================================
    # TABELA
    # =====================================

    def _criar_tabela(self, master):

        painel = ctk.CTkFrame(
            master,
            fg_color=COLORS["white"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )

        painel.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        painel.grid_columnconfigure(0, weight=1)
        painel.grid_rowconfigure(1, weight=1)

        topo = ctk.CTkFrame(
            painel,
            fg_color="transparent"
        )

        topo.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=16,
            pady=14
        )

        topo.grid_columnconfigure(0, weight=1)

        self.titulo_tabela = ctk.CTkLabel(
            topo,
            text="Estoque atual",
            font=("Poppins", 15, "bold"),
            text_color=COLORS["text"]
        )

        self.titulo_tabela.grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.total_registros = ctk.CTkLabel(
            topo,
            text="0 registros",
            font=FONTS["small"],
            text_color=COLORS["muted"]
        )

        self.total_registros.grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.tabela = ctk.CTkScrollableFrame(
            painel,
            fg_color=COLORS["white"],
            corner_radius=6
        )

        self.tabela.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

        self.feedback = ctk.CTkLabel(
            painel,
            text="",
            font=FONTS["small"],
            text_color=COLORS["muted"]
        )

        self.feedback.grid(
            row=2,
            column=0,
            sticky="w",
            padx=18,
            pady=(0, 12)
        )

    # =====================================
    # SELECIONAR RELATÓRIO
    # =====================================

    def _selecionar_relatorio(self, escolha):

        self.relatorio_atual = escolha

        self.carregar_relatorio()

    # =====================================
    # CARREGAR DADOS
    # =====================================

    def carregar_relatorio(self):

        self.relatorio_atual = self.seletor.get()

        if not self.on_carregar:

            self._mensagem(
                "Callback de relatórios não configurado.",
                erro=True
            )

            return

        tipo = self.RELATORIOS[
            self.relatorio_atual
        ]["tipo"]

        try:

            self.dados = list(
                self.on_carregar(tipo) or []
            )

            self._renderizar_tabela()

            self.titulo_tabela.configure(
                text=self.relatorio_atual
            )

            quantidade = len(self.dados)

            self.total_registros.configure(
                text=f"{quantidade} registros"
            )

            self._mensagem(
                "Relatório carregado com sucesso."
            )

        except Exception as exc:

            self.dados = []

            self._renderizar_tabela()

            self._mensagem(
                f"Erro ao gerar relatório: {exc}",
                erro=True
            )

    # =====================================
    # RENDERIZAR DADOS
    # =====================================

    def _renderizar_tabela(self):

        for widget in self.tabela.winfo_children():
            widget.destroy()

        configuracao = self.RELATORIOS[
            self.relatorio_atual
        ]

        colunas = configuracao["colunas"]

        for indice, (chave, titulo) in enumerate(colunas):

            self.tabela.grid_columnconfigure(
                indice,
                weight=1
            )

            ctk.CTkLabel(
                self.tabela,
                text=titulo,
                font=("Roboto", 12, "bold"),
                text_color=COLORS["text"],
                fg_color=COLORS["table_header"],
                corner_radius=4,
                anchor="w"
            ).grid(
                row=0,
                column=indice,
                sticky="ew",
                padx=2,
                pady=3,
                ipady=9
            )

        if not self.dados:

            ctk.CTkLabel(
                self.tabela,
                text="Nenhum registro encontrado para este relatório.",
                font=FONTS["body"],
                text_color=COLORS["muted"]
            ).grid(
                row=1,
                column=0,
                columnspan=len(colunas),
                pady=25
            )

            return

        for linha, registro in enumerate(
            self.dados,
            start=1
        ):

            for coluna, (chave, titulo) in enumerate(colunas):

                valor = registro.get(chave)

                if valor is None:
                    valor = "—"

                elif hasattr(valor, "strftime"):
                    valor = valor.strftime("%d/%m/%Y %H:%M")

                elif isinstance(valor, float):
                    valor = f"{valor:.2f}"

                ctk.CTkLabel(
                    self.tabela,
                    text=str(valor),
                    font=FONTS["body"],
                    text_color=COLORS["text"],
                    anchor="w"
                ).grid(
                    row=linha,
                    column=coluna,
                    sticky="ew",
                    padx=8,
                    pady=10
                )

    # =====================================
    # LIMPAR
    # =====================================

    def limpar(self):

        self.seletor.set("Estoque atual")
        self.relatorio_atual = "Estoque atual"
        self.dados = []

        self.titulo_tabela.configure(
            text="Estoque atual"
        )

        self.total_registros.configure(
            text="0 registros"
        )

        self._renderizar_tabela()

        self._mensagem("")

    # =====================================
    # MENSAGENS
    # =====================================

    def _mensagem(self, texto, erro=False):

        self.feedback.configure(
            text=texto,
            text_color=(
                COLORS["red"] if erro
                else COLORS["green"]
            )
        )
