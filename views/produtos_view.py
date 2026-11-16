import customtkinter as ctk
from tkinter import messagebox, simpledialog
from .theme import COLORS, FONTS
from .components import PageHeader


class ProdutosView(ctk.CTkFrame):
    def __init__(self, master, on_salvar=None, on_limpar=None, on_buscar=None, categorias=None, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.on_salvar = on_salvar or (lambda dados: None)
        self.on_limpar = on_limpar
        self.on_buscar = on_buscar
        self.categorias = categorias or []
        self.entries = {}
        PageHeader(self, "Cadastro de Produtos", "Informe os dados do produto", "package").pack(fill="x", padx=22, pady=(22, 18))
        body = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=10, border_width=1, border_color=COLORS["border"])
        body.pack(fill="both", expand=True, padx=22, pady=(0, 22))
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
        ctk.CTkButton(botoes, text="Consultar produtos", command=self._buscar, fg_color=COLORS["graphite"]).pack(side="left", padx=8)
        self.feedback = ctk.CTkLabel(body, text="", font=FONTS["small"], text_color=COLORS["muted"])
        self.feedback.grid(row=3, column=0, columnspan=3, sticky="w", padx=16, pady=8)

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

    def _buscar(self):
        termo = simpledialog.askstring("Consultar produtos", "Digite parte do nome ou código (deixe vazio para listar todos):", parent=self)
        if termo is not None and self.on_buscar: self.on_buscar(termo.strip() or None)

    def limpar(self):
        for widget in self.entries.values():
            if isinstance(widget, ctk.CTkComboBox): widget.set("")
            else: widget.delete(0, "end")
        self.feedback.configure(text="")
        if self.on_limpar: self.on_limpar()
