import customtkinter as ctk
from .theme import COLORS, FONTS
from .icons import get_icon


class LoginView(ctk.CTkFrame):
    """Tela de login. on_login(usuario, senha) é fornecido pelo Controller."""

    def __init__(self, master, on_login, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.on_login = on_login
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Painel institucional
        left = ctk.CTkFrame(self, fg_color=COLORS["navy"], corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(left, text="", image=get_icon("package", COLORS["red"], 80),
                     text_color=COLORS["white"]).grid(row=0, column=0, pady=(40, 0))
        ctk.CTkLabel(
            left, text="Controle de\nEstoque",
            font=("Poppins", 30, "bold"), text_color=COLORS["white"],
            justify="center"
        ).grid(row=1, column=0, padx=24)
        ctk.CTkLabel(
            left, text="Organização, controle e eficiência\npara o seu negócio.",
            font=FONTS["body"], text_color="#E6E6E6", justify="center"
        ).grid(row=2, column=0, pady=(0, 55))

        # Cartão de acesso
        right = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure((0, 2), weight=1)
        card = ctk.CTkFrame(
            right, fg_color=COLORS["white"], corner_radius=14,
            border_width=1, border_color=COLORS["border"]
        )
        card.grid(row=1, column=0, padx=34, pady=30, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="  Acesso ao Sistema", image=get_icon("lock", COLORS["red"], 23), compound="left", font=("Poppins", 20, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=28, pady=(34, 5))
        ctk.CTkLabel(
            card, text="Faça login para continuar", font=FONTS["body"],
            text_color=COLORS["muted"]
        ).pack(anchor="w", padx=28, pady=(0, 24))

        self.user_entry = ctk.CTkEntry(
            card, height=42, placeholder_text="Usuário",
            font=FONTS["body"], border_color=COLORS["border"]
        )
        self.user_entry.pack(fill="x", padx=28, pady=7)

        self.password_entry = ctk.CTkEntry(
            card, height=42, placeholder_text="Senha", show="●",
            font=FONTS["body"], border_color=COLORS["border"]
        )
        self.password_entry.pack(fill="x", padx=28, pady=7)
        self.password_entry.bind("<Return>", lambda _event: self._submit())

        self.message = ctk.CTkLabel(
            card, text="", font=FONTS["small"], text_color=COLORS["red"]
        )
        self.message.pack(padx=28, pady=(4, 0), anchor="w")

        ctk.CTkButton(
            card, text="Entrar", height=43, corner_radius=8,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
            font=FONTS["button"], command=self._submit
        ).pack(fill="x", padx=28, pady=(14, 18))

        ctk.CTkLabel(
            card, text="Controle de Estoque • Projeto Integrador",
            font=FONTS["small"], text_color=COLORS["muted"]
        ).pack(pady=(12, 25))

    def _submit(self):
        usuario = self.user_entry.get().strip()
        senha = self.password_entry.get()
        if not usuario or not senha:
            self.message.configure(text="Informe o usuário e a senha.")
            return
        self.message.configure(text="")
        self.on_login(usuario, senha)

    def show_error(self, mensagem):
        self.message.configure(text=mensagem)
