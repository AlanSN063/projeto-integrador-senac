import customtkinter as ctk
from .theme import COLORS, FONTS
from .components import PageHeader


class PlaceholderView(ctk.CTkFrame):
    def __init__(self, master, title, description="Área preparada para integração com o Controller."):
        super().__init__(master, fg_color=COLORS["background"])
        PageHeader(self, title, description, "▤").pack(
            fill="x", padx=22, pady=(22, 18)
        )
        panel = ctk.CTkFrame(
            self, fg_color=COLORS["white"], corner_radius=10,
            border_width=1, border_color=COLORS["border"]
        )
        panel.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        ctk.CTkLabel(
            panel, text=f"Tela de {title}",
            font=("Poppins", 20, "bold"), text_color=COLORS["text"]
        ).pack(pady=(50, 8))
        ctk.CTkLabel(
            panel, text=description, font=FONTS["body"],
            text_color=COLORS["muted"]
        ).pack(pady=8)
