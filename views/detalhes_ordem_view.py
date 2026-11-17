"""Janela de detalhes de ordem de serviço utilizando CustomTkinter."""
import customtkinter as ctk
from .theme import COLORS


class DetalhesOrdemView(ctk.CTkToplevel):
    STATUS = {
        "ABERTA": ("Aberta", "#B91C1C", "#FEE2E2"),
        "EM_EXECUCAO": ("Em andamento", "#9A5700", "#FFF1D6"),
        "CONCLUIDA": ("Concluída", "#166534", "#DCFCE7"),
        "CANCELADA": ("Cancelada", "#555555", "#E9E9E9"),
    }

    def __init__(self, master, registro):
        super().__init__(master)
        self.title(f"Ordem de serviço • {registro.get('numero', '')}")
        self.geometry("760x570")
        self.minsize(590, 470)
        self.configure(fg_color=COLORS["background"])
        self.transient(master)

        # Centralizar em relação à janela principal, respeitando a área disponível.
        self.update_idletasks()
        x = master.winfo_rootx() + max(0, (master.winfo_width() - 760) // 2)
        y = master.winfo_rooty() + max(0, (master.winfo_height() - 570) // 2)
        self.geometry(f"760x570+{x}+{y}")

        cabecalho = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=0)
        cabecalho.pack(fill="x")
        ctk.CTkLabel(cabecalho, text="DETALHES DA ORDEM DE SERVIÇO",
                     text_color=COLORS["muted"], font=("Roboto", 12, "bold"),
                     anchor="w").pack(fill="x", padx=28, pady=(22, 3))
        linha = ctk.CTkFrame(cabecalho, fg_color="transparent")
        linha.pack(fill="x", padx=28, pady=(0, 22))
        ctk.CTkLabel(linha, text=str(registro.get("numero") or "—"),
                     font=("Poppins", 25, "bold"), text_color=COLORS["text"]
                     ).pack(side="left")
        descricao_status, cor, fundo = self.STATUS.get(
            str(registro.get("status", "")).upper(),
            (str(registro.get("status") or "Não informado"), COLORS["muted"], COLORS["soft_gray"])
        )
        ctk.CTkLabel(linha, text=descricao_status, fg_color=fundo,
                     text_color=cor, corner_radius=12,
                     font=("Roboto", 12, "bold"), height=30,
                     padx=14).pack(side="right")

        rolagem = ctk.CTkScrollableFrame(self, fg_color="transparent")
        rolagem.pack(fill="both", expand=True, padx=22, pady=(20, 10))

        dados = ctk.CTkFrame(rolagem, fg_color=COLORS["white"], corner_radius=12,
                             border_width=1, border_color=COLORS["border"])
        dados.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(dados, text="Informações da ordem", font=("Poppins", 16, "bold"),
                     anchor="w", text_color=COLORS["text"]
                     ).pack(fill="x", padx=20, pady=(18, 12))

        grade = ctk.CTkFrame(dados, fg_color="transparent")
        grade.pack(fill="x", padx=20, pady=(0, 20))
        grade.grid_columnconfigure((0, 1), weight=1, uniform="coluna")
        data = registro.get("data_abertura")
        data_formatada = data.strftime("%d/%m/%Y") if hasattr(data, "strftime") else str(data or "—")
        campos = [
            ("Cliente", registro.get("cliente_nome")),
            ("Placa do veículo", registro.get("placa_veiculo")),
            ("Data de abertura", data_formatada),
            ("Número da OS", registro.get("numero")),
        ]
        for i, (rotulo, valor) in enumerate(campos):
            bloco = ctk.CTkFrame(grade, fg_color=COLORS["background"], corner_radius=8)
            bloco.grid(row=i // 2, column=i % 2, sticky="nsew", padx=5, pady=5)
            ctk.CTkLabel(bloco, text=rotulo, text_color=COLORS["muted"],
                         font=("Roboto", 12), anchor="w").pack(fill="x", padx=13, pady=(10, 2))
            ctk.CTkLabel(bloco, text=str(valor or "—"), text_color=COLORS["text"],
                         font=("Roboto", 14, "bold"), anchor="w", wraplength=265,
                         justify="left").pack(fill="x", padx=13, pady=(0, 12))

        servico = ctk.CTkFrame(rolagem, fg_color=COLORS["white"], corner_radius=12,
                               border_width=1, border_color=COLORS["border"])
        servico.pack(fill="x")
        ctk.CTkLabel(servico, text="Descrição do serviço", font=("Poppins", 16, "bold"),
                     anchor="w", text_color=COLORS["text"]
                     ).pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(servico, text=str(registro.get("descricao_servico") or "Não informada"),
                     anchor="w", justify="left", wraplength=645,
                     text_color=COLORS["text"], font=("Roboto", 14)
                     ).pack(fill="x", padx=20, pady=(0, 20))

        rodape = ctk.CTkFrame(self, fg_color=COLORS["white"], corner_radius=0)
        rodape.pack(fill="x")
        ctk.CTkButton(rodape, text="Fechar", command=self.destroy,
                      fg_color=COLORS["red"], hover_color=COLORS["dark_red"],
                      width=130, height=38, font=("Roboto", 13, "bold")
                      ).pack(side="right", padx=25, pady=16)
        self.bind("<Escape>", lambda _event: self.destroy())
        self.after(100, self._ativar_modal)

    def _ativar_modal(self):
        if self.winfo_exists():
            self.lift()
            self.focus_force()
            self.grab_set()
