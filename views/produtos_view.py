import customtkinter as ctk
from tkinter import filedialog
from .theme import COLORS, FONTS
from .components import PageHeader


class ProdutosView(ctk.CTkFrame):
    """Formulário de produto. on_salvar recebe um dicionário com os campos."""

    def __init__(self, master, on_salvar=None, on_limpar=None,
                 on_buscar=None, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.on_salvar = on_salvar or (lambda dados: None)
        self.on_limpar = on_limpar
        self.on_buscar = on_buscar
        self.image_path = None
        self.entries = {}

        PageHeader(
            self, "Cadastro de Produtos", "Informe os dados do produto", "▣"
        ).pack(fill="x", padx=22, pady=(22, 18))

        body = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=10,
            border_width=1, border_color=COLORS["border"]
        )
        body.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=1)
        body.grid_columnconfigure(3, weight=1)

        fields = [
            ("nome", "Nome do Produto *", 0, 0),
            ("categoria", "Categoria *", 0, 1),
            ("fornecedor", "Fornecedor *", 0, 2),
            ("codigo_barras", "Código de Barras", 1, 0),
            ("preco_venda", "Preço de Venda *", 1, 1),
            ("estoque_minimo", "Estoque Mínimo *", 1, 2),
        ]
        for key, label, row, col in fields:
            self._add_field(body, key, label, row, col)

        desc_label = ctk.CTkLabel(
            body, text="Descrição", font=("Roboto", 12, "bold"),
            text_color=COLORS["text"]
        )
        desc_label.grid(row=2, column=0, columnspan=3, sticky="w",
                        padx=14, pady=(14, 4))
        self.description = ctk.CTkTextbox(
            body, height=95, font=FONTS["body"],
            border_width=1, border_color=COLORS["border"],
            fg_color=COLORS["white"], text_color=COLORS["text"]
        )
        self.description.grid(row=3, column=0, columnspan=3, sticky="ew",
                              padx=14, pady=(0, 12))

        image_panel = ctk.CTkFrame(body, fg_color=COLORS["background"], corner_radius=8)
        image_panel.grid(row=0, column=3, rowspan=4, padx=14, pady=14, sticky="nsew")
        self.image_label = ctk.CTkLabel(
            image_panel, text="Imagem do\nproduto", width=125, height=135,
            fg_color=COLORS["table_header"], corner_radius=8,
            text_color=COLORS["muted"], font=FONTS["body"]
        )
        self.image_label.pack(padx=10, pady=(18, 12), fill="both", expand=True)
        ctk.CTkButton(
            image_panel, text="▣  Selecionar Imagem", height=34,
            fg_color=COLORS["blue"], font=("Roboto", 11, "bold"),
            command=self._select_image
        ).pack(fill="x", padx=10, pady=(0, 14))

        actions = ctk.CTkFrame(body, fg_color="transparent")
        actions.grid(row=4, column=0, columnspan=4, sticky="w", padx=14, pady=14)
        ctk.CTkButton(
            actions, text="✓  Salvar", width=125, height=40,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
            font=FONTS["button"], command=self._save
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            actions, text="↻  Limpar", width=110, height=40,
            fg_color=COLORS["white"], border_width=1,
            border_color=COLORS["navy"], text_color=COLORS["navy"],
            hover_color=COLORS["table_header"], font=FONTS["button"],
            command=self.clear
        ).pack(side="left")

        self.feedback = ctk.CTkLabel(
            body, text="", text_color=COLORS["green"], font=FONTS["small"]
        )
        self.feedback.grid(row=5, column=0, columnspan=4, sticky="w",
                           padx=16, pady=(0, 8))

    def _add_field(self, parent, key, label, row, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=14, pady=(14, 2))
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            frame, text=label, font=("Roboto", 12, "bold"),
            text_color=COLORS["text"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        if key == "categoria":
            widget = ctk.CTkComboBox(
                frame, values=["Peças Automotivas", "Acessórios",
                               "Produtos Químicos", "Outros"],
                height=36, font=FONTS["body"], border_color=COLORS["border"]
            )
            widget.set("")
        elif key == "fornecedor":
            widget = ctk.CTkComboBox(
                frame, values=["Auto Peças Ltda", "Fornecedor Exemplo"],
                height=36, font=FONTS["body"], border_color=COLORS["border"]
            )
            widget.set("")
        else:
            widget = ctk.CTkEntry(
                frame, height=36, font=FONTS["body"],
                border_color=COLORS["border"]
            )
        widget.grid(row=1, column=0, sticky="ew")
        self.entries[key] = widget

    def _select_image(self):
        path = filedialog.askopenfilename(
            title="Selecionar imagem do produto",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.webp"), ("Todos", "*.*")]
        )
        if path:
            self.image_path = path
            try:
                from PIL import Image
                image = ctk.CTkImage(
                    light_image=Image.open(path), dark_image=Image.open(path),
                    size=(130, 135)
                )
                self.image_label.configure(image=image, text="")
                self.image_label.image = image
            except Exception:
                self.image_label.configure(text="Imagem selecionada")

    def _save(self):
        dados = {key: widget.get().strip() for key, widget in self.entries.items()}
        dados["descricao"] = self.description.get("1.0", "end").strip()
        dados["imagem"] = self.image_path
        obrigatorios = ("nome", "categoria", "fornecedor", "preco_venda", "estoque_minimo")
        if any(not dados.get(campo) for campo in obrigatorios):
            self.feedback.configure(
                text="Preencha os campos obrigatórios (*).",
                text_color=COLORS["red"]
            )
            return
        self.on_salvar(dados)
        self.feedback.configure(text="Dados enviados para o Controller.", text_color=COLORS["green"])

    def clear(self):
        for widget in self.entries.values():
            if isinstance(widget, ctk.CTkComboBox):
                widget.set("")
            else:
                widget.delete(0, "end")
        self.description.delete("1.0", "end")
        self.image_path = None
        self.image_label.configure(image=None, text="Imagem do\nproduto")
        self.feedback.configure(text="")
        if self.on_limpar:
            self.on_limpar()
