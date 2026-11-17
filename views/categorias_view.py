
import customtkinter as ctk
from tkinter import messagebox

from .theme import COLORS
from .components import PageHeader


class CategoriasView(ctk.CTkFrame):
    """Tela de cadastro, consulta, edição e exclusão de categorias."""

    def __init__(
        self,
        master,
        categorias=None,
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

        self.categorias = list(categorias or [])
        self.on_salvar = on_salvar or (lambda dados: False)
        self.on_atualizar = on_atualizar or (
            lambda categoria_id, dados: False
        )
        self.on_excluir = on_excluir or (
            lambda categoria_id: False
        )
        self.on_listar = on_listar

        self.categoria_selecionada = None
        self.entries = {}

        PageHeader(
            self,
            "Categorias",
            "Cadastre e organize as categorias dos produtos",
            "tags"
        ).pack(fill="x", padx=22, pady=(22, 16))

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
        self._renderizar_lista(self.categorias)

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

        formulario.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            formulario,
            text="Dados da categoria",
            font=("Poppins", 16, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(16, 8)
        )

        campos = [
            ("nome", "Nome da categoria *"),
            ("descricao", "Descrição")
        ]

        for linha, (chave, rotulo) in enumerate(campos, start=1):
            campo = ctk.CTkFrame(
                formulario,
                fg_color="transparent"
            )

            campo.grid(
                row=linha,
                column=0,
                sticky="ew",
                padx=18,
                pady=6
            )

            campo.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                campo,
                text=rotulo,
                font=("Roboto", 12, "bold"),
                text_color=COLORS["text"]
            ).pack(anchor="w", pady=(0, 5))

            entrada = ctk.CTkEntry(
                campo,
                height=38,
                font=("Roboto", 13),
                placeholder_text=f"Digite {rotulo.lower()}"
            )

            entrada.pack(fill="x")
            self.entries[chave] = entrada

        acoes = ctk.CTkFrame(
            formulario,
            fg_color="transparent"
        )

        acoes.grid(
            row=3,
            column=0,
            sticky="w",
            padx=18,
            pady=(12, 8)
        )

        self.btn_salvar = ctk.CTkButton(
            acoes,
            text="Salvar categoria",
            width=160,
            height=36,
            fg_color="#1769D2",
            hover_color="#1255AA",
            command=self._salvar
        )
        self.btn_salvar.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            acoes,
            text="Limpar",
            width=100,
            height=36,
            fg_color="#64748B",
            hover_color="#475569",
            command=self.limpar
        ).pack(side="left")

        self.feedback = ctk.CTkLabel(
            formulario,
            text="",
            font=("Roboto", 12),
            text_color=COLORS["text"]
        )

        self.feedback.grid(
            row=4,
            column=0,
            sticky="w",
            padx=18,
            pady=(0, 12)
        )

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
            text="Categorias cadastradas",
            font=("Poppins", 16, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(16, 10)
        )

        busca_frame = ctk.CTkFrame(
            painel,
            fg_color="transparent"
        )

        busca_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 12)
        )

        busca_frame.grid_columnconfigure(0, weight=1)

        self.busca = ctk.CTkEntry(
            busca_frame,
            height=36,
            placeholder_text="Pesquisar categoria pelo nome ou descrição..."
        )

        self.busca.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        self.busca.bind(
            "<KeyRelease>",
            lambda event: self._filtrar()
        )

        ctk.CTkButton(
            busca_frame,
            text="Pesquisar",
            width=100,
            height=36,
            command=self._filtrar
        ).grid(row=0, column=1)

        self.lista = ctk.CTkScrollableFrame(
            painel,
            fg_color="transparent"
        )

        self.lista.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(0, 18)
        )

        self.lista.grid_columnconfigure(0, weight=1)

    def _renderizar_lista(self, categorias):
        for widget in self.lista.winfo_children():
            widget.destroy()

        if not categorias:
            ctk.CTkLabel(
                self.lista,
                text="Nenhuma categoria cadastrada.",
                font=("Roboto", 13),
                text_color="#64748B"
            ).grid(
                row=0,
                column=0,
                pady=25
            )
            return

        for linha, categoria in enumerate(categorias):
            card = ctk.CTkFrame(
                self.lista,
                fg_color="#F4F7FB",
                corner_radius=8
            )

            card.grid(
                row=linha,
                column=0,
                sticky="ew",
                pady=5
            )

            card.grid_columnconfigure(0, weight=1)

            informacoes = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )

            informacoes.grid(
                row=0,
                column=0,
                sticky="ew",
                padx=12,
                pady=10
            )

            nome = categoria.get("nome", "")
            descricao = categoria.get("descricao") or "Sem descrição"

            ctk.CTkLabel(
                informacoes,
                text=nome,
                font=("Roboto", 14, "bold"),
                text_color=COLORS["text"]
            ).pack(anchor="w")

            ctk.CTkLabel(
                informacoes,
                text=descricao,
                font=("Roboto", 12),
                text_color="#64748B"
            ).pack(anchor="w", pady=(3, 0))

            acoes = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )

            acoes.grid(
                row=0,
                column=1,
                padx=10,
                pady=10
            )

            ctk.CTkButton(
                acoes,
                text="Editar",
                width=65,
                height=30,
                command=lambda item=categoria: self._selecionar_edicao(item)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                acoes,
                text="Excluir",
                width=65,
                height=30,
                fg_color="#DC2626",
                hover_color="#991B1B",
                command=lambda item=categoria: self._excluir(item)
            ).pack(side="left", padx=3)

    def _dados_formulario(self):
        return {
            chave: widget.get().strip()
            for chave, widget in self.entries.items()
        }

    def _salvar(self):
        dados = self._dados_formulario()

        if not dados["nome"]:
            self._mensagem(
                "Informe o nome da categoria.",
                erro=True
            )
            return

        dados["descricao"] = dados["descricao"] or None

        try:
            if self.categoria_selecionada is None:
                sucesso = self.on_salvar(dados)
                mensagem = "Categoria cadastrada com sucesso."
            else:
                sucesso = self.on_atualizar(
                    self.categoria_selecionada,
                    dados
                )
                mensagem = "Categoria atualizada com sucesso."

            if sucesso:
                self.limpar()
                self.atualizar_lista()
                self._mensagem(mensagem)
            else:
                self._mensagem(
                    "Não foi possível salvar a categoria.",
                    erro=True
                )

        except Exception as exc:
            self._mensagem(str(exc), erro=True)

    def _selecionar_edicao(self, categoria):
        self.categoria_selecionada = categoria.get("id")

        for chave, widget in self.entries.items():
            widget.delete(0, "end")

            valor = categoria.get(chave)

            if valor is not None:
                widget.insert(0, str(valor))

        self.btn_salvar.configure(
            text="Atualizar categoria"
        )

        self._mensagem(
            f"Editando categoria: {categoria.get('nome', '')}"
        )

    def _excluir(self, categoria):
        categoria_id = categoria.get("id")
        nome = categoria.get("nome", "esta categoria")

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja realmente excluir a categoria '{nome}'?",
            parent=self
        )

        if not confirmar:
            return

        try:
            if self.on_excluir(categoria_id):
                if self.categoria_selecionada == categoria_id:
                    self.limpar()

                self.atualizar_lista()
                self._mensagem("Categoria excluída com sucesso.")

            else:
                self._mensagem(
                    "Não foi possível excluir a categoria.",
                    erro=True
                )

        except Exception as exc:
            self._mensagem(str(exc), erro=True)

    def _filtrar(self):
        termo = self.busca.get().strip().casefold()

        if not termo:
            self._renderizar_lista(self.categorias)
            return

        filtradas = [
            categoria
            for categoria in self.categorias
            if termo in (
                str(categoria.get("nome") or "") + " " +
                str(categoria.get("descricao") or "")
            ).casefold()
        ]

        self._renderizar_lista(filtradas)

    def atualizar_lista(self):
        if self.on_listar:
            try:
                self.categorias = list(self.on_listar() or [])
            except Exception as exc:
                self._mensagem(
                    f"Erro ao carregar categorias: {exc}",
                    erro=True
                )
                return

        self._filtrar()

    def limpar(self):
        for widget in self.entries.values():
            widget.delete(0, "end")

        self.categoria_selecionada = None

        self.btn_salvar.configure(
            text="Salvar categoria"
        )

        self._mensagem("")

    def _mensagem(self, texto, erro=False):
        self.feedback.configure(
            text=texto,
            text_color="#DC2626" if erro else "#16A34A"
        )
