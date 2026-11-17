import customtkinter as ctk
from tkinter import messagebox
from .theme import COLORS, FONTS
from .components import PageHeader


class ProdutosView(ctk.CTkFrame):
    def __init__(self, master, on_salvar=None, on_limpar=None, on_buscar=None, on_listar=None, categorias=None, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.on_salvar = on_salvar or (lambda dados: None)
        self.on_limpar = on_limpar
        self.on_buscar = on_buscar
        self.on_listar = on_listar
        self.produtos = []
        self.categorias = categorias or []
        self.entries = {}
        PageHeader(self, "Cadastro de Produtos", "Informe os dados do produto", "package").pack(fill="x", padx=22, pady=(22, 18))
        body = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=10, border_width=1, border_color=COLORS["border"])
        body.pack(fill="x", padx=22, pady=(0, 14))
        for col in range(3): body.grid_columnconfigure(col, weight=1)
        campos = [("nome", "Nome do produto *", 0, 0), ("codigo", "Código *", 0, 1), ("marca", "Marca", 0, 2), ("categoria", "Categoria *", 1, 0), ("preco_venda", "Preço de venda *", 1, 1), ("estoque_minimo", "Estoque mínimo *", 1, 2)]
        for chave, rotulo, linha, coluna in campos:
            frame = ctk.CTkFrame(body, fg_color="transparent")
            frame.grid(row=linha, column=coluna, sticky="ew", padx=14, pady=14)
            frame.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(frame, text=rotulo, font=("Roboto", 12, "bold"), text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", pady=(0, 5))
            if chave == "categoria":
                widget = ctk.CTkComboBox(frame, values=self.categorias or ["Cadastre uma categoria"], height=36, font=FONTS["body"])
                widget.set("")
            else:
                widget = ctk.CTkEntry(frame, height=36, font=FONTS["body"], border_color=COLORS["border"])
            widget.grid(row=1, column=0, sticky="ew")
            self.entries[chave] = widget
        botoes = ctk.CTkFrame(body, fg_color="transparent")
        botoes.grid(row=2, column=0, columnspan=3, sticky="w", padx=14, pady=18)
        ctk.CTkButton(botoes, text="Salvar produto", command=self._salvar, fg_color=COLORS["blue"], font=FONTS["button"]).pack(side="left", padx=(0, 8))
        ctk.CTkButton(botoes, text="Limpar", command=self.limpar, fg_color=COLORS["white"], text_color=COLORS["navy"], border_width=1, border_color=COLORS["navy"]).pack(side="left", padx=8)
        
        self.feedback = ctk.CTkLabel(body, text="", font=FONTS["small"], text_color=COLORS["muted"])
        self.feedback.grid(row=3, column=0, columnspan=3, sticky="w", padx=16, pady=8)
        self._criar_listagem()
        self.atualizar_lista()

    def _salvar(self):
        dados = {chave: widget.get().strip() for chave, widget in self.entries.items()}
        if any(not dados.get(c) for c in ("nome", "codigo", "categoria", "preco_venda", "estoque_minimo")):
            self.feedback.configure(text="Preencha todos os campos obrigatórios.", text_color=COLORS["red"]); return
        try:
            resultado = self.on_salvar(dados)
        except Exception as exc:
            self.feedback.configure(text=str(exc), text_color=COLORS["red"])
            return
        if resultado:
            self.feedback.configure(text="Produto cadastrado com sucesso.", text_color=COLORS["green"])
            self.limpar()
            self.atualizar_lista()

    def _criar_listagem(self):
        painel = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=10,
                              border_width=1, border_color=COLORS["border"])
        painel.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        painel.grid_columnconfigure(0, weight=1)
        painel.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(painel, text="Produtos cadastrados", font=("Poppins", 16, "bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))
        self.busca = ctk.CTkEntry(painel, placeholder_text="Pesquisar por nome ou código...",
                                  height=38, border_color=COLORS["border"])
        self.busca.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        self.busca.bind("<KeyRelease>", lambda event: self._filtrar())
        self.tabela = ctk.CTkScrollableFrame(painel, fg_color="transparent")
        self.tabela.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        for coluna, peso in enumerate((2, 1, 1, 2, 1, 1, 1, 1)):
            self.tabela.grid_columnconfigure(coluna, weight=peso)

    def atualizar_lista(self):
        if not self.on_listar:
            return
        try:
            self.produtos = list(self.on_listar() or [])
            self._filtrar()
        except Exception as exc:
            self.feedback.configure(text=f"Erro ao carregar produtos: {exc}", text_color=COLORS["red"])

    def _filtrar(self):
        termo = self.busca.get().strip().casefold()
        encontrados = [p for p in self.produtos if termo in
                       f"{p.get('nome') or ''} {p.get('codigo') or ''}".casefold()]
        self._renderizar_tabela(encontrados)

    def _renderizar_tabela(self, produtos):
        for widget in self.tabela.winfo_children():
            widget.destroy()
        titulos = ("Código", "Produto", "Marca", "Categoria", "Preço", "Estoque", "Mínimo", "Situação")
        for coluna, titulo in enumerate(titulos):
            ctk.CTkLabel(self.tabela, text=titulo, font=("Roboto", 12, "bold"),
                         text_color=COLORS["text"]).grid(row=0, column=coluna, sticky="w", padx=8, pady=10)
        if not produtos:
            ctk.CTkLabel(self.tabela, text="Nenhum produto encontrado.",
                         text_color=COLORS["muted"], font=FONTS["body"]).grid(
                             row=1, column=0, columnspan=8, pady=25)
            return
        for linha, produto in enumerate(produtos, 1):
            estoque = int(produto.get("estoque_atual") or 0)
            minimo = int(produto.get("estoque_minimo") or 0)
            situacao = "Inativo" if not produto.get("ativo", True) else (
                "Abaixo do mínimo" if estoque < minimo else "Regular")
            preco = produto.get("preco_venda") or 0
            valores = (produto.get("codigo") or "-", produto.get("nome") or "-",
                       produto.get("marca") or "-", produto.get("categoria") or "-",
                       f"R$ {preco:.2f}", estoque, minimo, situacao)
            for coluna, valor in enumerate(valores):
                cor = (COLORS["red"] if situacao != "Regular" else COLORS["green"]) if coluna == 7 else COLORS["text"]
                ctk.CTkLabel(self.tabela, text=str(valor), font=FONTS["small"],
                             text_color=cor, anchor="w").grid(
                                 row=linha, column=coluna, sticky="ew", padx=8, pady=8)

    def limpar(self):
        for widget in self.entries.values():
            if isinstance(widget, ctk.CTkComboBox): widget.set("")
            else: widget.delete(0, "end")
        self.feedback.configure(text="")
        if self.on_limpar: self.on_limpar()
