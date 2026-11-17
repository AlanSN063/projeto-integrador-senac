
import customtkinter as ctk
from tkinter import messagebox

from .theme import COLORS, FONTS
from .components import PageHeader


class UsuariosView(ctk.CTkFrame):

    def __init__(
        self,
        master,
        usuarios=None,
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

        self.usuarios = list(usuarios or [])

        self.on_salvar = on_salvar or (lambda dados: False)
        self.on_atualizar = on_atualizar or (
            lambda usuario_id, dados: False
        )
        self.on_excluir = on_excluir or (
            lambda usuario_id: False
        )
        self.on_listar = on_listar

        self.usuario_selecionado = None
        self.entries = {}

        PageHeader(
            self,
            "Usuários",
            "Cadastre e gerencie os usuários do sistema",
            "users"
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

        self._renderizar_tabela(self.usuarios)

    # =====================================
    # FORMULÁRIO
    # =====================================

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

        formulario.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        ctk.CTkLabel(
            formulario,
            text="Dados do usuário",
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
            ("nome", "Nome completo *", 1, 0),
            ("login", "Login *", 1, 1),
            ("senha", "Senha *", 2, 0),
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
                height=36,
                font=FONTS["body"],
                border_color=COLORS["border"],
                placeholder_text=rotulo.replace(" *", ""),
                show="*" if chave == "senha" else ""
            )

            entrada.grid(
                row=1,
                column=0,
                sticky="ew"
            )

            self.entries[chave] = entrada

        # Cargo

        campo_cargo = ctk.CTkFrame(
            formulario,
            fg_color="transparent"
        )

        campo_cargo.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=14,
            pady=7
        )

        campo_cargo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            campo_cargo,
            text="Cargo *",
            font=("Roboto", 12, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        self.cargo = ctk.CTkOptionMenu(
            campo_cargo,
            values=["OPERADOR", "ADMINISTRADOR"],
            height=36,
            fg_color=COLORS["blue"],
            button_color=COLORS["blue"],
            button_hover_color=COLORS["blue_hover"],
            font=FONTS["body"]
        )

        self.cargo.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.cargo.set("OPERADOR")

        # Situação

        self.status = ctk.CTkOptionMenu(
            campo_cargo,
            values=["Ativo", "Inativo"],
            height=36,
            fg_color=COLORS["graphite"],
            font=FONTS["body"]
        )

        ctk.CTkLabel(
            campo_cargo,
            text="Situação",
            font=("Roboto", 12, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=(10, 5)
        )

        self.status.grid(
            row=3,
            column=0,
            sticky="ew"
        )

        self.status.set("Ativo")

        # Botões

        botoes = ctk.CTkFrame(
            formulario,
            fg_color="transparent"
        )

        botoes.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            padx=14,
            pady=(12, 8)
        )

        self.btn_salvar = ctk.CTkButton(
            botoes,
            text="Salvar usuário",
            height=36,
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
            botoes,
            text="Limpar",
            height=36,
            fg_color=COLORS["white"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            hover_color=COLORS["soft_gray"],
            command=self.limpar
        ).pack(
            side="left",
            padx=8
        )

        self.feedback = ctk.CTkLabel(
            formulario,
            text="",
            font=FONTS["small"],
            text_color=COLORS["muted"]
        )

        self.feedback.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(0, 12)
        )

    # =====================================
    # LISTAGEM
    # =====================================

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

        ctk.CTkLabel(
            topo,
            text="Usuários cadastrados",
            font=("Poppins", 15, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.busca = ctk.CTkEntry(
            topo,
            width=240,
            height=34,
            placeholder_text="Buscar por nome ou login...",
            font=FONTS["small"],
            border_color=COLORS["border"]
        )

        self.busca.grid(
            row=0,
            column=1,
            padx=(8, 6)
        )

        self.busca.bind(
            "<Return>",
            lambda event: self._filtrar()
        )

        ctk.CTkButton(
            topo,
            text="Buscar",
            width=75,
            height=34,
            fg_color=COLORS["blue"],
            command=self._filtrar
        ).grid(
            row=0,
            column=2,
            padx=(0, 6)
        )

        ctk.CTkButton(
            topo,
            text="Atualizar",
            width=90,
            height=34,
            fg_color=COLORS["graphite"],
            command=self.atualizar_lista
        ).grid(
            row=0,
            column=3
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

    # =====================================
    # RENDERIZAR TABELA
    # =====================================

    def _renderizar_tabela(self, usuarios):

        for widget in self.tabela.winfo_children():
            widget.destroy()

        titulos = [
            "Nome",
            "Login",
            "Cargo",
            "Situação",
            "Ações"
        ]

        larguras = [2, 1, 1, 1, 2]

        for coluna, (titulo, peso) in enumerate(
            zip(titulos, larguras)
        ):

            self.tabela.grid_columnconfigure(
                coluna,
                weight=peso
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
                column=coluna,
                sticky="ew",
                padx=2,
                pady=3,
                ipady=9
            )

        if not usuarios:

            ctk.CTkLabel(
                self.tabela,
                text="Nenhum usuário cadastrado.",
                font=FONTS["body"],
                text_color=COLORS["muted"]
            ).grid(
                row=1,
                column=0,
                columnspan=5,
                pady=24
            )

            return

        for indice, usuario in enumerate(
            usuarios,
            start=1
        ):

            valores = [
                usuario.get("nome", ""),
                usuario.get("login", ""),
                usuario.get("cargo", ""),
                "Ativo" if usuario.get("ativo") else "Inativo"
            ]

            for coluna, valor in enumerate(valores):

                ctk.CTkLabel(
                    self.tabela,
                    text=str(valor),
                    font=FONTS["body"],
                    text_color=COLORS["text"],
                    anchor="w"
                ).grid(
                    row=indice,
                    column=coluna,
                    sticky="ew",
                    padx=8,
                    pady=10
                )

            acoes = ctk.CTkFrame(
                self.tabela,
                fg_color="transparent"
            )

            acoes.grid(
                row=indice,
                column=4,
                padx=2,
                pady=5
            )

            ctk.CTkButton(
                acoes,
                text="Editar",
                width=60,
                height=28,
                fg_color=COLORS["graphite"],
                hover_color=COLORS["charcoal"],
                command=lambda item=usuario: self._selecionar_edicao(item)
            ).pack(
                side="left",
                padx=2
            )

            if usuario.get("ativo"):

                ctk.CTkButton(
                    acoes,
                    text="Desativar",
                    width=78,
                    height=28,
                    fg_color=COLORS["red"],
                    hover_color=COLORS["dark_red"],
                    command=lambda item=usuario: self._excluir(item)
                ).pack(
                    side="left",
                    padx=2
                )

    # =====================================
    # SALVAR / ATUALIZAR
    # =====================================

    def _salvar(self):

        dados = {
            chave: widget.get().strip()
            for chave, widget in self.entries.items()
        }

        if not dados["nome"] or not dados["login"]:
            self._mensagem(
                "Informe o nome e o login.",
                erro=True
            )
            return

        if self.usuario_selecionado is None and not dados["senha"]:
            self._mensagem(
                "Informe uma senha para o novo usuário.",
                erro=True
            )
            return

        if dados["senha"] and len(dados["senha"]) < 8:
            self._mensagem(
                "A senha deve possuir pelo menos 8 caracteres.",
                erro=True
            )
            return

        dados["cargo"] = self.cargo.get()
        dados["ativo"] = self.status.get() == "Ativo"

        try:

            if self.usuario_selecionado is None:

                sucesso = self.on_salvar(dados)
                mensagem = "Usuário cadastrado com sucesso."

            else:

                sucesso = self.on_atualizar(
                    self.usuario_selecionado,
                    dados
                )

                mensagem = "Usuário atualizado com sucesso."

            if sucesso:

                self._mensagem(mensagem)
                self.limpar()
                self.atualizar_lista()

            else:

                self._mensagem(
                    "Não foi possível salvar o usuário.",
                    erro=True
                )

        except Exception as exc:

            self._mensagem(str(exc), erro=True)

    # =====================================
    # EDITAR
    # =====================================

    def _selecionar_edicao(self, usuario):

        self.usuario_selecionado = usuario.get("id")

        for chave, widget in self.entries.items():

            widget.delete(0, "end")

            if chave == "senha":
                continue

            valor = usuario.get(chave)

            if valor is not None:
                widget.insert(0, str(valor))

        self.cargo.set(
            usuario.get("cargo") or "OPERADOR"
        )

        self.status.set(
            "Ativo" if usuario.get("ativo") else "Inativo"
        )

        self.btn_salvar.configure(
            text="Atualizar usuário"
        )

        self._mensagem(
            "Edite os dados. Deixe a senha vazia para mantê-la."
        )

    # =====================================
    # DESATIVAR
    # =====================================

    def _excluir(self, usuario):

        usuario_id = usuario.get("id")
        nome = usuario.get("nome", "este usuário")

        confirmar = messagebox.askyesno(
            "Confirmar desativação",
            f"Deseja realmente desativar '{nome}'?",
            parent=self
        )

        if not confirmar:
            return

        try:

            if self.on_excluir(usuario_id):

                self._mensagem(
                    "Usuário desativado com sucesso."
                )

                if self.usuario_selecionado == usuario_id:
                    self.limpar()

                self.atualizar_lista()

            else:

                self._mensagem(
                    "Não foi possível desativar o usuário.",
                    erro=True
                )

        except Exception as exc:

            self._mensagem(str(exc), erro=True)

    # =====================================
    # PESQUISAR
    # =====================================

    def _filtrar(self):

        termo = self.busca.get().strip().casefold()

        if not termo:
            self._renderizar_tabela(self.usuarios)
            return

        filtrados = [
            usuario
            for usuario in self.usuarios
            if termo in " ".join(
                str(usuario.get(campo) or "")
                for campo in ("nome", "login", "cargo")
            ).casefold()
        ]

        self._renderizar_tabela(filtrados)

    # =====================================
    # ATUALIZAR LISTAGEM
    # =====================================

    def atualizar_lista(self):

        if self.on_listar:

            try:

                self.usuarios = list(
                    self.on_listar() or []
                )

            except Exception as exc:

                self._mensagem(
                    f"Erro ao carregar usuários: {exc}",
                    erro=True
                )
                return

        self._filtrar()

    # =====================================
    # LIMPAR
    # =====================================

    def limpar(self):

        for widget in self.entries.values():
            widget.delete(0, "end")

        self.usuario_selecionado = None

        self.cargo.set("OPERADOR")
        self.status.set("Ativo")

        self.btn_salvar.configure(
            text="Salvar usuário"
        )

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
