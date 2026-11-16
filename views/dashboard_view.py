import customtkinter as ctk
from .theme import COLORS, FONTS
from .components import PageHeader, MetricCard


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, resumo=None, movimentacoes=None, categorias_estoque=None, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        PageHeader(
            self, "Dashboard", "Visão geral do seu estoque", "home"
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=22, pady=(22, 18))

        resumo = resumo or {
            "Produtos": 300, "Fornecedores": 18,
            "Ordens de Serviço": 32, "Movimentações": 120
        }
        cards = [
            ("Produtos", resumo.get("Produtos", 0), "package", COLORS["blue"]),
            ("Fornecedores", resumo.get("Fornecedores", 0), "truck", COLORS["dark_red"]),
            ("Ordens de Serviço", resumo.get("Ordens de Serviço", 0), "wrench", COLORS["graphite"]),
            ("Movimentações", resumo.get("Movimentações", 0), "arrows", COLORS["charcoal"]),
        ]
        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 18))
        for i, (title, value, icon, color) in enumerate(cards):
            metrics.grid_columnconfigure(i, weight=1)
            MetricCard(metrics, title, value, icon, color).grid(
                row=0, column=i, padx=5, sticky="nsew"
            )

        recent = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=10,
            border_width=1, border_color=COLORS["border"]
        )
        recent.grid(row=2, column=0, sticky="nsew", padx=(22, 9), pady=(0, 22))
        recent.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            recent, text="Movimentações Recentes", font=("Poppins", 15, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=16, pady=14)

        rows = movimentacoes if movimentacoes is not None else []
        header = ctk.CTkFrame(recent, fg_color=COLORS["table_header"], corner_radius=5)
        header.pack(fill="x", padx=12)
        for col, title in enumerate(("Data", "Tipo", "Produto", "Qtd.")):
            header.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(header, text=title, font=("Roboto", 11, "bold"),
                         text_color=COLORS["text"]).grid(row=0, column=col, padx=5, pady=9)
        for row in rows:
            line = ctk.CTkFrame(recent, fg_color="transparent")
            line.pack(fill="x", padx=12)
            for col, value in enumerate(row):
                line.grid_columnconfigure(col, weight=1)
                color = COLORS["green"] if value == "Entrada" or str(value).startswith("+") else COLORS["red"] if value == "Saída" or str(value).startswith("-") else COLORS["text"]
                ctk.CTkLabel(
                    line, text=str(value), font=FONTS["small"],
                    text_color=color
                ).grid(row=0, column=col, padx=5, pady=9, sticky="w")

        category = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=10,
            border_width=1, border_color=COLORS["border"]
        )
        category.grid(row=2, column=1, sticky="nsew", padx=(9, 22), pady=(0, 22))
        ctk.CTkLabel(
            category, text="Estoque por Categoria", font=("Poppins", 15, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=16, pady=14)
        cores = [COLORS["blue"], COLORS["dark_red"], COLORS["graphite"], COLORS["charcoal"]]
        for indice, (name, saldo, proporcao) in enumerate(categorias_estoque or []):
            color = cores[indice % len(cores)]
            line = ctk.CTkFrame(category, fg_color="transparent")
            line.pack(fill="x", padx=18, pady=10)
            ctk.CTkLabel(line, text="●", text_color=color, font=("Roboto", 17)).pack(side="left")
            ctk.CTkLabel(line, text=name, text_color=COLORS["text"],
                         font=FONTS["body"]).pack(side="left", padx=8)
            ctk.CTkLabel(line, text=f"{saldo} un.", text_color=COLORS["text"],
                         font=("Roboto", 12, "bold")).pack(side="right")
            bar = ctk.CTkProgressBar(category, height=8, corner_radius=4,
                                     progress_color=color, fg_color=COLORS["border"])
            bar.pack(fill="x", padx=(42, 22), pady=(0, 6))
            bar.set(proporcao)
        if not categorias_estoque:
            ctk.CTkLabel(category, text="Ainda não há saldo de estoque registrado.",
                         text_color=COLORS["muted"], font=FONTS["body"]).pack(padx=18, pady=18)
