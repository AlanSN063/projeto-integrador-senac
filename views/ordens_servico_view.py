import customtkinter as ctk
from .theme import COLORS, FONTS
from .components import PageHeader
from .icons import get_icon


class OrdensServicoView(ctk.CTkFrame):
    """Lista de OS; callbacks recebem o identificador da ordem."""

    def __init__(self, master, ordens=None, on_nova_ordem=None,
                 on_visualizar=None, on_editar=None, on_excluir=None, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.on_nova_ordem = on_nova_ordem or (lambda: None)
        self.on_visualizar = on_visualizar or (lambda item_id: None)
        self.on_editar = on_editar or (lambda item_id: None)
        self.on_excluir = on_excluir or (lambda item_id: None)
        self.ordens = ordens or [
            ("OS-0001", "João Silva", "Toyota Corolla", "06/11/2026", "Aberta"),
            ("OS-0002", "Maria Souza", "Honda Civic", "05/11/2026", "Em Andamento"),
            ("OS-0003", "Carlos Lima", "Fiat Uno", "04/11/2026", "Concluída"),
        ]

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(22, 16))
        PageHeader(
            top, "Ordens de Serviço", "Gerencie as ordens de serviço", "wrench"
        ).pack(side="left")
        ctk.CTkButton(
            top, text="+  Nova Ordem", height=38,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
            font=FONTS["button"], command=self.on_nova_ordem
        ).pack(side="right", anchor="center")

        search = ctk.CTkFrame(self, fg_color="transparent")
        search.pack(fill="x", padx=22, pady=(0, 12))
        self.search_entry = ctk.CTkEntry(
            search, placeholder_text="Buscar por cliente, veículo ou status...",
            height=38, font=FONTS["body"], border_color=COLORS["border"]
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            search, text="", image=get_icon("search", COLORS["white"], 18), width=42, height=38,
            fg_color=COLORS["blue"], command=self._filter
        ).pack(side="left", padx=(8, 0))

        self.table = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=10,
            border_width=1, border_color=COLORS["border"]
        )
        self.table.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        self._render_rows(self.ordens)

    def _render_rows(self, rows):
        for child in self.table.winfo_children():
            child.destroy()
        headers = ["Nº OS", "Cliente", "Veículo", "Data", "Status", "Ações"]
        for col, title in enumerate(headers):
            self.table.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(
                self.table, text=title, font=("Roboto", 12, "bold"),
                text_color=COLORS["text"], fg_color=COLORS["table_header"],
                corner_radius=3
            ).grid(row=0, column=col, sticky="ew", padx=2, pady=3, ipady=10)

        for row_index, item in enumerate(rows, start=1):
            item_id, cliente, veiculo, data, status = item
            values = [item_id, cliente, veiculo, data, status]
            for col, value in enumerate(values):
                color = {
                    "Aberta": COLORS["blue"],
                    "Em Andamento": COLORS["orange"],
                    "Concluída": COLORS["green"]
                }.get(value, COLORS["text"])
                ctk.CTkLabel(
                    self.table, text=str(value), font=FONTS["body"],
                    text_color=color
                ).grid(row=row_index, column=col, sticky="w", padx=10, pady=12)

            actions = ctk.CTkFrame(self.table, fg_color="transparent")
            actions.grid(row=row_index, column=5, padx=3, pady=5)
            ctk.CTkButton(
                actions, text="", image=get_icon("eye", COLORS["red"], 17), width=30, height=28,
                fg_color=COLORS["soft_gray"], text_color=COLORS["blue"],
                hover_color=COLORS["border"],
                command=lambda key=item_id: self.on_visualizar(key)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                actions, text="", image=get_icon("edit", COLORS["red"], 17), width=30, height=28,
                fg_color=COLORS["soft_gray"], text_color=COLORS["blue"],
                hover_color=COLORS["border"],
                command=lambda key=item_id: self.on_editar(key)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                actions, text="", image=get_icon("trash", COLORS["red"], 17), width=30, height=28,
                fg_color=COLORS["soft_red"], text_color=COLORS["red"],
                hover_color="#FFCCCC",
                command=lambda key=item_id: self.on_excluir(key)
            ).pack(side="left", padx=2)

    def _filter(self):
        term = self.search_entry.get().strip().lower()
        filtered = [
            row for row in self.ordens
            if term in " ".join(map(str, row)).lower()
        ] if term else self.ordens
        self._render_rows(filtered)

    def atualizar(self, ordens):
        self.ordens = ordens
        self._render_rows(ordens)
