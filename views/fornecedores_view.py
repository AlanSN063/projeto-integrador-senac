
import customtkinter as ctk
from tkinter import messagebox

from .theme import COLORS, FONTS
from .components import PageHeader


class FornecedoresView(ctk.CTkFrame):
    """Cadastro, consulta, edição e exclusão de fornecedores."""

    def __init__(
        self,
        master,
        fornecedores=None,
        on_salvar=None,
        on_atualizar=None,
        on_excluir=None,
        on_listar=None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["background"],
            **kwargs
        )

        self.fornecedores = list(fornecedores or [])
        self.on_salvar = on_salvar or (lambda dados: False)
        self.on_atualizar = on_atualizar or (
            lambda fornecedor_id, dados: False
        )
        self.on_excluir = on_excluir or (
            lambda fornecedor_id: False
        )
        self.on_listar = on_listar

        self.fornecedor_selecionado = None
        self.entries = {}

        # CABEÇALHO
        PageHeader(
            self,
            "Fornecedores",
            "Cadastre e gerencie os fornecedores do estoque",
            "truck"
        ).pack(fill="x", padx=22, pady=(22, 16))

        # CONTEÚDO
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

        self._criar_formulario(conteudo)
        self._criar_listagem(conteudo)

        self._renderizar_tabela(self.fornecedores)

    # ==========================================
    # FORMULÁRIO
    # ==========================================

    def _criar_formulario(self, master):

        formulario = ctk.CTkFrame(
            master,
            fg_color=COLORS["white"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )

        formulario.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 14)
        )

        formulario.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            formulario,
            text="Dados do fornecedor",
            font=("Poppins", 16, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(16, 8)
        )

        campos = [
            ("razao_social", "Razão social *", 1, 0),
            ("cnpj", "CNPJ", 1, 1),
            ("telefone", "Telefone", 2, 0),
            ("email", "E-mail", 2, 1)
        ]

        for chave, rotulo, linha, coluna in campos:

            campo = ctk.CTkFrame(
                formulario,
                fg_color="transparent"
            )

            campo.grid(
                row=linha,
                column=coluna,
                sticky="ew",
                padx=14,
                pady=7
            )

            campo.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                campo,
                text=rotulo,
                font=("Roboto", 12, "bold"),
                text_color=COLORS["text"]
            ).grid(
                row=0,
                column=0,
                sticky="w",
                pady=(0, 5)
            )

            entrada = ctk.CTkEntry(
                campo,
                height=38,
                font=FONTS["body"],
                border_color=COLORS["border"]
            )

            entrada.grid(
                row=1,
                column=0,
                sticky="ew"
            )

            self.entries[chave] = entrada

        # ÁREA DE AÇÕES
        acoes = ctk.CTkFrame(
            formulario,
            fg_color="transparent"
        )

        acoes.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=14,
            pady=(12, 5)
        )

        self.btn_salvar = ctk.CTkButton(
            acoes,
            text="Salvar fornecedor",
            height=38,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_hover"],
            font=FONTS["button"],
            command=self._salvar
        )

        self.btn_salvar.pack(
            side="left",
            padx=(0, 8)
        )

        ctk.CTkButton(
            acoes,
            text="Limpar",
            height=38,
            fg_color=COLORS["muted"],
            hover_color=COLORS["navy"],
            font=FONTS["button"],
            command=self.limpar
        ).pack(side="left")

        self.feedback = ctk.CTkLabel(
            formulario,
            text="",
            font=FONTS["small"],
            text_color=COLORS["green"]
        )

        self.feedback.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(4, 12)
        )

    # ==========================================
    # LISTAGEM
    # ==========================================

    def _criar_listagem(self, master):

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
        painel.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            painel,
            text="Fornecedores cadastrados",
            font=("Poppins", 16, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(16, 10)
        )

        # PESQUISA
        self.busca = ctk.CTkEntry(
            painel,
            placeholder_text="Pesquisar fornecedor...",
            height=38,
            border_color=COLORS["border"]
        )

        self.busca.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 12)
        )

        self.busca.bind(
            "<KeyRelease>",
            lambda event: self._filtrar()
        )

        # ÁREA DA TABELA
        self.tabela = ctk.CTkScrollableFrame(
            painel,
            fg_color="transparent"
        )

        self.tabela.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

        self.tabela.grid_columnconfigure(0, weight=2)
        self.tabela.grid_columnconfigure(1, weight=1)
        self.tabela.grid_columnconfigure(2, weight=1)
        self.tabela.grid_columnconfigure(3, weight=2)
        self.tabela.grid_columnconfigure(4, weight=1)

    # ==========================================
    # RENDERIZAR TABELA
    # ==========================================

    def _renderizar_tabela(self, fornecedores):

        for widget in self.tabela.winfo_children():
            widget.destroy()

        colunas = [
            "Razão social",
            "CNPJ",
            "Telefone",
            "E-mail",
            "Ações"
        ]

        for coluna, titulo in enumerate(colunas):

            ctk.CTkLabel(
                self.tabela,
                text=titulo,
                font=("Roboto", 12, "bold"),
                text_color=COLORS["text"]
            ).grid(
                row=0,
                column=coluna,
                sticky="w",
                padx=6,
                pady=10
            )

        if not fornecedores:

            ctk.CTkLabel(
                self.tabela,
                text="Nenhum fornecedor encontrado.",
                text_color=COLORS["muted"],
                font=FONTS["body"]
            ).grid(
                row=1,
                column=0,
                columnspan=5,
                pady=25
            )

            return

        for linha, fornecedor in enumerate(fornecedores, start=1):

            valores = [
                fornecedor.get("razao_social", ""),
                fornecedor.get("cnpj") or "-",
                fornecedor.get("telefone") or "-",
                fornecedor.get("email") or "-"
            ]

            for coluna, valor in enumerate(valores):

                ctk.CTkLabel(
                    self.tabela,
                    text=str(valor),
                    font=FONTS["small"],
                    text_color=COLORS["text"],
                    anchor="w"
                ).grid(
                    row=linha,
                    column=coluna,
                    sticky="ew",
                    padx=6,
                    pady=8
                )

            acoes = ctk.CTkFrame(
                self.tabela,
                fg_color="transparent"
            )

            acoes.grid(
                row=linha,
                column=4,
                sticky="w",
                padx=3
            )

            ctk.CTkButton(
                acoes,
                text="Editar",
                width=55,
                height=28,
                fg_color=COLORS["blue"],
                hover_color=COLORS["blue_hover"],
                command=lambda item=fornecedor:
                    self._selecionar_edicao(item)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                acoes,
                text="Excluir",
                width=58,
                height=28,
                fg_color=COLORS["red"],
                hover_color=COLORS["dark_red"],
                command=lambda item=fornecedor:
                    self._excluir(item)
            ).pack(side="left", padx=2)

    # ==========================================
    # OBTER DADOS
    # ==========================================

    def _dados_formulario(self):

        return {
            chave: widget.get().strip()
            for chave, widget in self.entries.items()
        }

    # ==========================================
    # SALVAR / ATUALIZAR
    # ==========================================

    def _salvar(self):

        dados = self._dados_formulario()

        if not dados["razao_social"]:
            self._mensagem(
                "Informe a razão social do fornecedor.",
                erro=True
            )
            return

        for campo in ("cnpj", "telefone", "email"):
            dados[campo] = dados[campo] or None

        try:

            if self.fornecedor_selecionado is None:

                sucesso = self.on_salvar(dados)
                mensagem = "Fornecedor cadastrado com sucesso."

            else:

                sucesso = self.on_atualizar(
                    self.fornecedor_selecionado,
                    dados
                )

                mensagem = "Fornecedor atualizado com sucesso."

            if sucesso:

                self._mensagem(mensagem)
                self.limpar()
                self.atualizar_lista()

            else:

                self._mensagem(
                    "Não foi possível salvar o fornecedor.",
                    erro=True
                )

        except Exception as exc:

            self._mensagem(str(exc), erro=True)

    # ==========================================
    # EDITAR
    # ==========================================

    def _selecionar_edicao(self, fornecedor):

        self.fornecedor_selecionado = fornecedor.get("id")

        for chave, widget in self.entries.items():

            widget.delete(0, "end")

            valor = fornecedor.get(chave)

            if valor is not None:
                widget.insert(0, str(valor))

        self.btn_salvar.configure(
            text="Atualizar fornecedor"
        )

        self._mensagem(
            f"Editando fornecedor: {fornecedor.get('razao_social', '')}"
        )

    # ==========================================
    # EXCLUIR
    # ==========================================

    def _excluir(self, fornecedor):

        fornecedor_id = fornecedor.get("id")
        nome = fornecedor.get("razao_social", "este fornecedor")

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja realmente excluir '{nome}'?",
            parent=self
        )

        if not confirmar:
            return

        try:

            if self.on_excluir(fornecedor_id):

                self._mensagem(
                    "Fornecedor excluído com sucesso."
                )

                if self.fornecedor_selecionado == fornecedor_id:
                    self.limpar()

                self.atualizar_lista()

            else:

                self._mensagem(
                    "Não foi possível excluir o fornecedor.",
                    erro=True
                )

        except Exception as exc:

            self._mensagem(str(exc), erro=True)

    # ==========================================
    # PESQUISAR
    # ==========================================

    def _filtrar(self):

        termo = self.busca.get().strip().casefold()

        if not termo:
            self._renderizar_tabela(self.fornecedores)
            return

        filtrados = [
            fornecedor
            for fornecedor in self.fornecedores
            if termo in " ".join(
                str(fornecedor.get(campo) or "")
                for campo in (
                    "razao_social",
                    "cnpj",
                    "telefone",
                    "email"
                )
            ).casefold()
        ]

        self._renderizar_tabela(filtrados)

    # ==========================================
    # ATUALIZAR LISTAGEM
    # ==========================================

    def atualizar_lista(self):

        if self.on_listar:

            try:
                self.fornecedores = list(
                    self.on_listar() or []
                )

            except Exception as exc:

                self._mensagem(
                    f"Erro ao carregar fornecedores: {exc}",
                    erro=True
                )
                return

        self._filtrar()

    # ==========================================
    # LIMPAR
    # ==========================================

    def limpar(self):

        for widget in self.entries.values():
            widget.delete(0, "end")

        self.fornecedor_selecionado = None

        self.btn_salvar.configure(
            text="Salvar fornecedor"
        )

        self._mensagem("")

    # ==========================================
    # MENSAGENS
    # ==========================================

    def _mensagem(self, texto, erro=False):

        self.feedback.configure(
            text=texto,
            text_color=(
                COLORS["red"] if erro
                else COLORS["green"]
            )
        )
