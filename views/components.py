import customtkinter as ctk
from .theme import COLORS, FONTS
from .icons import get_icon


class PageHeader(ctk.CTkFrame):
    def __init__(self, master, title, subtitle="", icon=""):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="", image=get_icon(icon or "home", COLORS["blue"], 28)
        ).grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky="w")

        ctk.CTkLabel(
            self, text=title, font=FONTS["title"], text_color=COLORS["text"]
        ).grid(row=0, column=1, sticky="sw")

        if subtitle:
            ctk.CTkLabel(
                self, text=subtitle, font=FONTS["body"],
                text_color=COLORS["muted"]
            ).grid(row=1, column=1, sticky="nw")


class MetricCard(ctk.CTkFrame):
    def __init__(self, master, title, value, icon, color):
        super().__init__(
            master, fg_color=color, corner_radius=12,
            border_width=0
        )
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self, text=f"  {title}", image=get_icon(icon, COLORS["white"], 18),
            compound="left", font=("Roboto", 13, "bold"),
            text_color=COLORS["white"], anchor="w"
        ).grid(row=0, column=0, padx=16, pady=(15, 4), sticky="ew")
        ctk.CTkLabel(
            self, text=str(value), font=FONTS["metric"],
            text_color=COLORS["white"], anchor="w"
        ).grid(row=1, column=0, padx=16, pady=(0, 14), sticky="ew")


class Sidebar(ctk.CTkFrame):
    ITEMS = [
        ("Início", "home"), ("Produtos", "package"),
        ("Fornecedores", "truck"), ("Categorias", "tags"),
        ("Ordens de serviço", "wrench"), ("Movimentações", "arrows"),
        ("Usuários", "users"), ("Relatórios", "chart"),
        ("Configurações", "settings"),
    ]

    def __init__(self, master, on_navigate, on_logout=None):
        super().__init__(master, width=205, corner_radius=0, fg_color=COLORS["navy"])
        self.grid_propagate(False)
        self.on_navigate = on_navigate
        self.buttons = {}
        self._images = {}

        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", padx=16, pady=(20, 22))
        ctk.CTkLabel(
            brand, text="", image=get_icon("boxes", COLORS["white"], 32),
            text_color=COLORS["white"]
        ).pack(side="left", padx=(0, 9))
        ctk.CTkLabel(
            brand, text="Controle de\nEstoque",
            font=("Poppins", 15, "bold"), text_color=COLORS["white"],
            justify="left"
        ).pack(side="left")

        for label, icon in self.ITEMS:
            self._images[label] = get_icon(icon, COLORS["white"], 19)
            button = ctk.CTkButton(
                self, text=f"  {label}", image=self._images[label], compound="left", anchor="w", height=42,
                corner_radius=8, fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["white"], font=FONTS["body"],
                command=lambda page=label: self.on_navigate(page)
            )
            button.pack(fill="x", padx=10, pady=3)
            self.buttons[label] = button

        ctk.CTkFrame(self, fg_color="transparent").pack(expand=True, fill="both")
        ctk.CTkButton(
            self, text="  Sair", image=get_icon("logout", COLORS["white"], 19),
            compound="left", anchor="w", height=42,
            fg_color="transparent", hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["white"], font=FONTS["body"],
            command=on_logout or (lambda: None)
        ).pack(fill="x", padx=10, pady=(8, 18))

    def set_active(self, label):
        for name, button in self.buttons.items():
            button.configure(
                fg_color=COLORS["blue"] if name == label else "transparent"
            )
